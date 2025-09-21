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

    # ===== МЕТОДЫ ДЛЯ РАБОТЫ С КУПОНАМИ =====

    async def get_all_coupons(self):
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

    async def get_coupon(self, coupon_id: int):
        """Получить купон по ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM partner_coupons WHERE id = ?', (coupon_id,))
        coupon = cursor.fetchone()
        conn.close()
        return dict(coupon) if coupon else None

    async def update_coupon_quantity(self, coupon_id: int, new_quantity: int):
        """Обновить количество оставшихся купонов"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE partner_coupons SET remaining_quantity = ? WHERE id = ?',
                       (new_quantity, coupon_id))
        conn.commit()
        conn.close()
        return True

    async def increase_coupon_quantity(self, coupon_id: int, amount: int = 1):
        """Увеличить количество купонов"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE partner_coupons 
            SET remaining_quantity = remaining_quantity + ?, total_quantity = total_quantity + ?
            WHERE id = ?
        ''', (amount, amount, coupon_id))
        conn.commit()

        # Получаем обновленное количество
        cursor.execute('SELECT remaining_quantity, total_quantity FROM partner_coupons WHERE id = ?', (coupon_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    async def decrease_coupon_quantity(self, coupon_id: int, amount: int = 1):
        """Уменьшить количество купонов"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, достаточно ли купонов
        cursor.execute('SELECT remaining_quantity FROM partner_coupons WHERE id = ?', (coupon_id,))
        current = cursor.fetchone()

        if not current or current['remaining_quantity'] < amount:
            conn.close()
            return None

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

    async def get_coupon_stats(self):
        """Получить статистику по купонам"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                COUNT(*) as total_coupons,
                SUM(remaining_quantity) as total_remaining,
                SUM(total_quantity) as total_available,
                COUNT(CASE WHEN remaining_quantity = 0 THEN 1 END) as out_of_stock,
                COUNT(CASE WHEN remaining_quantity > 0 AND remaining_quantity <= 5 THEN 1 END) as low_stock,
                COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_coupons
            FROM partner_coupons
        ''')

        stats = cursor.fetchone()
        conn.close()
        return dict(stats) if stats else None

    async def get_popular_coupons(self, limit: int = 5):
        """Получить самые популярные купоны (по количеству покупок)"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT p.id, p.partner_name, p.coupon_name, p.remaining_quantity,
                   COUNT(uc.id) as purchases_count,
                   (p.total_quantity - p.remaining_quantity) as sold_count
            FROM partner_coupons p
            LEFT JOIN user_coupons uc ON p.id = uc.coupon_id
            GROUP BY p.id
            ORDER BY purchases_count DESC
            LIMIT ?
        ''', (limit,))

        coupons = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return coupons

    async def get_coupon_purchases(self, coupon_id: int):
        """Получить историю покупок купона"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT uc.id, u.name, u.user_id, uc.purchase_date, uc.is_used, uc.used_date
            FROM user_coupons uc
            JOIN users u ON uc.user_id = u.user_id
            WHERE uc.coupon_id = ?
            ORDER BY uc.purchase_date DESC
        ''', (coupon_id,))

        purchases = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return purchases

    async def set_coupon_active(self, coupon_id: int, is_active: bool):
        """Активировать/деактивировать купон"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE partner_coupons SET is_active = ? WHERE id = ?',
                       (is_active, coupon_id))
        conn.commit()
        conn.close()
        return True

    # ===== СУЩЕСТВУЮЩИЕ МЕТОДЫ (остаются без изменений) =====

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
        skills_count = skills_count_result['count'] if skills_count_result and skills_count_result[
            'count'] is not None else 0

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
        """Поиск сотрудников со ВСЕМИ указанными навыками"""
        conn = get_db_connection()
        cursor = conn.cursor()

        if not skills:
            return None

        # Создаем условия для поиска по каждому навыку
        conditions = []
        params = []

        for skill in skills:
            conditions.append('''
            (EXISTS (SELECT 1 FROM user_languages WHERE user_id = u.user_id AND language LIKE ?) OR
            EXISTS (SELECT 1 FROM user_programming WHERE user_id = u.user_id AND language LIKE ?) OR
            EXISTS (SELECT 1 FROM user_skills WHERE user_id = u.user_id AND skill LIKE ?))
            ''')
            search_term = f"%{skill}%"
            params.extend([search_term, search_term, search_term])

        # Основной запрос для поиска сотрудников со ВСЕМИ навыками
        query = f'''
        SELECT 
            u.user_id, 
            u.name, 
            u.xp,
            u.career_goal
        FROM users u
        WHERE u.name IS NOT NULL 
        AND {' AND '.join(conditions)}
        ORDER BY u.xp DESC
        LIMIT 10
        '''

        cursor.execute(query, params)
        employees = cursor.fetchall()

        conn.close()

        if not employees:
            # Если не найдено сотрудников со всеми навыками, ищем с группировкой по комбинациям
            return await self.search_grouped_partial_matches(skills)

        # Формируем ответ для полных совпадений
        response = f"✅ Найдены сотрудники со ВСЕМИ навыками: {', '.join(skills)}\n\n"
        
        for emp in employees:
            response += f"• {emp['name']} ({emp['xp']} XP)"
            response += "\n"

        return response

    async def search_grouped_partial_matches(self, skills):
        """Поиск сотрудников с группировкой по комбинациям навыков без дубликатов"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        response = f"⚠️ Сотрудников со ВСЕМИ навыками ({', '.join(skills)}) не найдено\n\n"
        response += "🔍 Частичные совпадения:\n\n"
        
        # Создаем все возможные комбинации навыков (от больших к меньшим)
        from itertools import combinations
        all_combinations = []
        
        # Генерируем комбинации от самых больших к самым маленьким
        for r in range(len(skills), 1, -1):  # Начинаем с 2+ навыков
            for combo in combinations(skills, r):
                all_combinations.append(combo)
        
        found_employees = set()  # Множество для отслеживания уже найденных сотрудников
        found_any = False
        
        # Ищем сотрудников для каждой комбинации навыков
        for combo in all_combinations:
            conditions = []
            params = []
            
            for skill in combo:
                conditions.append('''
                (EXISTS (SELECT 1 FROM user_languages WHERE user_id = u.user_id AND language LIKE ?) OR
                EXISTS (SELECT 1 FROM user_programming WHERE user_id = u.user_id AND language LIKE ?) OR
                EXISTS (SELECT 1 FROM user_skills WHERE user_id = u.user_id AND skill LIKE ?))
                ''')
                search_term = f"%{skill}%"
                params.extend([search_term, search_term, search_term])
            
            query = f'''
            SELECT 
                u.user_id, 
                u.name, 
                u.xp,
                u.career_goal
            FROM users u
            WHERE u.name IS NOT NULL 
            AND {' AND '.join(conditions)}
            ORDER BY u.xp DESC
            LIMIT 10
            '''
            
            cursor.execute(query, params)
            employees = cursor.fetchall()
            
            if employees:
                # Фильтруем сотрудников, которые еще не были найдены в более полных комбинациях
                new_employees = []
                for emp in employees:
                    emp_id = emp['user_id']
                    if emp_id not in found_employees:
                        new_employees.append(emp)
                        found_employees.add(emp_id)
                
                if new_employees:
                    found_any = True
                    response += f"📊 {', '.join(combo)}:\n"
                    for emp in new_employees:
                        response += f"• {emp['name']} ({emp['xp']} XP)"
                        response += "\n"
                    response += "\n"
        
        conn.close()

        if not found_any:
            # Если не найдено групповых совпадений, ищем одиночные навыки
            return await self.search_single_skills(skills)

        return response

    async def search_single_skills(self, skills):
        """Поиск по одиночным навыкам (если нет групповых совпадений)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        response = f"⚠️ Сотрудников со ВСЕМИ навыками ({', '.join(skills)}) не найдено\n\n"
        response += "🔍 Совпадения по отдельным навыкам:\n\n"
        
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
            ORDER BY u.xp DESC
            LIMIT 3
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

        user_ids = []  # Список для хранения user_id

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

        return user_ids  # Возвращаем список user_id

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

    # ===== МЕТОДЫ ДЛЯ РАБОТЫ С КУПОНАМИ =====

    async def set_coupon_quantity(self, coupon_id: int, new_quantity: int):
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

    async def increase_coupon_quantity(self, coupon_id: int, amount: int = 1):
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

    async def decrease_coupon_quantity(self, coupon_id: int, amount: int = 1):
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

    async def create_coupon(self, partner_name: str, coupon_name: str, description: str, xp_cost: int,
                            total_quantity: int = 100):
        """Создать новый купон"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Проверяем, не существует ли уже такой купон
            cursor.execute('''
                SELECT 1 FROM partner_coupons 
                WHERE partner_name = ? AND coupon_name = ?
            ''', (partner_name, coupon_name))

            if cursor.fetchone():
                conn.close()
                return None, "Купон с таким названием уже существует"

            # Проверяем валидность данных
            if xp_cost <= 0:
                conn.close()
                return None, "Стоимость XP должна быть положительной"

            if total_quantity <= 0:
                conn.close()
                return None, "Количество должно быть положительным"

            # Создаем новый купон
            cursor.execute('''
                INSERT INTO partner_coupons 
                (partner_name, coupon_name, description, xp_cost, total_quantity, remaining_quantity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (partner_name, coupon_name, description, xp_cost, total_quantity, total_quantity))

            conn.commit()
            coupon_id = cursor.lastrowid
            conn.close()

            return coupon_id, None

        except Exception as e:
            conn.close()
            return None, f"Ошибка при создании купона: {str(e)}"

    async def delete_coupon(self, coupon_id: int):
        """Удалить купон"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Проверяем, есть ли покупки этого купона
            cursor.execute('SELECT COUNT(*) as count FROM user_coupons WHERE coupon_id = ?', (coupon_id,))
            purchases_count = cursor.fetchone()['count']

            if purchases_count > 0:
                conn.close()
                return False, "Нельзя удалить купон, у которого есть покупки"

            # Удаляем купон
            cursor.execute('DELETE FROM partner_coupons WHERE id = ?', (coupon_id,))
            conn.commit()
            conn.close()

            return True, None

        except Exception as e:
            conn.close()
            return False, f"Ошибка при удалении купона: {str(e)}"
# Создаем экземпляр обертки
db = DBWrapper()

print(f"✅ HR-бот подключен к базе: {DB_PATH}")
print("🎫 Модуль управления купонами активирован")
