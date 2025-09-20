from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database_utils import db
from keyboards_hr import get_hr_keyboard

router = Router()

async def is_hr_user(user_id: int):
    from config_hr import HR_WHITELIST
    return user_id in HR_WHITELIST

@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика")
async def cmd_stats(message: Message):
    if not await is_hr_user(message.from_user.id):
        await message.answer("❌ Доступ только для HR-специалистов")
        return
        
    try:
        total_registered = await db.get_users_count()
        total_with_names = await db.get_users_with_names_count()
        active_users = await db.get_active_users_count()
        total_skills = await db.get_total_skills_count()
        vacancies = await db.get_vacancies()
        total_vacancies = len(vacancies)
        
        response = (
            f"📊 Статистика компании:\n\n"
            f"• 👥 Всего зарегистрировано: {total_registered}\n"
            f"• 📝 С заполненными профилями: {total_with_names}\n"
            f"• ✅ Активных пользователей: {active_users}\n"
            f"• 📋 Активных вакансий: {total_vacancies}\n"
            f"• 🔧 Всего навыков: {total_skills}\n\n"
        )
        
        if total_registered > 0:
            completion_rate = (total_with_names / total_registered) * 100
            response += f"• 📈 Заполнение профилей: {completion_rate:.1f}%\n\n"
        
        # Показываем топ пользователей
        if total_with_names > 0:
            all_users = await db.get_all_users()
            response += "🏆 Топ-3 по опыту:\n"
            for i, user in enumerate(all_users[:3], 1):
                response += f"  {i}. {user['name']} - {user['xp']} XP\n"
        
        await message.answer(response, reply_markup=get_hr_keyboard())
        
    except Exception as e:
        await message.answer(f"❌ Ошибка получения статистики: {str(e)}")

@router.message(Command("debug_users"))
async def cmd_debug_users(message: Message):
    """Отладочная команда - показать всех пользователей"""
    if not await is_hr_user(message.from_user.id):
        return
        
    try:
        # Используем отладочную функцию
        all_users = await db.debug_get_all_users()
        
        response = f"🐛 Все пользователи в базе ({len(all_users)}):\n\n"
        
        for user in all_users:
            status = "✅" if user['name'] else "❌"
            response += f"{status} ID: {user['user_id']}, Name: {user['name']}, XP: {user['xp']}\n"
            if len(response) > 3500:  # Ограничение Telegram
                response += "... (и еще)"
                break
        
        await message.answer(response)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка отладки: {str(e)}")