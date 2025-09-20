from aiogram.fsm.state import State, StatesGroup

class VacancyState(StatesGroup):
    title = State()
    description = State()
    skills = State()

class SearchState(StatesGroup):
    skills = State()