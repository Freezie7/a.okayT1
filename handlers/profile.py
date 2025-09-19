from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from states.profile_st import ProfileState
from database import db
from keyboards.main_kb import get_main_keyboard
from keyboards.profile_kb import get_education_keyboard, get_skip_keyboard

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


@router.message(ProfileState.about, F.text)
async def process_about(message: Message, state: FSMContext):
    # Сохраняем "о себе" в базу
    await db.update_user_profile(message.from_user.id, about=message.text)
    await db.add_xp_to_user(message.from_user.id, 15)
    await db.add_badge_to_user(message.from_user.id, "profile_start")
    
    # Спрашиваем про уровень образования
    await message.answer(
        "📚 <b>Расскажи про свое образование</b>\n\n"
        "Какой у тебя уровень образования?",
        parse_mode="HTML",
        reply_markup=get_education_keyboard()  # Клавиатура с вариантами
    )
    await state.set_state(ProfileState.education_level)  # Переходим к следующему состоянию

# Обработчик для уровня образования
@router.message(ProfileState.education_level, F.text)
async def process_education_level(message: Message, state: FSMContext):
    await db.update_user_profile(message.from_user.id, education_level=message.text)
    await db.add_xp_to_user(message.from_user.id, 10)
    
    await message.answer(
        "Отлично! Где ты учился(лась)? Напиши название учебного заведения:",
        reply_markup=ReplyKeyboardRemove()  # Убираем клаву
    )
    await state.set_state(ProfileState.education_place)

# Обработчик для учебного заведения
@router.message(ProfileState.education_place, F.text)
async def process_education_place(message: Message, state: FSMContext):
    await db.update_user_profile(message.from_user.id, education_place=message.text)
    await db.add_xp_to_user(message.from_user.id, 10)
    
    await message.answer(
        "🎯 <b>Теперь самое интересное!</b>\n\n"
        "Кем ты хочешь стать в компании через 3 года?\n"
        "Напиши название желаемой должности:",
        parse_mode="HTML"
    )
    await state.set_state(ProfileState.career_goal)

# Обработчик для карьерной цели (ФИНАЛЬНЫЙ шаг цепочки)
@router.message(ProfileState.career_goal, F.text)
async def process_career_goal(message: Message, state: FSMContext):
    await db.update_user_profile(message.from_user.id, career_goal=message.text)
    await db.add_xp_to_user(message.from_user.id, 20)  # Больше XP за важный ответ!
    
    # Выдаем бейдж за заполнение профиля
    await db.add_badge_to_user(message.from_user.id, "profile_done")
    
    await state.clear() 
    
    await message.answer(
        f"🔥 <b>Потрясающе! Ты прошел базовое заполнение профиля!</b>\n\n"
        f"Твоя цель: <i>{message.text}</i>\n"
        f"+20 XP за четкую цель!\n"
        f"Ты получил бейдж 'Профилист'! 🏆\n\n"
        f"Теперь используй команду /myprofile чтобы посмотреть свой профиль!",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()  # Возвращаем главное меню
    )