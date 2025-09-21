from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards_hr import get_hr_keyboard

router = Router()

async def is_hr_user(user_id: int):
    from config_hr import HR_WHITELIST
    return user_id in HR_WHITELIST

@router.message(Command("start"))
async def cmd_start_hr(message: Message):
    if not await is_hr_user(message.from_user.id):
        await message.answer("❌ Доступ только для HR-специалистов")
        return
        
    await message.answer(
        "🤵 *Добро пожаловать в HR-панель!*\n\n"
        "Здесь вы можете управлять вакансиями и находить сотрудников.\n\n"
        "📋 *Доступные команды:*\n"
        "• /add_vacancy - добавить вакансию\n"
        "• /list_vacancies - список вакансий\n"  
        "• /close_vacancy [id] - закрыть вакансию\n"
        "• /vacancy_stats - статистика вакансий\n"
        "• /find - поиск сотрудников\n"
        "• /stats - общая статистика\n\n"
        "Или используйте кнопки меню ↓",
        parse_mode="Markdown",
        reply_markup=get_hr_keyboard()
    )

@router.message(Command("help"))
async def cmd_help_hr(message: Message):
    if not await is_hr_user(message.from_user.id):
        await message.answer("❌ Доступ только для HR-специалистов")
        return
        
    help_text = (
        "📋 *Помощь по HR-боту:*\n\n"
        "📝 *Вакансии:*\n"
        "• /add_vacancy - создать новую вакансию\n"
        "• /list_vacancies - список всех вакансий\n"
        "• /close_vacancy 123 - закрыть вакансию №123\n"
        "• /vacancy_stats - статистика по вакансиям\n\n"
        "🔍 *Поиск сотрудников:*\n"
        "• /find Python JavaScript - поиск по навыкам\n"
        "• Или нажмите кнопку 'Найти сотрудников'\n\n"
        "📊 *Аналитика:*\n"
        "• /stats - общая статистика компании\n"
        "• /all_employees - все сотрудники\n\n"
        "Для начала работы нажмите 'Добавить вакансию' или используйте команды выше."
    )
    
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_hr_keyboard())