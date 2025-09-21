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
    
    # Таблица партнерских купонов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS partner_coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        partner_name TEXT NOT NULL,
        coupon_name TEXT NOT NULL,
        description TEXT NOT NULL,
        xp_cost INTEGER NOT NULL,
        total_quantity INTEGER DEFAULT 100,
        remaining_quantity INTEGER DEFAULT 100,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Таблица покупок купонов пользователями
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        coupon_id INTEGER,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_used BOOLEAN DEFAULT 0,
        used_date TIMESTAMP NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        FOREIGN KEY (coupon_id) REFERENCES partner_coupons (id)
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

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С КУПОНАМИ =====

async def init_coupons_table():
    """Инициализация таблицы купонов"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Добавляем начальные данные купонов
        initial_coupons = [
            ('OZON', 'Подарочный сертификат 500₽', 'Подарочный сертификат на 500 рублей в OZON', 100, 50),
            ('OZON', 'Подарочный сертификат 1000₽', 'Подарочный сертификат на 1000 рублей в OZON', 200, 30),
            ('DNS', 'Скидка 15% на технику', 'Скидка 15% на любую технику в DNS', 150, 40),
            ('DNS', 'Скидка 25% на комплектующие', 'Скидка 25% на комплектующие ПК в DNS', 250, 20),
            ('ЛитРес', 'Книга в подарок', 'Выбор любой книги из каталога ЛитРес', 80, 100),
            ('ЛитРес', 'Подписка на 1 месяц', 'Подписка ЛитРес на 1 месяц', 120, 80),
            ('Кофейня', 'Кофе и десерт', 'Кофе и десерт в партнерской кофейне', 50, 200),
            ('Кофейня', 'Завтрак', 'Полноценный завтрак в кофейне', 100, 100),
            ('Яндекс.Маркет', 'Скидка 10% на заказ', 'Скидка 10% на любой заказ', 120, 60),
            ('Яндекс.Еда', 'Бесплатная доставка', 'Бесплатная доставка на 1 месяц', 90, 150)
        ]

        # Проверяем, нужно ли добавлять купоны
        cursor.execute("SELECT COUNT(*) FROM partner_coupons")
        count_result = cursor.fetchone()
        coupon_count = count_result[0] if count_result else 0
        
        if coupon_count == 0:
            print("🔄 Добавляем начальные купоны в базу данных...")
            for coupon in initial_coupons:
                cursor.execute('''
                INSERT INTO partner_coupons (partner_name, coupon_name, description, xp_cost, total_quantity, remaining_quantity)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (coupon[0], coupon[1], coupon[2], coupon[3], coupon[4], coupon[4]))
            print(f"✅ Добавлено {len(initial_coupons)} купонов!")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"❌ Ошибка инициализации таблицы купонов: {e}")

async def get_available_coupons():
    """Получить все доступные купоны"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
        SELECT id, partner_name, coupon_name, description, xp_cost, remaining_quantity 
        FROM partner_coupons 
        WHERE is_active = 1 AND remaining_quantity > 0
        ORDER BY partner_name, xp_cost
        ''')

        coupons = cursor.fetchall()
        conn.close()

        return [{
            'id': row[0],
            'partner': row[1],
            'name': row[2],
            'description': row[3],
            'xp_cost': row[4],
            'remaining': row[5]
        } for row in coupons]

    except Exception as e:
        print(f"Error getting available coupons: {e}")
        return []

async def purchase_coupon(user_id: int, coupon_id: int):
    """Покупка купона пользователем"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем информацию о купоне
        cursor.execute('''
        SELECT xp_cost, remaining_quantity FROM partner_coupons 
        WHERE id = ? AND is_active = 1 AND remaining_quantity > 0
        ''', (coupon_id,))

        coupon = cursor.fetchone()
        if not coupon:
            conn.close()
            return None, "Купон недоступен"

        xp_cost, remaining = coupon['xp_cost'], coupon['remaining_quantity']

        # Проверяем XP пользователя
        cursor.execute("SELECT xp FROM users WHERE user_id = ?", (user_id,))
        user_xp_result = cursor.fetchone()
        user_xp = user_xp_result['xp'] if user_xp_result else 0

        if user_xp < xp_cost:
            conn.close()
            return None, f"Недостаточно XP. Нужно: {xp_cost}, у вас: {user_xp}"

        # Списание XP
        cursor.execute("UPDATE users SET xp = xp - ? WHERE user_id = ?", (xp_cost, user_id))

        # Уменьшаем количество купонов
        cursor.execute('''
        UPDATE partner_coupons 
        SET remaining_quantity = remaining_quantity - 1 
        WHERE id = ?
        ''', (coupon_id,))

        # Добавляем запись о покупке
        cursor.execute('''
        INSERT INTO user_coupons (user_id, coupon_id) 
        VALUES (?, ?)
        ''', (user_id, coupon_id))

        conn.commit()
        conn.close()

        return {
            'xp_cost': xp_cost,
            'remaining_xp': user_xp - xp_cost
        }, None

    except Exception as e:
        print(f"Error purchasing coupon: {e}")
        return None, "Ошибка при покупке"

async def get_user_coupons(user_id: int):
    """Получить купоны пользователя"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
        SELECT uc.id, p.partner_name, p.coupon_name, p.description, 
               uc.purchase_date, uc.is_used, uc.used_date
        FROM user_coupons uc
        JOIN partner_coupons p ON uc.coupon_id = p.id
        WHERE uc.user_id = ?
        ORDER BY uc.purchase_date DESC
        ''', (user_id,))

        coupons = cursor.fetchall()
        conn.close()

        return [{
            'id': row[0],
            'partner': row[1],
            'name': row[2],
            'description': row[3],
            'purchase_date': row[4],
            'is_used': bool(row[5]),
            'used_date': row[6]
        } for row in coupons]

    except Exception as e:
        print(f"Error getting user coupons: {e}")
        return []

async def get_all_coupons():
    """Получить все купоны"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, partner_name, coupon_name, description, xp_cost, 
               remaining_quantity, total_quantity, is_active
        FROM partner_coupons 
        ORDER BY partner_name, coupon_name
    ''')
    coupons = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return coupons

async def get_coupon(coupon_id: int):
    """Получить купон по ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM partner_coupons WHERE id = ?', (coupon_id,))
    coupon = cursor.fetchone()
    conn.close()
    return dict(coupon) if coupon else None

async def update_coupon_quantity(coupon_id: int, new_quantity: int):
    """Обновить количество оставшихся купонов"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE partner_coupons SET remaining_quantity = ? WHERE id = ?',
                   (new_quantity, coupon_id))
    conn.commit()
    conn.close()
    return True

async def increase_coupon_quantity(coupon_id: int, amount: int = 1):
    """Увеличить количество доступных купонов (только remaining_quantity)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверяем существование купона
    cursor.execute('SELECT total_quantity FROM partner_coupons WHERE id = ?', (coupon_id,))
    coupon = cursor.fetchone()

    if not coupon:
        conn.close()
        return None

    # Увеличиваем только remaining_quantity
    cursor.execute('''
        UPDATE partner_coupons 
        SET remaining_quantity = remaining_quantity + ?
        WHERE id = ?
    ''', (amount, coupon_id))
    conn.commit()

    # Получаем обновленное количество
    cursor.execute('SELECT remaining_quantity, total_quantity FROM partner_coupons WHERE id = ?', (coupon_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

async def decrease_coupon_quantity(coupon_id: int, amount: int = 1):
    """Уменьшить количество доступных купонов (только remaining_quantity)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Проверяем, достаточно ли купонов
    cursor.execute('SELECT remaining_quantity, total_quantity FROM partner_coupons WHERE id = ?', (coupon_id,))
    current = cursor.fetchone()

    if not current or current['remaining_quantity'] < amount:
        conn.close()
        return None

    # Уменьшаем только remaining_quantity
    cursor.execute('''
        UPDATE partner_coupons 
        SET remaining_quantity = remaining_quantity - ?
        WHERE id = ?
    ''', (amount, coupon_id))
    conn.commit()

    # Получаем обновленное количество
    cursor.execute('SELECT remaining_quantity, total_quantity FROM partner_coupons WHERE id = ?', (coupon_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

async def set_coupon_quantity(coupon_id: int, new_quantity: int):
    """Установить точное количество available купонов (не превышая total_quantity)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем максимальное возможное количество
    cursor.execute('SELECT total_quantity FROM partner_coupons WHERE id = ?', (coupon_id,))
    total = cursor.fetchone()

    if not total:
        conn.close()
        return None

    # Не позволяем установить больше чем total_quantity
    final_quantity = min(new_quantity, total['total_quantity'])

    cursor.execute('UPDATE partner_coupons SET remaining_quantity = ? WHERE id = ?',
                   (final_quantity, coupon_id))
    conn.commit()

    # Получаем обновленное количество
    cursor.execute('SELECT remaining_quantity, total_quantity FROM partner_coupons WHERE id = ?', (coupon_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

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
