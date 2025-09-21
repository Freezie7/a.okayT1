from aiogram.fsm.state import State, StatesGroup

class VacancyState(StatesGroup):
    title = State()
    description = State()
    skills = State()

class SearchState(StatesGroup):
    skills = State()

class CouponState(StatesGroup):
    add_quantity = State()
    decrease_quantity = State()
    create_coupon_partner = State()
    create_coupon_name = State()
    create_coupon_description = State()
    create_coupon_xp_cost = State()
    create_coupon_quantity = State()
    delete_coupon = State()