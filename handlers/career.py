from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F

from database import db
from ai.scibox_service import scibox_service

router = Router()

# Обработчик для команды /career_plan
@router.message(Command("career_plan"))
async def cmd_career_plan(message: Message):
    await generate_career_plan(message)

# Обработчик для кнопки "🎯 Мой карьерный план"  
@router.message(F.text == "🎯 Мой карьерный план")
async def career_plan_button(message: Message):
    await generate_career_plan(message)

# Общая функция генерации плана
async def generate_career_plan(message: Message):
    """Генерация персонального карьерного плана"""
    
    # Получаем данные пользователя
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    # Проверяем, есть ли пользователь и заполнено ли имя
    if not user or not user['name']:
        await message.answer("❌ Сначала заполни профиль через /profile")
        return
    
    # Получаем все навыки пользователя
    languages = await db.get_user_languages(user_id)
    programming = await db.get_user_programming(user_id)  
    skills = await db.get_user_skills(user_id)
    
    # Проверяем, есть ли хотя бы какие-то данные
    if not languages and not programming and not skills and not user['career_goal']:
        await message.answer(
            "📋 Для генерации карьерного плана нужно:\n"
            "• Заполнить профиль /profile\n"
            "• Добавить навыки /skills\n"
            "• Указать карьерную цель"
        )
        return
    
    # Показываем что идет генерация
    wait_msg = await message.answer("🧠 <b>ИИ-консультант анализирует твой профиль...</b>\nЭто займет 20-30 секунд", parse_mode="HTML")
    
    try:
        # Формируем данные для ИИ
        user_data = {
            "name": user['name'],
            "about": " ",
            "education_level": user['education_level'],
            "education_place": user['education_place'],
            "career_goal": user['career_goal'],
            "languages": languages,
            "programming": programming,
            "skills": skills
        }
        
        # Генерируем план
        career_plan = await scibox_service.generate_career_plan(user_data)
        
        # Пытаемся удалить сообщение "генерируется"
        try:
            await wait_msg.delete()
        except:
            pass
        
        # Отправляем заголовок
        await message.answer("🎯 <b>Ваш карьерный план:</b>\n" + "═" * 35, parse_mode="HTML")
        
        # Разбиваем план на части если нужно
        if len(career_plan) > 4000:
            parts = [career_plan[i:i+4000] for i in range(0, len(career_plan), 4000)]
            for i, part in enumerate(parts, 1):
                if i == 1:
                    await message.answer(part)
                else:
                    await message.answer(part)
        else:
            await message.answer(career_plan)
        
        # Начисляем XP за использование ИИ
        await db.add_xp_to_user(user_id, 25)
        await message.answer("✅ +25 XP за использование ИИ-консультанта! 🚀")
        
    except Exception as e:
        # Пытаемся удалить сообщение "генерируется"
        try:
            await wait_msg.delete()
        except:
            pass
        
        await message.answer("❌ Не удалось сгенерировать план. Попробуйте позже.")
