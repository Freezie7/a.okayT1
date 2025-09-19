from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from states.profile_st import ProfileState
from database import db
from keyboards.main_kb import get_main_keyboard

router = Router()

# Команда /profile
@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    await message.answer(
        "🎮 <b>Давай соберём твоего профессионального аватара!</b>\n\n"
        "Каждый твой ответ — это +10 к характеристикам и новые бейджи!\n"
        "Как тебя зовут? (Имя и Фамилия)",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()  # Убираем главное меню на время заполнения
    )
    await state.set_state(ProfileState.name)
    # Начислим XP за начало заполнения
    await db.add_xp_to_user(message.from_user.id, 10)

# Обработчик состояния "name"
@router.message(ProfileState.name, F.text)
async def process_name(message: Message, state: FSMContext):
    # Сохраняем имя в базу и в состояние FSM
    await db.update_user_profile(message.from_user.id, name=message.text)
    await state.update_data(name=message.text)
    
    # Начисляем XP за ввод имени
    await db.add_xp_to_user(message.from_user.id, 10)
    
    await message.answer(
        f"Отлично, {message.text}! +10 XP к харизме! 🎉\n\n"
        "Теперь расскажи о себе кратко (2-3 предложения):\n"
        "<i>Чем занимаешься, что нравится, какие у тебя интересы...</i>",
        parse_mode="HTML"
    )
    await state.set_state(ProfileState.about)

# Обработчик состояния "about"
@router.message(ProfileState.about, F.text)
async def process_about(message: Message, state: FSMContext):
    # Сохраняем "о себе" в базу
    await db.update_user_profile(message.from_user.id, about=message.text)
    
    # Начисляем XP за ввод информации о себе
    await db.add_xp_to_user(message.from_user.id, 15)
    
    # Выдаем бейдж "Первый шаг"
    await db.add_badge_to_user(message.from_user.id, "profile_start")
    
    # Завершаем машину состояний (пока только для этих двух полей)
    await state.clear()
    
    await message.answer(
        "Супер! Ты создал основу своего профиля! +15 XP! 🚀\n"
        "Ты получил бейдж 'Первый шаг'! 🏅\n\n"
        "Теперь у тебя есть доступ к полному функционалу!",
        reply_markup=get_main_keyboard()  # Возвращаем главное меню
    )