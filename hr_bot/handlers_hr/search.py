from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database_utils import db
from keyboards_hr import get_hr_keyboard, get_cancel_keyboard
from states_hr import SearchState  # Импортируем состояние поиска

router = Router()

async def is_hr_user(user_id: int):
    from config_hr import HR_WHITELIST
    return user_id in HR_WHITELIST

@router.message(Command("find"))
@router.message(F.text == "🔍 Найти сотрудников")
async def cmd_find_employees(message: Message, state: FSMContext):
    if not await is_hr_user(message.from_user.id):
        await message.answer("❌ Доступ только для HR-специалистов")
        return
        
    await message.answer(
        "🔍 Введите навыки для поиска через пробел:\n\nПример: Python JavaScript Управление\n\nИли нажмите ❌ Отмена",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(SearchState.skills)

@router.message(SearchState.skills)
async def process_search_skills(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Поиск отменен", reply_markup=get_hr_keyboard())
        return
        
    skills = message.text.split()
    
    if not skills:
        await message.answer("❌ Укажите навыки для поиска!\nПример: Python JavaScript")
        return
    
    await message.answer(f"🔍 Ищу сотрудников с навыками: {', '.join(skills)}...")
    
    try:
        # Используем простой поиск
        result = await db.search_employees_by_skills_simple(skills)
        
        if not result:
            await message.answer("❌ Сотрудники с такими навыками не найдены", reply_markup=get_hr_keyboard())
        else:
            await message.answer(result, reply_markup=get_hr_keyboard())
        
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Ошибка поиска: {str(e)}", reply_markup=get_hr_keyboard())
        await state.clear()

# Добавляем обработчик для команды /find с навыками
@router.message(Command("find"))
async def cmd_find_with_skills(message: Message):
    if not await is_hr_user(message.from_user.id):
        await message.answer("❌ Доступ только для HR-специалистов")
        return
        
    skills = message.text.split()[1:]  # Берем все после /find
    
    if not skills:
        await message.answer("❌ Укажите навыки для поиска!\nПример: /find Python JavaScript")
        return
    
    await message.answer(f"🔍 Ищу сотрудников с навыками: {', '.join(skills)}...")
    
    try:
        result = await db.search_employees_by_skills_simple(skills)
        
        if not result:
            await message.answer("❌ Сотрудники с такими навыками не найдены", reply_markup=get_hr_keyboard())
        else:
            await message.answer(result, reply_markup=get_hr_keyboard())
        
    except Exception as e:
        await message.answer(f"❌ Ошибка поиска: {str(e)}", reply_markup=get_hr_keyboard())