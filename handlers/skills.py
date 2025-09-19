from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from states.profile_st import ProfileState
from database import db
from keyboards.profile_kb import (get_skills_type_keyboard, get_level_keyboard,
                                 get_popular_languages_keyboard, get_popular_programming_keyboard,
                                 get_popular_skills_keyboard)
from keyboards.main_kb import get_main_keyboard

router = Router()

# ===== ОБРАБОТЧИКИ ДЛЯ ИНОСТРАННЫХ ЯЗЫКОВ =====

@router.message(Command("skills"))
async def cmd_skills(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🔧 <b>Прокачка навыков!</b>\n\n"
        "Выбери, какие навыки хочешь добавить:",
        parse_mode="HTML",
        reply_markup=get_skills_type_keyboard()
    )
    await state.set_state(ProfileState.choosing_skill_type)

@router.message(ProfileState.choosing_skill_type, F.text == "🌍 Иностранные языки")
async def choose_foreign_language(message: Message, state: FSMContext):
    await message.answer(
        "Выбери язык или введи свой:",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "Популярные языки:",
        reply_markup=get_popular_languages_keyboard()
    )
    await state.set_state(ProfileState.foreign_language)

@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery, state: FSMContext):
    language_map = {
        "lang_english": "English", "lang_german": "Deutsch", 
        "lang_spanish": "Español", "lang_french": "Français",
        "lang_chinese": "中文", "lang_japanese": "日本語"
    }
    
    if callback.data == "lang_other":
        await callback.message.answer("Введи название языка:")
        await state.set_state(ProfileState.foreign_language)
    else:
        language = language_map[callback.data]
        await state.update_data(language=language)
        await callback.message.answer(
            f"Выбран язык: <b>{language}</b>\n\nТеперь выбери уровень владения:",
            parse_mode="HTML",
            reply_markup=get_level_keyboard()
        )
        await state.set_state(ProfileState.foreign_language_level)
    await callback.answer()

@router.message(ProfileState.foreign_language, F.text)
async def process_custom_language(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer(
        f"Отлично! Теперь выбери уровень владения <b>{message.text}</b>:",
        parse_mode="HTML",
        reply_markup=get_level_keyboard()
    )
    await state.set_state(ProfileState.foreign_language_level)

@router.message(ProfileState.foreign_language_level, F.text)
async def process_language_level(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language')
    level = message.text
    
    if not language:
        await message.answer("Что-то пошло не так. Давай начнем сначала: /skills")
        await state.clear()
        return
    
    await db.add_user_language(message.from_user.id, language, level)
    await db.add_xp_to_user(message.from_user.id, 15)
    
    badge_awarded = await db.add_badge_to_user(message.from_user.id, "language_added")
    
    success_message = f"🌍 <b>Добавлен язык:</b> {language} ({level})\n+15 XP!\n"
    if badge_awarded: success_message += "🎉 Ты получил бейдж 'Полиглот'!\n\n"
    success_message += "Хочешь добавить еще навыки?"
    
    await message.answer(success_message, parse_mode="HTML", reply_markup=get_skills_type_keyboard())
    await state.set_state(ProfileState.choosing_skill_type)

# ===== ОБРАБОТЧИКИ ДЛЯ ЯЗЫКОВ ПРОГРАММИРОВАНИЯ =====

@router.message(ProfileState.choosing_skill_type, F.text == "💻 Языки программирования")
async def choose_programming_language(message: Message, state: FSMContext):
    await message.answer(
        "Выбери язык программирования или введи свой:",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "Популярные языки программирования:",
        reply_markup=get_popular_programming_keyboard()
    )
    await state.set_state(ProfileState.programming_language)

@router.callback_query(F.data.startswith("prog_"))
async def process_programming_selection(callback: CallbackQuery, state: FSMContext):
    programming_map = {
        "prog_python": "Python", "prog_js": "JavaScript", "prog_java": "Java",
        "prog_cpp": "C++", "prog_sql": "SQL", "prog_php": "PHP",
        "prog_go": "Go", "prog_ruby": "Ruby", "prog_swift": "Swift"
    }
    
    if callback.data == "prog_other":
        await callback.message.answer("Введи название языка программирования:")
        await state.set_state(ProfileState.programming_language)
    else:
        language = programming_map[callback.data]
        await state.update_data(programming_language=language)
        await callback.message.answer(
            f"Выбран язык: <b>{language}</b>\n\nТеперь выбери уровень владения:",
            parse_mode="HTML",
            reply_markup=get_level_keyboard()
        )
        await state.set_state(ProfileState.programming_language_level)
    await callback.answer()

@router.message(ProfileState.programming_language, F.text)
async def process_custom_programming(message: Message, state: FSMContext):
    await state.update_data(programming_language=message.text)
    await message.answer(
        f"Отлично! Теперь выбери уровень владения <b>{message.text}</b>:",
        parse_mode="HTML",
        reply_markup=get_level_keyboard()
    )
    await state.set_state(ProfileState.programming_language_level)

@router.message(ProfileState.programming_language_level, F.text)
async def process_programming_level(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('programming_language')
    level = message.text
    
    if not language:
        await message.answer("Что-то пошло не так. Давай начнем сначала: /skills")
        await state.clear()
        return
    
    await db.add_user_programming(message.from_user.id, language, level)
    await db.add_xp_to_user(message.from_user.id, 15)
    
    badge_awarded = await db.add_badge_to_user(message.from_user.id, "programming_added")
    
    success_message = f"💻 <b>Добавлен язык программирования:</b> {language} ({level})\n+15 XP!\n"
    if badge_awarded: success_message += "🎉 Ты получил бейдж 'Кодер'!\n\n"
    success_message += "Хочешь добавить еще навыки?"
    
    await message.answer(success_message, parse_mode="HTML", reply_markup=get_skills_type_keyboard())
    await state.set_state(ProfileState.choosing_skill_type)

# ===== ОБРАБОТЧИКИ ДЛЯ ДРУГИХ НАВЫКОВ =====

@router.message(ProfileState.choosing_skill_type, F.text == "🔧 Другие навыки")
async def choose_other_skills(message: Message, state: FSMContext):
    await message.answer(
        "Выбери навык или введи свой:",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "Популярные навыки:",
        reply_markup=get_popular_skills_keyboard()
    )
    await state.set_state(ProfileState.other_skill)

@router.callback_query(F.data.startswith("skill_"))
async def process_skill_selection(callback: CallbackQuery, state: FSMContext):
    skills_map = {
        "skill_leadership": "Лидерство", "skill_communication": "Коммуникация",
        "skill_design": "Дизайн", "skill_analysis": "Аналитика",
        "skill_management": "Управление проектами", "skill_marketing": "Маркетинг"
    }
    
    if callback.data == "skill_other":
        await callback.message.answer("Введи название навыка:")
        await state.set_state(ProfileState.other_skill)
    else:
        skill = skills_map[callback.data]
        await state.update_data(skill=skill)
        await callback.message.answer(
            f"Выбран навык: <b>{skill}</b>\n\nТеперь выбери уровень владения:",
            parse_mode="HTML",
            reply_markup=get_level_keyboard()
        )
        await state.set_state(ProfileState.other_skill_level)
    await callback.answer()

@router.message(ProfileState.other_skill, F.text)
async def process_custom_skill(message: Message, state: FSMContext):
    await state.update_data(skill=message.text)
    await message.answer(
        f"Отлично! Теперь выбери уровень владения <b>{message.text}</b>:",
        parse_mode="HTML",
        reply_markup=get_level_keyboard()
    )
    await state.set_state(ProfileState.other_skill_level)

@router.message(ProfileState.other_skill_level, F.text)
async def process_skill_level(message: Message, state: FSMContext):
    data = await state.get_data()
    skill = data.get('skill')
    level = message.text
    
    if not skill:
        await message.answer("Что-то пошло не так. Давай начнем сначала: /skills")
        await state.clear()
        return
    
    await db.add_user_skill(message.from_user.id, skill, level)
    await db.add_xp_to_user(message.from_user.id, 15)
    
    # Проверяем общее количество навыков для бейджа "Мастер навыков"
    user_stats = await db.get_user_stats(message.from_user.id)
    badge_awarded = False
    if user_stats['total_skills'] >= 5:
        badge_awarded = await db.add_badge_to_user(message.from_user.id, "skill_master")
    
    success_message = f"🔧 <b>Добавлен навык:</b> {skill} ({level})\n+15 XP!\n"
    if badge_awarded: success_message += "🎉 Ты получил бейдж 'Мастер навыков'!\n\n"
    success_message += "Хочешь добавить еще навыки?"
    
    await message.answer(success_message, parse_mode="HTML", reply_markup=get_skills_type_keyboard())
    await state.set_state(ProfileState.choosing_skill_type)

# ===== ОБЩИЕ ОБРАБОТЧИКИ =====

@router.message(ProfileState.choosing_skill_type, F.text == "✅ Завершить добавление")
async def finish_skills(message: Message, state: FSMContext):
    await message.answer(
        "🎉 Отлично! Твои навыки сохранены!\n"
        "Используй /myprofile чтобы посмотреть свой профиль.",
        reply_markup=get_main_keyboard()
    )
    await state.clear()

@router.message(StateFilter(ProfileState))
async def process_unknown_message_in_skills(message: Message):
    await message.answer(
        "Пожалуйста, ответь на предыдущий вопрос 🙂\n"
        "Или используй /cancel чтобы прервать заполнение навыков"
    )

@router.message(Command("cancel"))
async def cmd_cancel_skills(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добавление навыков прервано.\nТвои уже введенные данные сохранены!",
        reply_markup=get_main_keyboard()
    )