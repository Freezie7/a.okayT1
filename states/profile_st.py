from aiogram.fsm.state import State, StatesGroup

class ProfileState(StatesGroup):
    name = State()
    education_level = State()
    education_place = State()
    career_goal = State()
    
    # Состояния для навыков
    choosing_skill_type = State()          # Выбор типа навыка
    foreign_language = State()             # Иностранный язык
    foreign_language_level = State()       # Уровень языка
    programming_language = State()         # Язык программирования  
    programming_language_level = State()   # Уровень языка программирования
    other_skill = State()                  # Другой навык
    other_skill_level = State()            # Уровень другого навыка