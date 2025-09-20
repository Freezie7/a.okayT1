from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database import db

router = Router()

@router.message(Command("vacancies"))
async def cmd_vacancies(message: Message):
    """Показать все активные вакансии"""
    try:
        vacancies = await db.get_active_vacancies()
        
        if not vacancies:
            await message.answer("📭 На данный момент нет открытых вакансий")
            return
        
        response = "📋 *Открытые вакансии:*\n\n"
        
        for vacancy in vacancies:
            response += f"📝 *{vacancy['title']}*\n"
            response += f"📄 {vacancy['description']}\n"
            response += f"🔧 *Требуемые навыки:* {vacancy['required_skills']}\n"
            response += "─" * 30 + "\n"
        
        response += "\nЕсли вы подходите по навыкам - свяжитесь с HR-отделом!"
        
        await message.answer(response, parse_mode="Markdown")
        
    except Exception as e:
        await message.answer("❌ Не удалось загрузить вакансии. Попробуйте позже.")
        print(f"Ошибка загрузки вакансий: {e}")