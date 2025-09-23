# db.py (yangilangan — message_id saqlash qo'shildi)
import sqlite3
import time
import asyncio
from typing import Optional, Tuple, List

DB_PATH = 'xo_game.db'

def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _init_db_sync():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        draws INTEGER DEFAULT 0,
        total_games INTEGER DEFAULT 0,
        total_time REAL DEFAULT 0
    )
    """)

    # games jadvaliga message_x_id va message_o_id qo'shildi
    cur.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_x INTEGER,
        player_o INTEGER,
        board TEXT DEFAULT '---------',
        turn INTEGER,
        start_time REAL,
        end_time REAL,
        result TEXT,
        message_x_id INTEGER,
        message_o_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS waiting (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        requested_at REAL
    )
    """)

    conn.commit()
    conn.close()

async def init_db():
    await asyncio.to_thread(_init_db_sync)

# --- users helpers
def _add_user_sync(user_id: int, username: Optional[str]):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (user_id, username))
    # update username if changed or null
    cur.execute("UPDATE users SET username = COALESCE(?, username) WHERE id = ?", (username, user_id))
    conn.commit()
    conn.close()

async def add_user(user_id: int, username: Optional[str]):
    await asyncio.to_thread(_add_user_sync, user_id, username)

async def get_user_stats(user_id: int) -> Optional[dict]:
    def f():
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    return await asyncio.to_thread(f)

async def update_stats_after_game(winner: Optional[str], player_x: int, player_o: int, duration: float):
    def f():
        conn = _get_conn()
        cur = conn.cursor()
        # ensure both users exist
        cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (player_x, None))
        cur.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)", (player_o, None))

        # total games++ and total_time add
        cur.execute("UPDATE users SET total_games = total_games + 1, total_time = total_time + ? WHERE id = ?", (duration, player_x))
        cur.execute("UPDATE users SET total_games = total_games + 1, total_time = total_time + ? WHERE id = ?", (duration, player_o))

        if winner == 'X':
            cur.execute("UPDATE users SET wins = wins + 1 WHERE id = ?", (player_x,))
            cur.execute("UPDATE users SET losses = losses + 1 WHERE id = ?", (player_o,))
        elif winner == 'O':
            cur.execute("UPDATE users SET wins = wins + 1 WHERE id = ?", (player_o,))
            cur.execute("UPDATE users SET losses = losses + 1 WHERE id = ?", (player_x,))
        else:
            cur.execute("UPDATE users SET draws = draws + 1 WHERE id IN (?, ?)", (player_x, player_o))

        conn.commit()
        conn.close()
    await asyncio.to_thread(f)

# --- waiting helpers
def _add_waiting_sync(user_id: int, username: Optional[str]):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO waiting (user_id, username, requested_at) VALUES (?, ?, ?)", (user_id, username, time.time()))
    conn.commit()
    conn.close()

async def add_waiting(user_id: int, username: Optional[str]):
    await asyncio.to_thread(_add_waiting_sync, user_id, username)

async def pop_waiting(exclude_user_id: int) -> Optional[Tuple[int, Optional[str]]]:
    def f():
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id, username FROM waiting WHERE user_id != ? ORDER BY requested_at LIMIT 1", (exclude_user_id,))
        row = cur.fetchone()
        if row:
            user_id, username = row[0], row[1]
            cur.execute("DELETE FROM waiting WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return (user_id, username)
        conn.close()
        return None
    return await asyncio.to_thread(f)

async def remove_waiting(user_id: int):
    def f():
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM waiting WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    await asyncio.to_thread(f)

# --- games helpers
def _create_game_sync(player_x: int, player_o: int) -> int:
    conn = _get_conn()
    cur = conn.cursor()
    start = time.time()
    cur.execute("INSERT INTO games (player_x, player_o, board, turn, start_time) VALUES (?, ?, ?, ?, ?)",
                (player_x, player_o, '---------', player_x, start))
    game_id = cur.lastrowid
    conn.commit()
    conn.close()
    return game_id

async def create_game(player_x: int, player_o: int) -> int:
    return await asyncio.to_thread(_create_game_sync, player_x, player_o)

async def update_game_messages(game_id: int, message_x_id: Optional[int], message_o_id: Optional[int]):
    def f():
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE games SET message_x_id = ?, message_o_id = ? WHERE id = ?", (message_x_id, message_o_id, game_id))
        conn.commit()
        conn.close()
    return await asyncio.to_thread(f)

async def get_game(game_id: int) -> Optional[dict]:
    def f():
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM games WHERE id = ?", (game_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    return await asyncio.to_thread(f)

async def update_game_move(game_id: int, board: str, turn: int):
    def f():
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE games SET board = ?, turn = ? WHERE id = ?", (board, turn, game_id))
        conn.commit()
        conn.close()
    await asyncio.to_thread(f)

async def finish_game(game_id: int, result: str):
    def f():
        conn = _get_conn()
        cur = conn.cursor()
        end = time.time()
        cur.execute("UPDATE games SET result = ?, end_time = ? WHERE id = ?", (result, end, game_id))
        cur.execute("SELECT player_x, player_o, start_time FROM games WHERE id = ?", (game_id,))
        row = cur.fetchone()
        if row:
            player_x, player_o, start_time = row[0], row[1], row[2]
            duration = (end - start_time) if start_time else 0
            conn.commit()
            conn.close()
            return (player_x, player_o, duration)
        conn.commit()
        conn.close()
        return None
    return await asyncio.to_thread(f)

# top players
async def get_top_players(limit: int = 10) -> List[dict]:
    def f():
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, username, wins, total_games FROM users ORDER BY wins DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    return await asyncio.to_thread(f)
