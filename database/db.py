import sqlite3
import os

# Убедимся, что папка database существует
os.makedirs('database', exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('database/users.db')
    conn.row_factory = sqlite3.Row  # Чтобы получать результаты в виде словаря
    return conn

def init_db():
    """Инициализация базы данных: создаем таблицу пользователей"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL,
        name TEXT,
        about TEXT,
        xp INTEGER DEFAULT 0
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_badges (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        badge_key TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Вызываем инициализацию при импорте
init_db()

async def get_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

async def create_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Пользователь уже существует
        pass
    finally:
        conn.close()

async def update_user_profile(user_id: int, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
    values = list(kwargs.values())
    values.append(user_id)
    cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', values)
    conn.commit()
    conn.close()

async def add_xp_to_user(user_id: int, xp: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET xp = xp + ? WHERE user_id = ?', (xp, user_id))
    conn.commit()
    conn.close()

async def add_badge_to_user(user_id: int, badge_key: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO user_badges (user_id, badge_key) VALUES (?, ?)', (user_id, badge_key))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Бейдж уже есть у пользователя
        return False
    finally:
        conn.close()