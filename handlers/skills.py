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
from config import BADGES

router = Router()

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

async def check_and_award_badges(user_id: int, skill_type: str):
    """Проверяет и выдает бейджи в зависимости от количества навыков"""
    badges_awarded = []
    
    user_stats = await db.get_user_stats(user_id)
    user_badges = await db.get_user_badges(user_id)  # Получаем текущие бейджи пользователя
    
    if skill_type == "foreign_language":
        languages_count = user_stats['languages_count']
        
        if languages_count == 1 and "language_added" not in user_badges:
            if await db.add_badge_to_user(user_id, "language_added"):
                badges_awarded.append("language_added")
        elif languages_count == 3 and "polyglot_bronze" not in user_badges:
            if await db.add_badge_to_user(user_id, "polyglot_bronze"):
                badges_awarded.append("polyglot_bronze")
        elif languages_count == 5 and "polyglot_silver" not in user_badges:
            if await db.add_badge_to_user(user_id, "polyglot_silver"):
                badges_awarded.append("polyglot_silver")
        elif languages_count >= 10 and "polyglot_gold" not in user_badges:
            if await db.add_badge_to_user(user_id, "polyglot_gold"):
                badges_awarded.append("polyglot_gold")
    
    elif skill_type == "programming":
        programming_count = user_stats['programming_count']
        
        if programming_count == 1 and "programming_added" not in user_badges:
            if await db.add_badge_to_user(user_id, "programming_added"):
                badges_awarded.append("programming_added")
        elif programming_count == 3 and "coder_bronze" not in user_badges:
            if await db.add_badge_to_user(user_id, "coder_bronze"):
                badges_awarded.append("coder_bronze")
        elif programming_count == 5 and "coder_silver" not in user_badges:
            if await db.add_badge_to_user(user_id, "coder_silver"):
                badges_awarded.append("coder_silver")
        elif programming_count >= 10 and "coder_gold" not in user_badges:
            if await db.add_badge_to_user(user_id, "coder_gold"):
                badges_awarded.append("coder_gold")
    
    # Проверяем общее количество навыков для бейджей
    total_skills = user_stats['total_skills']
    
    if total_skills >= 5 and "skill_master" not in user_badges:
        if await db.add_badge_to_user(user_id, "skill_master"):
            badges_awarded.append("skill_master")
    
    if total_skills >= 10 and "skill_guru" not in user_badges:
        if await db.add_badge_to_user(user_id, "skill_guru"):
            badges_awarded.append("skill_guru")
    
    if total_skills >= 20 and "skill_legend" not in user_badges:
        if await db.add_badge_to_user(user_id, "skill_legend"):
            badges_awarded.append("skill_legend")
    
    # Проверяем бейджи за опыт
    xp = user_stats['xp']
    
    if xp >= 100 and "xp_100" not in user_badges:
        if await db.add_badge_to_user(user_id, "xp_100"):
            badges_awarded.append("xp_100")
    
    if xp >= 500 and "xp_500" not in user_badges:
        if await db.add_badge_to_user(user_id, "xp_500"):
            badges_awarded.append("xp_500")
    
    if xp >= 1000 and "xp_1000" not in user_badges:
        if await db.add_badge_to_user(user_id, "xp_1000"):
            badges_awarded.append("xp_1000")
    
    if xp >= 5000 and "xp_5000" not in user_badges:
        if await db.add_badge_to_user(user_id, "xp_5000"):
            badges_awarded.append("xp_5000")
    
    return badges_awarded

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
        "lang_english": "English", "lang_german": "Deutsch", "lang_french": "Français",
        "lang_spanish": "Español", "lang_italian": "Italiano", "lang_portuguese": "Português",
        "lang_chinese": "中文", "lang_japanese": "日本語", "lang_korean": "한국어",
        "lang_russian": "Русский", "lang_arabic": "العربية", "lang_hindi": "हिन्दी"
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
    
    # Сохраняем в базу и проверяем результат
    added = await db.add_user_language(message.from_user.id, language, level)
    
    if not added:
        await message.answer(
            f"❌ Язык <b>{language}</b> уже есть в твоем профиле!\n"
            "Попробуй добавить другой язык или изменить уровень существующего.",
            parse_mode="HTML",
            reply_markup=get_skills_type_keyboard()
        )
        await state.set_state(ProfileState.choosing_skill_type)
        return
    
    await db.add_xp_to_user(message.from_user.id, 15)
    
    # Проверяем и выдаем бейджи
    badges_awarded = await check_and_award_badges(message.from_user.id, "foreign_language")
    
    success_message = f"🌍 <b>Добавлен язык:</b> {language} ({level})\n+15 XP!\n"
    
    if badges_awarded:
        success_message += "🎉 Получены бейджи:\n"
        for badge in badges_awarded:
            badge_info = BADGES.get(badge, {})
            success_message += f"• {badge_info.get('name', badge)}\n"
        success_message += "\n"
    
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
        "prog_cpp": "C++", "prog_csharp": "C#", "prog_php": "PHP",
        "prog_go": "Go", "prog_ruby": "Ruby", "prog_swift": "Swift",
        "prog_kotlin": "Kotlin", "prog_ts": "TypeScript", "prog_rust": "Rust",
        "prog_sql": "SQL", "prog_html": "HTML/CSS", "prog_dart": "Dart"
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
    
    # Сохраняем в базу и проверяем результат
    added = await db.add_user_programming(message.from_user.id, language, level)
    
    if not added:
        await message.answer(
            f"❌ Язык программирования <b>{language}</b> уже есть в твоем профиле!\n"
            "Попробуй добавить другой язык или изменить уровень существующего.",
            parse_mode="HTML",
            reply_markup=get_skills_type_keyboard()
        )
        await state.set_state(ProfileState.choosing_skill_type)
        return
    
    await db.add_xp_to_user(message.from_user.id, 15)
    
    # Проверяем и выдаем бейджи
    badges_awarded = await check_and_award_badges(message.from_user.id, "programming")
    
    success_message = f"💻 <b>Добавлен язык программирования:</b> {language} ({level})\n+15 XP!\n"
    
    if badges_awarded:
        success_message += "🎉 Получены бейджи:\n"
        for badge in badges_awarded:
            badge_info = BADGES.get(badge, {})
            success_message += f"• {badge_info.get('name', badge)}\n"
        success_message += "\n"
    
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
        "skill_management": "Управление проектами", "skill_marketing": "Маркетинг",
        "skill_sales": "Продажи", "skill_creativity": "Креативность",
        "skill_teamwork": "Командная работа", "skill_problem_solving": "Решение проблем"
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
    
    # Сохраняем в базу и проверяем результат
    added = await db.add_user_skill(message.from_user.id, skill, level)
    
    if not added:
        await message.answer(
            f"❌ Навык <b>{skill}</b> уже есть в твоем профиле!\n"
            "Попробуй добавить другой навык или изменить уровень существующего.",
            parse_mode="HTML",
            reply_markup=get_skills_type_keyboard()
        )
        await state.set_state(ProfileState.choosing_skill_type)
        return
    
    await db.add_xp_to_user(message.from_user.id, 15)
    
    # Проверяем и выдаем бейджи
    badges_awarded = await check_and_award_badges(message.from_user.id, "other")
    
    success_message = f"🔧 <b>Добавлен навык:</b> {skill} ({level})\n+15 XP!\n"
    
    if badges_awarded:
        success_message += "🎉 Получены бейджи:\n"
        for badge in badges_awarded:
            badge_info = BADGES.get(badge, {})
            success_message += f"• {badge_info.get('name', badge)}\n"
        success_message += "\n"
    
    success_message += "Хочешь добавить еще навыки?"
    
    await message.answer(success_message, parse_mode="HTML", reply_markup=get_skills_type_keyboard())
    await state.set_state(ProfileState.choosing_skill_type)

# ===== РЕДАКТ УРОВНЯ НАВЫКОВ =====
@router.message(Command("my_skills"))
async def cmd_my_skills(message: Message):
    """Показать все навыки пользователя с возможностью редактирования"""
    user_id = message.from_user.id
    
    languages = await db.get_user_languages(user_id)
    programming = await db.get_user_programming(user_id)
    skills = await db.get_user_skills(user_id)
    
    if not languages and not programming and not skills:
        await message.answer("У тебя пока нет навыков. Добавь их через /skills")
        return
    
    skills_text = "📊 <b>Твои навыки:</b>\n\n"
    
    if languages:
        skills_text += "🌍 <b>Иностранные языки:</b>\n"
        for lang in languages:
            skills_text += f"• {lang['language']} ({lang['level']})\n"
        skills_text += "\n"
    
    if programming:
        skills_text += "💻 <b>Языки программирования:</b>\n"
        for prog in programming:
            skills_text += f"• {prog['language']} ({prog['level']})\n"
        skills_text += "\n"
    
    if skills:
        skills_text += "🔧 <b>Другие навыки:</b>\n"
        for skill in skills:
            skills_text += f"• {skill['skill']} ({skill['level']})\n"
    
    skills_text += "\nИспользуй /skills чтобы добавить новые навыки!"
    
    await message.answer(skills_text, parse_mode="HTML")

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