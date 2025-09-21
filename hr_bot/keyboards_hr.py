from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_hr_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Добавить вакансию"), KeyboardButton(text="🔍 Найти сотрудников")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📋 Список вакансий")],
            [KeyboardButton(text="📈 Аналитика навыков"), KeyboardButton(text="🎫 Управление купонами")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def get_coupons_management_keyboard():
    """Клавиатура для управления купонами"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статус купонов"), KeyboardButton(text="➕ Добавить купоны")],
            [KeyboardButton(text="➖ Уменьшить купоны"), KeyboardButton(text="📋 Список купонов")],
            [KeyboardButton(text="🆕 Создать купон"), KeyboardButton(text="🗑️ Удалить купон")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )