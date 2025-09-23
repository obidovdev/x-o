from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery
from db import (
    get_game,
    update_game_move,
    finish_game,
    update_stats_after_game,
    get_user_stats,
)
from keyboards import board_markup, disabled_board_markup, render_board_text


def register(dp: Dispatcher):
    dp.callback_query.register(on_move, F.data.startswith("game_move:"))
    dp.callback_query.register(ignore_move, F.data == "ignore")


# ==================== HELPERS ====================

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


def check_winner(board: str) -> str:
    for a, b, c in WIN_LINES:
        if board[a] != "-" and board[a] == board[b] == board[c]:
            return board[a]  # "X" yoki "O"
    if "-" not in board:
        return "draw"
    return ""


async def safe_edit(bot, chat_id: int, message_id: int, text: str, reply_markup):
    """Xabarni xavfsiz tarzda tahrirlash"""
    try:
        await bot.edit_message_text(
            text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup
        )
    except Exception:
        pass


async def get_username(uid: int) -> str:
    user = await get_user_stats(uid)
    return f"@{user['username']}" if user and user.get("username") else str(uid)


# ==================== CALLBACK HANDLERS ====================

async def on_move(callback: CallbackQuery):
    """O‘yinchi yurish qilganda ishlaydi"""
    try:
        _, game_id, cell = callback.data.split(":")
        game_id, cell = int(game_id), int(cell)
    except ValueError:
        return await callback.answer()

    game = await get_game(game_id)
    if not game:
        return await callback.answer("O'yin topilmadi.")

    user_id = callback.from_user.id
    board, turn = game["board"], game["turn"]

    if user_id != turn:
        return await callback.answer("Hozir navbat sizda emas.", show_alert=True)

    symbol = "X" if user_id == game["player_x"] else "O"
    if board[cell] != "-":
        return await callback.answer("Bu katak band.")

    # update board
    board_list = list(board)
    board_list[cell] = symbol
    new_board = "".join(board_list)

    next_turn = game["player_o"] if user_id == game["player_x"] else game["player_x"]
    await update_game_move(game_id, new_board, next_turn)

    ux_name = await get_username(game["player_x"])
    uo_name = await get_username(game["player_o"])

    winner = check_winner(new_board)
    bot = callback.bot

    if winner:
        # yakunlash
        res = "draw" if winner == "draw" else winner
        res_info = await finish_game(game_id, res)
        if res_info:
            px, po, duration = res_info
            await update_stats_after_game(
                None if res == "draw" else winner, px, po, duration
            )

        if res == "draw":
            text_final = f"O'yin tugadi — Durrang.\n\n{render_board_text(new_board)}"
        else:
            win_name = ux_name if winner == "X" else uo_name
            text_final = f"O'yin tugadi — G'olib: {win_name}\n\n{render_board_text(new_board)}"

        kb = disabled_board_markup(new_board)
        await _broadcast_update(bot, game, text_final, kb)
        return await callback.answer("O'yin tugadi.")

    # ongoing
    next_name = ux_name if next_turn == game["player_x"] else uo_name
    text_update = (
        f"O'yin davom etmoqda.\nNavbat: {next_name}\n\n{render_board_text(new_board)}"
    )
    kb = board_markup(game_id, new_board)

    await _broadcast_update(bot, game, text_update, kb)
    await callback.answer()


async def _broadcast_update(bot, game: dict, text: str, kb):
    """Xabarlarni ikkala o‘yinchiga va callback messagega yangilash"""
    msg_x_id, msg_o_id = game.get("message_x_id"), game.get("message_o_id")
    px, po = game["player_x"], game["player_o"]

    if msg_x_id:
        await safe_edit(bot, px, msg_x_id, text, kb)
    if msg_o_id:
        await safe_edit(bot, po, msg_o_id, text, kb)

    try:
        await bot.edit_message_text(text, chat_id=px, message_id=msg_x_id, reply_markup=kb)
    except Exception:
        pass


async def ignore_move(callback: CallbackQuery):
    await callback.answer("⛔ O'yin tugagan. Endi yurish mumkin emas.", show_alert=True)
