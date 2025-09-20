import sys
import os

# Добавляем родительскую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from database import db
    print("✅ База данных успешно импортирована")
except ImportError as e:
    print(f"❌ Ошибка импорта базы данных: {e}")
    # Создаем заглушку для тестирования
    class DBStub:
        async def add_vacancy(self, *args, **kwargs):
            return 1
        async def get_vacancies(self, *args, **kwargs):
            return []
    
    db = DBStub()