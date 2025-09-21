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
    
    # Таблица для вакансий (HR)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hr_vacancies (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        status TEXT DEFAULT 'open',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
    
    # Проверяем, есть ли уже такой язык у пользователя
    cursor.execute('SELECT 1 FROM user_languages WHERE user_id = ? AND language = ?', 
                  (user_id, language))
    if cursor.fetchone():
        conn.close()
        return False  # Язык уже существует
    
    cursor.execute('INSERT INTO user_languages (user_id, language, level) VALUES (?, ?, ?)', 
                  (user_id, language, level))
    conn.commit()
    conn.close()
    return True

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
    
    # Проверяем, есть ли уже такой язык у пользователя
    cursor.execute('SELECT 1 FROM user_programming WHERE user_id = ? AND language = ?', 
                  (user_id, language))
    if cursor.fetchone():
        conn.close()
        return False  # Язык уже существует
    
    cursor.execute('INSERT INTO user_programming (user_id, language, level) VALUES (?, ?, ?)', 
                  (user_id, language, level))
    conn.commit()
    conn.close()
    return True

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
    
    # Проверяем, есть ли уже такой навык у пользователя
    cursor.execute('SELECT 1 FROM user_skills WHERE user_id = ? AND skill = ?', 
                  (user_id, skill))
    if cursor.fetchone():
        conn.close()
        return False  # Навык уже существует
    
    cursor.execute('INSERT INTO user_skills (user_id, skill, level) VALUES (?, ?, ?)', 
                  (user_id, skill, level))
    conn.commit()
    conn.close()
    return True

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

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ВАКАНСИЯМИ (HR) =====

async def add_vacancy(title: str, description: str, required_skills: str, created_by: int):
    """Добавить вакансию с указанием требуемых навыков"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO hr_vacancies (title, description, required_skills, created_by, status) VALUES (?, ?, ?, ?, ?)',
        (title, description, required_skills, created_by, 'open')
    )
    conn.commit()
    vacancy_id = cursor.lastrowid
    conn.close()
    return vacancy_id

async def get_vacancy(vacancy_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM hr_vacancies WHERE id = ?', (vacancy_id,))
    vacancy = cursor.fetchone()
    conn.close()
    return dict(vacancy) if vacancy else None

async def get_active_vacancies():
    """Получить все активные вакансии"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM hr_vacancies WHERE status = "open" ORDER BY created_at DESC')
    vacancies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return vacancies

async def get_vacancy(vacancy_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM hr_vacancies WHERE id = ?', (vacancy_id,))
    vacancy = cursor.fetchone()
    conn.close()
    return dict(vacancy) if vacancy else None

async def close_vacancy(vacancy_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE hr_vacancies SET status = "closed" WHERE id = ?', (vacancy_id,))
    conn.commit()
    conn.close()

# ===== ФУНКЦИИ ПОИСКА СОТРУДНИКОВ =====

async def search_employees_by_skills(skills: list):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if not skills:
        return []
    
    placeholders = ','.join('?' * len(skills))
    query = f'''
    SELECT DISTINCT u.user_id, u.name, u.career_goal, u.xp,
           GROUP_CONCAT(DISTINCT ul.language) as languages,
           GROUP_CONCAT(DISTINCT up.language) as programming,
           GROUP_CONCAT(DISTINCT us.skill) as other_skills
    FROM users u
    LEFT JOIN user_languages ul ON u.user_id = ul.user_id
    LEFT JOIN user_programming up ON u.user_id = up.user_id
    LEFT JOIN user_skills us ON u.user_id = us.user_id
    WHERE ul.language IN ({placeholders}) 
       OR up.language IN ({placeholders})
       OR us.skill IN ({placeholders})
    GROUP BY u.user_id
    LIMIT 10
    '''
    
    cursor.execute(query, skills * 3)
    employees = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return employees

async def search_employees_for_vacancy(vacancy_id: int):
    """Поиск сотрудников подходящих для конкретной вакансии"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем вакансию
    vacancy = await get_vacancy(vacancy_id)
    if not vacancy:
        return []
    
    # Анализируем описание вакансии чтобы выявить ключевые навыки
    description = vacancy['description'].lower()
    skills_to_search = []
    
    # Простой анализ текста для выявления навыков
    programming_keywords = ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'sql', 'html', 'css', 'react', 'vue', 'angular', 'node', 'django', 'flask']
    language_keywords = ['английский', 'english', 'немецкий', 'german', 'французский', 'french', 'китайский', 'chinese']
    skill_keywords = ['управление', 'management', 'лидерство', 'leadership', 'коммуникация', 'communication', 'аналитика', 'analysis']
    
    for keyword in programming_keywords + language_keywords + skill_keywords:
        if keyword in description:
            skills_to_search.append(keyword)
    
    if not skills_to_search:
        return []
    
    # Ищем сотрудников с этими навыками
    placeholders = ','.join('?' * len(skills_to_search))
    query = f'''
    SELECT DISTINCT u.user_id, u.name, u.xp, u.career_goal,
           (SELECT COUNT(*) FROM user_languages WHERE user_id = u.user_id AND language IN ({placeholders})) as lang_match,
           (SELECT COUNT(*) FROM user_programming WHERE user_id = u.user_id AND language IN ({placeholders})) as prog_match,
           (SELECT COUNT(*) FROM user_skills WHERE user_id = u.user_id AND skill IN ({placeholders})) as skill_match
    FROM users u
    WHERE u.name IS NOT NULL
    HAVING (lang_match + prog_match + skill_match) > 0
    ORDER BY (lang_match + prog_match + skill_match) DESC
    LIMIT 10
    '''
    
    cursor.execute(query, skills_to_search * 3)
    employees = [dict(row) for row in cursor.fetchall()]
    
    # Добавляем информацию о проценте совпадения
    for emp in employees:
        total_matches = emp['lang_match'] + emp['prog_match'] + emp['skill_match']
        emp['match_percentage'] = min(100, total_matches * 20)  # Простая формула
    
    conn.close()
    return employees

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

async def get_all_users():
    """Получить всех пользователей (для админки)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, name, xp FROM users ORDER BY xp DESC')
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

async def get_users_count():
    """Получить количество всех пользователей"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM users')
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0

async def get_users_with_names_count():
    """Получить количество пользователей с заполненными именами"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE name IS NOT NULL')
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0

async def get_active_users_count():
    """Получить количество активных пользователей (с XP > 0)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE xp > 0 AND name IS NOT NULL')
    result = cursor.fetchone()
    conn.close()
    return result['count'] if result else 0

async def get_total_skills_count():
    """Получить общее количество навыков"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM user_languages')
    lang_count = cursor.fetchone()['count'] or 0
    
    cursor.execute('SELECT COUNT(*) as count FROM user_programming')
    prog_count = cursor.fetchone()['count'] or 0
    
    cursor.execute('SELECT COUNT(*) as count FROM user_skills')
    skills_count = cursor.fetchone()['count'] or 0
    
    conn.close()
    return lang_count + prog_count + skills_count

async def debug_get_all_users():
    """Отладочная функция - получить всех пользователей"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def migrate_db():
    """Миграция базы данных - добавляем колонку required_skills если её нет"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем есть ли колонка required_skills
        cursor.execute("PRAGMA table_info(hr_vacancies)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'required_skills' not in columns:
            print("🔄 Добавляем колонку required_skills в таблицу hr_vacancies...")
            cursor.execute('ALTER TABLE hr_vacancies ADD COLUMN required_skills TEXT DEFAULT ""')
            conn.commit()
            print("✅ Колонка required_skills добавлена!")
        else:
            print("✅ Колонка required_skills уже существует")
            
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
    finally:
        conn.close()

# Вызываем миграцию при импорте
migrate_db()