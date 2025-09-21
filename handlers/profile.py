from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from states.profile_st import ProfileState
from database import db
from keyboards.main_kb import get_main_keyboard
from keyboards.profile_kb import get_education_keyboard, get_skip_keyboard

router = Router()

# Команда /profile - начало заполнения профиля
@router.message(Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    # Проверяем, есть ли пользователь в базе
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("Сначала запусти бота командой /start")
        return
    
    await message.answer(
        "🎮 <b>Давай соберём твоего профессионального аватара!</b>\n\n"
        "Каждый твой ответ — это +10 к характеристикам и новые бейджи!\n"
        "Как тебя зовут? (Имя и Фамилия)",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()  # Убираем главное меню на время заполнения
    )
    await state.set_state(ProfileState.name)
    # Начислим XP за начало заполнения!
    await db.add_xp_to_user(message.from_user.id, 10)

# Обработчик состояния "name"
@router.message(ProfileState.name, F.text)
async def process_name(message: Message, state: FSMContext):
    # Сохраняем имя в базу и в состояние FSM
    await db.update_user_profile(message.from_user.id, name=message.text)
    await state.update_data(name=message.text)
    
    # Начисляем XP за ввод имени
    await db.add_xp_to_user(message.from_user.id, 10)
    
    # Пропускаем шаг "about" и сразу переходим к образованию
    await message.answer(
        f"Отлично, {message.text}! +10 XP к харизме! 🎉\n\n"
        "📚 <b>Расскажи про свое образование</b>\n\n"
        "Какой у тебя уровень образования?",
        parse_mode="HTML",
        reply_markup=get_education_keyboard()  # Клавиатура с вариантами
    )
    await state.set_state(ProfileState.education_level)

# Обработчик для уровня образования
@router.message(ProfileState.education_level, F.text)
async def process_education_level(message: Message, state: FSMContext):
    await db.update_user_profile(message.from_user.id, education_level=message.text)
    await db.add_xp_to_user(message.from_user.id, 10)
    
    await message.answer(
        "Отлично! Где ты учился(лась)? Напиши название учебного заведения:",
        reply_markup=ReplyKeyboardRemove()  # Убираем спец. клавиатуру
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
    badge_awarded = await db.add_badge_to_user(message.from_user.id, "profile_done")
    
    await state.clear()  # Важно: завершаем машину состояний
    
    success_message = (
        f"🔥 <b>Потрясающе! Ты прошел базовое заполнение профиля!</b>\n\n"
        f"Твоя цель: <i>{message.text}</i>\n"
        f"+20 XP за четкую цель!\n"
    )
    
    if badge_awarded:
        success_message += "Ты получил бейдж 'Профилист'! 🏆\n\n"
    
    success_message += (
        f"Теперь используй команду /myprofile чтобы посмотреть свой профиль!\n"
        f"Или начни прокачивать навыки командой /skills"
    )
    
    await message.answer(
        success_message,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()  # Возвращаем главное меню
    )

# Обработчик для команды отмены заполнения профиля
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять 🤷")
        return
    
    await state.clear()
    await message.answer(
        "Заполнение профиля прервано.\n"
        "Твои уже введенные данные сохранены!",
        reply_markup=get_main_keyboard()
    )