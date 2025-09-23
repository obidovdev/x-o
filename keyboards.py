from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def reply_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎲 Tasodifiy raqib")],
            [KeyboardButton(text="📊 Profilim"), KeyboardButton(text="🏆 Top o‘yinchilar")],
            [KeyboardButton(text="❌ O‘yin tugatish")],
        ],
        resize_keyboard=True,
    )
    return kb


def render_board_text(board: str) -> str:
    symbols = {"-": "⬜", "X": "❌", "O": "⭕"}
    lines = []
    for i in range(0, 9, 3):
        lines.append(" ".join(symbols.get(c, "⬜") for c in board[i : i + 3]))
    return "\n".join(lines)


def board_markup(game_id: int, board: str):
    buttons = []
    for idx, c in enumerate(board):
        text = "❌" if c == "X" else "⭕" if c == "O" else "⬜"
        buttons.append(
            InlineKeyboardButton(text=text, callback_data=f"game_move:{game_id}:{idx}")
        )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i : i + 3] for i in range(0, 9, 3)]
    )
    return kb


def disabled_board_markup(board: str):
    """
    Faqat ko‘rsatish uchun tugmalar (o‘yin tugagandan keyin).
    Bosilganda callback "ignore" bo‘ladi.
    """
    buttons = []
    for c in board:
        text = "❌" if c == "X" else "⭕" if c == "O" else "⬜"
        buttons.append(InlineKeyboardButton(text=text, callback_data="ignore"))
    kb = InlineKeyboardMarkup(
        inline_keyboard=[buttons[i : i + 3] for i in range(0, 9, 3)]
    )
    return kb
