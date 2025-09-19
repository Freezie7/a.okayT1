from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database import db
from keyboards.main_kb import get_main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await db.create_user(message.from_user.id)
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я твой личный <b>Карьерный штурман</b>!\n"
        "Помогу тебе:\n"
        "• Найти крутые вакансии внутри компании\n"
        "• Составить план развития\n"
        "• Прокачать навыки и получить бейджи!\n\n"
        "Начни с команды /profile чтобы заполнить свой профиль!",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - начать работу\n"
        "/profile - заполнить/изменить профиль\n"
        "/career_plan - мой карьерный план\n"
        "/skills - прокачать навыки\n"
        "/badges - мои достижения\n"
        "Или используй кнопки меню ↓",
        reply_markup=get_main_keyboard()
    )