from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для выбора уровня образования
def get_education_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Среднее")],
            [KeyboardButton(text="Среднее специальное")],
            [KeyboardButton(text="Высшее")],
            [KeyboardButton(text="Неоконченное высшее")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери вариант ↓"
    )

# Клавиатура для пропуска шага (будет полезно в будущем)
def get_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пропустить шаг")]
        ],
        resize_keyboard=True
    )