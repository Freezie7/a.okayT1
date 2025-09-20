import sys
import os
import sqlite3

# Добавляем родительскую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Указываем правильный путь к общей базе данных
DB_PATH = os.path.join(parent_dir, 'database', 'users.db')

def get_db_connection():
    """Подключаемся к общей базе данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Создаем функции-обертки для работы с базой
class DBWrapper:
    def __init__(self):
        self.connection = None
    
    async def get_all_users(self):
        """Получить всех пользователей с заполненными именами"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, name, xp FROM users WHERE name IS NOT NULL ORDER BY xp DESC')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    
    async def get_users_count(self):
        """Получить количество всех пользователей"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users')
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0
    
    async def get_users_with_names_count(self):
        """Получить количество пользователей с заполненными именами"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE name IS NOT NULL')
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0
    
    async def get_active_users_count(self):
        """Получить количество активных пользователей"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE xp > 0 AND name IS NOT NULL')
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0
    
    async def get_total_skills_count(self):
        """Получить общее количество навыков"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM user_languages')
        lang_count_result = cursor.fetchone()
        lang_count = lang_count_result['count'] if lang_count_result and lang_count_result['count'] is not None else 0
        
        cursor.execute('SELECT COUNT(*) as count FROM user_programming')
        prog_count_result = cursor.fetchone()
        prog_count = prog_count_result['count'] if prog_count_result and prog_count_result['count'] is not None else 0
        
        cursor.execute('SELECT COUNT(*) as count FROM user_skills')
        skills_count_result = cursor.fetchone()
        skills_count = skills_count_result['count'] if skills_count_result and skills_count_result['count'] is not None else 0
        
        conn.close()
        return lang_count + prog_count + skills_count
    
    async def get_vacancies(self):
        """Получить все вакансии"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hr_vacancies WHERE status = "open" ORDER BY created_at DESC')
        vacancies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return vacancies

    async def get_vacancy(self, vacancy_id: int):
        """Получить вакансию по ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hr_vacancies WHERE id = ?', (vacancy_id,))
        vacancy = cursor.fetchone()
        conn.close()
        return dict(vacancy) if vacancy else None
    
    async def add_vacancy(self, title: str, description: str, required_skills: str, created_by: int):
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

    async def close_vacancy(self, vacancy_id: int):
        """Закрыть вакансию"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE hr_vacancies SET status = "closed" WHERE id = ?', (vacancy_id,))
        conn.commit()
        conn.close()
    
    async def search_employees_by_skills_simple(self, skills):
        """Простой поиск сотрудников по навыкам"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if not skills:
            return None
        
        response = "🔍 Результаты поиска:\n\n"
        found_any = False
        
        for skill in skills:
            query = '''
            SELECT u.user_id, u.name, u.xp 
            FROM users u
            WHERE u.name IS NOT NULL AND (
                EXISTS (SELECT 1 FROM user_languages WHERE user_id = u.user_id AND language LIKE ?) OR
                EXISTS (SELECT 1 FROM user_programming WHERE user_id = u.user_id AND language LIKE ?) OR
                EXISTS (SELECT 1 FROM user_skills WHERE user_id = u.user_id AND skill LIKE ?)
            )
            LIMIT 5
            '''
            
            search_term = f"%{skill}%"
            cursor.execute(query, (search_term, search_term, search_term))
            employees = cursor.fetchall()
            
            if employees:
                found_any = True
                response += f"Навык: {skill}\n"
                for emp in employees:
                    response += f"• {emp['name']} ({emp['xp']} XP)\n"
                response += "\n"
        
        conn.close()
        
        if not found_any:
            return None
        
        return response


    async def search_employees_by_skills_simple2(self, skills):
        """Простой поиск сотрудников по навыкам. Возвращает список user_id."""
        conn = get_db_connection()
        cursor = conn.cursor()

        if not skills:
            return []  # Возвращаем пустой список, если навыков нет

        user_ids = [] # Список для хранения user_id

        for skill in skills:
            query = '''
            SELECT u.user_id, u.name, u.xp
            FROM users u
            WHERE u.name IS NOT NULL AND (
                EXISTS (SELECT 1 FROM user_languages WHERE user_id = u.user_id AND language LIKE ?) OR
                EXISTS (SELECT 1 FROM user_programming WHERE user_id = u.user_id AND language LIKE ?) OR
                EXISTS (SELECT 1 FROM user_skills WHERE user_id = u.user_id AND skill LIKE ?)
            )
            LIMIT 5
            '''

            search_term = f"%{skill}%"
            cursor.execute(query, (search_term, search_term, search_term))
            employees = cursor.fetchall()

            if employees:
                for emp in employees:
                    user_ids.append(emp[0])  # Добавляем user_id в список

        if not user_ids:
            return []  # Возвращаем пустой список, если ничего не найдено

        return user_ids # Возвращаем список user_id

    async def search_employees_by_skills_detailed(self, skills: list):
        """Детальный поиск сотрудников по навыкам"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if not skills:
            return None
        
        placeholders = ','.join('?' * len(skills))
        
        query = f'''
        SELECT u.user_id, u.name, u.xp, u.career_goal,
            (SELECT GROUP_CONCAT(language || ' (' || level || ')') 
                FROM user_languages WHERE user_id = u.user_id) as languages,
            (SELECT GROUP_CONCAT(language || ' (' || level || ')') 
                FROM user_programming WHERE user_id = u.user_id) as programming,
            (SELECT GROUP_CONCAT(skill || ' (' || level || ')') 
                FROM user_skills WHERE user_id = u.user_id) as skills
        FROM users u
        WHERE u.name IS NOT NULL AND (
            EXISTS (SELECT 1 FROM user_languages WHERE user_id = u.user_id AND language IN ({placeholders})) OR
            EXISTS (SELECT 1 FROM user_programming WHERE user_id = u.user_id AND language IN ({placeholders})) OR
            EXISTS (SELECT 1 FROM user_skills WHERE user_id = u.user_id AND skill IN ({placeholders}))
        )
        ORDER BY u.xp DESC
        LIMIT 10
        '''
        
        cursor.execute(query, skills * 3)
        employees = []
        
        for row in cursor.fetchall():
            emp = dict(row)
            # Форматируем данные
            emp['languages'] = emp['languages'] or 'Нет'
            emp['programming'] = emp['programming'] or 'Нет'
            emp['skills'] = emp['skills'] or 'Нет'
            employees.append(emp)
        
        conn.close()
        return employees
    
    async def debug_get_all_users(self):
        """Отладочная функция - получить всех пользователей"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users

# Создаем экземпляр обертки
db = DBWrapper()

print(f"✅ HR-бот подключен к базе: {DB_PATH}")