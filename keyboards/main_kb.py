from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Мой профиль"), KeyboardButton(text="🎯 Мой карьерный план")],
            [KeyboardButton(text="🔧 Прокачать навыки"), KeyboardButton(text="🏆 Мои достижения")],
            [KeyboardButton(text="💼 Вакансии внутри компании")],
            [KeyboardButton(text="🎁 Магазин купонов")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )