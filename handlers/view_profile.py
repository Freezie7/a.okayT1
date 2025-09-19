from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database import db
from config import BADGES
from keyboards.main_kb import get_main_keyboard

router = Router()

@router.message(Command("myprofile"))
async def cmd_view_profile(message: Message):
    user = await db.get_user(message.from_user.id)
    
    if not user:
        await message.answer("Сначала зарегистрируйся через /start")
        return
    
    # Получаем все данные
    languages = await db.get_user_languages(message.from_user.id)
    programming = await db.get_user_programming(message.from_user.id)
    skills = await db.get_user_skills(message.from_user.id)
    user_badges = await db.get_user_badges(message.from_user.id)
    
    # Проверяем, заполнен ли базовый профиль
    is_profile_complete = all([
        user['name'], 
        user['about'], 
        user['education_level'], 
        user['education_place'],
        user['career_goal']
    ])
    
    # Формируем текст с навыками
    skills_text = ""
    if languages: 
        skills_text += "\n🌍 <b>Иностранные языки:</b>\n" + "\n".join([f"• {lang['language']} ({lang['level']})" for lang in languages])
    if programming: 
        skills_text += "\n💻 <b>Языки программирования:</b>\n" + "\n".join([f"• {prog['language']} ({prog['level']})" for prog in programming])
    if skills: 
        skills_text += "\n🔧 <b>Другие навыки:</b>\n" + "\n".join([f"• {skill['skill']} ({skill['level']})" for skill in skills])
    
    # Формируем текст с бейджами
    badges_text = ""
    if user_badges:
        badges_text = "\n\n🏆 <b>Бейджи:</b>\n" + "\n".join([f"• {BADGES.get(badge, {}).get('name', badge)}" for badge in user_badges])
    
    # Сообщение о заполнении профиля
    profile_complete_text = ""
    if not is_profile_complete:
        profile_complete_text = "\n\n⚠️ <i>Профиль заполнен не полностью. Используй /profile чтобы дополнить информацию!</i>"
    else:
        profile_complete_text = "\n\n✅ <i>Основной профиль заполнен! Молодец!</i>"
    
    profile_text = (
        f"👤 <b>Твой профиль:</b>\n\n"
        f"<b>Имя:</b> {user['name'] or 'Не указано'}\n"
        f"<b>О себе:</b> {user['about'] or 'Не указано'}\n"
        f"<b>Образование:</b> {user['education_level'] or 'Не указано'} ({user['education_place'] or 'Не указано'})\n"
        f"<b>Цель:</b> {user['career_goal'] or 'Не указано'}"
        f"{skills_text}"
        f"{badges_text}"
        f"{profile_complete_text}\n\n"
        f"⭐ <b>Опыт:</b> {user['xp']} XP\n"
        f"<i>Используй /skills чтобы добавить больше навыков</i>"
    )
    
    await message.answer(profile_text, parse_mode="HTML")

# Добавляем команду для просмотра бейджей отдельно
@router.message(Command("badges"))
async def cmd_badges(message: Message):
    user_badges = await db.get_user_badges(message.from_user.id)
    
    if not user_badges:
        await message.answer(
            "У тебя пока нет бейджей 😢\n"
            "Заполняй профиль через /profile и добавляй навыки через /skills чтобы их получить! 💪"
        )
        return
    
    badges_text = "🏆 <b>Твои бейджи:</b>\n\n"
    for badge in user_badges:
        badge_info = BADGES.get(badge, {})
        badges_text += f"• <b>{badge_info.get('name', badge)}</b> - {badge_info.get('desc', '')}\n"
    
    badges_text += "\nПродолжай в том же духе! 💪"
    await message.answer(badges_text, parse_mode="HTML")

# Добавляем команду для просмотра навыков
@router.message(Command("my_skills"))
async def cmd_my_skills(message: Message):
    """Показать все навыки пользователя"""
    user_id = message.from_user.id
    
    languages = await db.get_user_languages(user_id)
    programming = await db.get_user_programming(user_id)
    skills = await db.get_user_skills(user_id)
    
    if not languages and not programming and not skills:
        await message.answer(
            "У тебя пока нет навыков 😢\n"
            "Используй /skills чтобы добавить первые навыки! 🔧"
        )
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