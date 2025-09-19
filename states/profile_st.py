from aiogram.fsm.state import State, StatesGroup

class ProfileState(StatesGroup):
    name = State()
    about = State()