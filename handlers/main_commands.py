from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from database import db
from keyboards.main_kb import get_main_keyboard
from states.profile_st import ProfileState

router = Router()

# ===== ОБРАБОТЧИКИ КНОПОК ГЛАВНОГО МЕНЮ =====

# Обработчик кнопки "📊 Мой профиль"
@router.message(F.text == "📊 Мой профиль")
async def my_profile_button(message: Message):
    # Перенаправляем на команду /myprofile
    from handlers.view_profile import cmd_view_profile
    await cmd_view_profile(message)

# Обработчик кнопки "🎯 Мой карьерный план"
@router.message(F.text == "🎯 Мой карьерный план")
async def my_career_plan_button(message: Message):
    await message.answer(
        "🚧 <b>Карьерный план в разработке!</b>\n\n"
        "Скоро здесь появится персональный план развития от ИИ-консультанта "
        "на основе твоих навыков и целей!\n\n"
        "А пока продолжай заполнять профиль через /profile и добавлять навыки через /skills 💪",
        parse_mode="HTML"
    )

# Обработчик кнопки "🔧 Прокачать навыки" - ИСПРАВЛЕННЫЙ
@router.message(F.text == "🔧 Прокачать навыки")
async def improve_skills_button(message: Message, state: FSMContext):
    # Просто вызываем команду skills
    await message.answer(
        "Переходим к прокачке навыков! 🔧",
        reply_markup=ReplyKeyboardRemove()
    )
    # Имитируем вызов команды /skills
    from handlers.skills import cmd_skills
    await cmd_skills(message, state)

# Обработчик кнопки "🏆 Мои достижения"
@router.message(F.text == "🏆 Мои достижения")
async def my_achievements_button(message: Message):
    # Перенаправляем на команду /badges
    from handlers.view_profile import cmd_badges
    await cmd_badges(message)

# Обработчик кнопки "💼 Вакансии внутри компании"
@router.message(F.text == "💼 Вакансии внутри компании")
async def internal_vacancies_button(message: Message):
    await message.answer(
        "🚧 <b>Система вакансий в разработке!</b>\n\n"
        "Скоро здесь появятся:\n"
        "• Актуальные вакансии компании\n"
        "• Рекомендации based on твоих навыков\n"
        "• Возможность подать заявку\n\n"
        "А пока продолжай прокачивать навыки! 🔧",
        parse_mode="HTML"
    )

# ===== ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ =====

# Обработчик команды /menu - показать главное меню
@router.message(Command("menu"))
async def show_main_menu(message: Message):
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_keyboard()
    )

# Обработчик команды /help - помощь
@router.message(Command("help"))
async def show_help(message: Message):
    help_text = (
        "🤖 <b>CareerPilot Bot - помощь</b>\n\n"
        "Основные команды:\n"
        "• /start - начать работу\n"
        "• /profile - заполнить/изменить профиль\n"
        "• /skills - добавить навыки\n"
        "• /myprofile - посмотреть свой профиль\n"
        "• /my_skills - посмотреть все навыки\n"
        "• /badges - мои достижения\n"
        "• /menu - показать главное меню\n\n"
        "Или используй кнопки ниже ↓"
    )
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_keyboard())

# Обработчик для любого неизвестного сообщения
@router.message()
async def unknown_message(message: Message):
    await message.answer(
        "Не понял тебя 😕\n"
        "Используй кнопки меню или команду /help для справки",
        reply_markup=get_main_keyboard()
    )