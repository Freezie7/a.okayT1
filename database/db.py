import sqlite3
import os

# Убедимся, что папка database существует
os.makedirs('database', exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('database/users.db')
    conn.row_factory = sqlite3.Row  # Чтобы получать результаты в виде словаря
    return conn

def init_db():
    """Инициализация базы данных: создаем таблицы"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL,
        name TEXT,
        about TEXT,
        education_level TEXT,
        education_place TEXT,
        career_goal TEXT,
        xp INTEGER DEFAULT 0
    )
    ''')
    
    # Таблица бейджей пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_badges (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        badge_key TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    # Таблица для иностранных языков
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_languages (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        language TEXT NOT NULL,
        level TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    # Таблица для языков программирования
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_programming (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        language TEXT NOT NULL,
        level TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    # Таблица для других навыков
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_skills (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        skill TEXT NOT NULL,
        level TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Вызываем инициализацию при импорте
init_db()

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ =====

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

async def get_user_xp(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT xp FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result['xp'] if result else 0

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С БЕЙДЖАМИ =====

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

async def check_user_has_badge(user_id: int, badge_key: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM user_badges WHERE user_id = ? AND badge_key = ?', (user_id, badge_key))
    result = cursor.fetchone()
    conn.close()
    return result is not None

async def get_user_badges(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT badge_key FROM user_badges WHERE user_id = ?', (user_id,))
    badges = [row['badge_key'] for row in cursor.fetchall()]
    conn.close()
    return badges

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ИНОСТРАННЫМИ ЯЗЫКАМИ =====

async def add_user_language(user_id: int, language: str, level: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_languages (user_id, language, level) VALUES (?, ?, ?)', 
                  (user_id, language, level))
    conn.commit()
    conn.close()

async def get_user_languages(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT language, level FROM user_languages WHERE user_id = ?', (user_id,))
    languages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return languages

async def delete_user_language(user_id: int, language: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_languages WHERE user_id = ? AND language = ?', (user_id, language))
    conn.commit()
    conn.close()

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ЯЗЫКАМИ ПРОГРАММИРОВАНИЯ =====

async def add_user_programming(user_id: int, language: str, level: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_programming (user_id, language, level) VALUES (?, ?, ?)', 
                  (user_id, language, level))
    conn.commit()
    conn.close()

async def get_user_programming(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT language, level FROM user_programming WHERE user_id = ?', (user_id,))
    programming = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return programming

async def delete_user_programming(user_id: int, language: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_programming WHERE user_id = ? AND language = ?', (user_id, language))
    conn.commit()
    conn.close()

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ДРУГИМИ НАВЫКАМИ =====

async def add_user_skill(user_id: int, skill: str, level: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_skills (user_id, skill, level) VALUES (?, ?, ?)', 
                  (user_id, skill, level))
    conn.commit()
    conn.close()

async def get_user_skills(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT skill, level FROM user_skills WHERE user_id = ?', (user_id,))
    skills = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return skills

async def delete_user_skill(user_id: int, skill: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_skills WHERE user_id = ? AND skill = ?', (user_id, skill))
    conn.commit()
    conn.close()

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

async def get_all_users():
    """Получить всех пользователей (для админки)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, name, xp FROM users ORDER BY xp DESC')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

async def search_users_by_skill(skill: str):
    """Поиск пользователей по навыку (для HR)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ищем в языках, программировании и навыках
    query = '''
    SELECT u.user_id, u.name, u.xp 
    FROM users u
    LEFT JOIN user_languages ul ON u.user_id = ul.user_id
    LEFT JOIN user_programming up ON u.user_id = up.user_id  
    LEFT JOIN user_skills us ON u.user_id = us.user_id
    WHERE ul.language LIKE ? OR up.language LIKE ? OR us.skill LIKE ?
    GROUP BY u.user_id
    '''
    
    search_pattern = f'%{skill}%'
    cursor.execute(query, (search_pattern, search_pattern, search_pattern))
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

async def get_user_stats(user_id: int):
    """Получить статистику пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем основные данные
    cursor.execute('SELECT name, xp FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    
    # Считаем количество навыков
    cursor.execute('SELECT COUNT(*) as count FROM user_languages WHERE user_id = ?', (user_id,))
    languages_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM user_programming WHERE user_id = ?', (user_id,))
    programming_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM user_skills WHERE user_id = ?', (user_id,))
    skills_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM user_badges WHERE user_id = ?', (user_id,))
    badges_count = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'name': user_data['name'] if user_data else None,
        'xp': user_data['xp'] if user_data else 0,
        'languages_count': languages_count,
        'programming_count': programming_count,
        'skills_count': skills_count,
        'badges_count': badges_count,
        'total_skills': languages_count + programming_count + skills_count
    }