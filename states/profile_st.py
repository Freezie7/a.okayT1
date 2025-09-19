from aiogram.fsm.state import State, StatesGroup

class ProfileState(StatesGroup):
    name = State()
    about = State()
    # Добавляем новые поля
    education_level = State()  # Уровень образования
    education_place = State()  # Учебное заведение
    career_goal = State()      # Карьерная цель