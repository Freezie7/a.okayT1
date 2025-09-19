from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database import db
from config import BADGES

router = Router()

@router.message(Command("myprofile"))
async def cmd_view_profile(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user: return await message.answer("Сначала зарегистрируйся через /start")
    
    # Получаем все данные
    languages = await db.get_user_languages(message.from_user.id)
    programming = await db.get_user_programming(message.from_user.id)
    skills = await db.get_user_skills(message.from_user.id)
    user_badges = await db.get_user_badges(message.from_user.id)
    
    # Формируем текст с навыками
    skills_text = ""
    if languages: skills_text += "\n🌍 <b>Языки:</b>\n" + "\n".join([f"• {lang['language']} ({lang['level']})" for lang in languages])
    if programming: skills_text += "\n💻 <b>Программирование:</b>\n" + "\n".join([f"• {prog['language']} ({prog['level']})" for prog in programming])
    if skills: skills_text += "\n🔧 <b>Навыки:</b>\n" + "\n".join([f"• {skill['skill']} ({skill['level']})" for skill in skills])
    
    # Формируем текст с бейджами
    badges_text = ""
    if user_badges:
        badges_text = "\n\n🏆 <b>Бейджи:</b>\n" + "\n".join([f"• {BADGES.get(badge, {}).get('name', badge)}" for badge in user_badges])
    
    profile_text = (
        f"👤 <b>Твой профиль:</b>\n\n"
        f"<b>Имя:</b> {user['name'] or 'Не указано'}\n"
        f"<b>О себе:</b> {user['about'] or 'Не указано'}\n"
        f"<b>Образование:</b> {user['education_level'] or 'Не указано'} ({user['education_place'] or 'Не указано'})\n"
        f"<b>Цель:</b> {user['career_goal'] or 'Не указано'}"
        f"{skills_text}"
        f"{badges_text}\n\n"
        f"⭐ <b>Опыт:</b> {user['xp']} XP\n"
        f"<i>Используй /skills чтобы добавить больше навыков</i>"
    )
    
    await message.answer(profile_text, parse_mode="HTML")

# Добавляем команду для просмотра бейджей отдельно
@router.message(Command("badges"))
async def cmd_badges(message: Message):
    user_badges = await db.get_user_badges(message.from_user.id)
    
    if not user_badges:
        await message.answer("У тебя пока нет бейджей 😢\nЗаполняй профиль и добавляй навыки чтобы их получить!")
        return
    
    badges_text = "🏆 <b>Твои бейджи:</b>\n\n"
    for badge in user_badges:
        badge_info = BADGES.get(badge, {})
        badges_text += f"• {badge_info.get('name', badge)} - {badge_info.get('desc', '')}\n"
    
    badges_text += "\nПродолжай в том же духе! 💪"
    await message.answer(badges_text, parse_mode="HTML")