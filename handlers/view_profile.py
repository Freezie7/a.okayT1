from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database import db

router = Router()

@router.message(Command("myprofile"))
async def cmd_view_profile(message: Message):
    user = await db.get_user(message.from_user.id)
    
    if not user:
        await message.answer("Сначала зарегистрируйся через /start")
        return
    
    # Формируем красивое сообщение с профилем
    profile_text = (
        f"👤 <b>Твой профиль:</b>\n\n"
        f"<b>Имя:</b> {user['name'] or 'Не указано'}\n"
        f"<b>О себе:</b> {user['about'] or 'Не указано'}\n"
        f"<b>Образование:</b> {user['education_level'] or 'Не указано'} ({user['education_place'] or 'Не указано'})\n"
        f"<b>Цель:</b> {user['career_goal'] or 'Не указано'}\n\n"
        f"⭐ <b>Опыт:</b> {user['xp']} XP\n"
        f"<i>Используй /profile чтобы дополнить профиль</i>"
    )
    
    await message.answer(profile_text, parse_mode="HTML")