from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_hr_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Добавить вакансию"), KeyboardButton(text="🔍 Найти сотрудников")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📋 Список вакансий")],
            [KeyboardButton(text="📈 Аналитика навыков")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )
