# handlers/profile.py
from aiogram import Dispatcher
from aiogram.types import Message
from db import get_user_stats, get_top_players

def register(dp: Dispatcher):
    pass  # start handler invokes functions directly

async def send_profile(message: Message):
    user_id = message.from_user.id
    stats = await get_user_stats(user_id)
    if not stats:
        return await message.answer("Sizda hali o'yinlar yo'q.")
    total_time_min = int((stats.get('total_time', 0) // 60))
    txt = (
        f"@{message.from_user.username}\n"
        f"O'yinlar: {stats.get('total_games', 0)}\n"
        f"G'alaba: {stats.get('wins', 0)}\n"
        f"Yutqazgan: {stats.get('losses', 0)}\n"
        f"Durrang: {stats.get('draws', 0)}\n"
        f"Umumiy vaqt: {total_time_min} daqiqa"
    )
    await message.answer(txt)

async def send_top(message: Message):
    top = await get_top_players(10)
    if not top:
        return await message.answer("Top mavjud emas.")
    lines = ["🏆 Top o'yinchilar:"]
    for i, p in enumerate(top, start=1):
        uname = p.get('username') or str(p.get('id'))
        lines.append(f"{i}. @{uname} — {p.get('wins',0)} g'alaba")
    await message.answer('\n'.join(lines))
