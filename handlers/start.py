# handlers/start.py (yangilangan random_match qismi)
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import reply_kb
from db import add_user, add_waiting, pop_waiting, create_game, update_game_messages
from keyboards import board_markup
import random

def register(dp: Dispatcher):
    dp.message.register(start, CommandStart())
    dp.message.register(random_match, lambda message: message.text == '🎲 Tasodifiy raqib')
    dp.message.register(my_profile, lambda message: message.text == '📊 Profilim')
    dp.message.register(top_players, lambda message: message.text == '🏆 Top o‘yinchilar')
    dp.message.register(end_game_cmd, lambda message: message.text == '❌ O‘yin tugatish')

async def start(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer("X/O o'yiniga xush kelibsiz! O'ynashni boshlang 👇", reply_markup=reply_kb())

async def random_match(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    other = await pop_waiting(user_id)
    if other:
        other_id, other_username = other
        # decide who X and O randomly
        players = [user_id, other_id]
        random.shuffle(players)
        player_x, player_o = players[0], players[1]
        # create game row first
        game_id = await create_game(player_x, player_o)
        board = '---------'
        # create board markup
        kb = board_markup(game_id, board)

        # prepare text with usernames if available
        ux = username if player_x == user_id else (other_username or str(player_x))
        uo = username if player_o == user_id else (other_username or str(player_o))
        # but better to show ids for now; we'll refine with DB username later
        text_for_x = f"O'yin boshlandi!\nSiz: X\nRaqib: {other_username or other_id}\nNavbat: Siz"
        text_for_o = f"O'yin boshlandi!\nSiz: O\nRaqib: {message.from_user.username or user_id}\nNavbat: @{player_x}"

        # send to player_x and player_o and capture message ids
        from config import BOT_TOKEN
        from aiogram import Bot
        bot = Bot(token=BOT_TOKEN)
        try:
            msg_x = await bot.send_message(player_x, text_for_x, reply_markup=kb)
            msg_o = await bot.send_message(player_o, text_for_o, reply_markup=kb)
            # save message ids in DB so we can edit both messages later
            await update_game_messages(game_id, msg_x.message_id, msg_o.message_id)
        except Exception:
            # agar private chat block bo'lsa, biz game yaramaydi yoki faqatgina yolg'izga yuboriladi.
            # qayta urinib, har ikkala userga o'yin xabarini bot orqali jo'natamiz (best-effort)
            try:
                await message.answer(f"O'yin boshlandi: X={player_x}, O={player_o}", reply_markup=kb)
            except Exception:
                pass
        finally:
            await bot.session.close()
    else:
        await add_waiting(user_id, username)
        await message.answer("Siz kutish ro'yxatiga qo'shildingiz. Boshqa foydalanuvchi topilganda o'yin boshlanadi.")

async def my_profile(message: Message):
    from handlers.profile import send_profile
    await send_profile(message)

async def top_players(message: Message):
    from handlers.profile import send_top
    await send_top(message)

async def end_game_cmd(message: Message):
    await message.answer("O'yinni tugatish funksiyasi inline o'yin ichida qo'llaniladi. Agar ochiq o'yiningiz bo'lsa, inline tugmadan yoki /endgame ketma-ketligidan foydalaning.")
