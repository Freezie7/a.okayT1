
from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database_utils import db
from states_hr import VacancyState
from keyboards_hr import get_hr_keyboard, get_cancel_keyboard

from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
import asyncio
router = Router()

# ===== КОНФИГУРАЦИЯ ДЛЯ ПЕРВОГО БОТА =====
BOT_TOKEN_MAIN = "8464487214:AAEI2IR5kmOauF_JCsYngPo_gVy-ldBXPA4"  # Замените на токен первого бота

async def is_hr_user(user_id: int):
    from config_hr import HR_WHITELIST
    return user_id in HR_WHITELIST

bot = Bot(token=BOT_TOKEN_MAIN)
async def notify_matching_employees(vacancy_name: str,vacancy_id: str, user_ids: list[int]) -> int:
    """
    Отправляет уведомления сотрудникам о новой вакансии.

    Args:
        vacancy_id: ID вакансии.
        user_ids: Список ID пользователей Telegram.

    Returns:
        Количество успешно отправленных уведомлений.
    """

    user_ids = list(set(user_ids))
    notified_count = 0
    for user_id in user_ids:
        try:
            message_text = (
                f"🎉 *Новая вакансия!* 🎉\n\n"  # Заголовок
                f"Появилась новая вакансий которая вам подойдет!\n\n"
                f"💼 *Вакансия:* {vacancy_name} ID:{vacancy_id}\n\n"  # Название вакансии (жирным)
                f"Подробности вы можете узнать в <💼 Вакансии внутри компании> ")

            try:
                await bot.send_message(chat_id=user_id, text=message_text)  # user_id тут - это telegram ID.
                notified_count += 1
                await asyncio.sleep(0.1)  # Небольшая задержка

            except TelegramForbiddenError:
                print(f"У пользователя {user_id} заблокирован бот.")
            except TelegramBadRequest as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
            except Exception as e:
                print(f"Неизвестная ошибка при отправке уведомления пользователю {user_id}: {e}")

        except Exception as e:
            print(f"Ошибка при обработке пользователя {user_id}: {e}")

    return notified_count

@router.message(Command("add_vacancy"))
@router.message(F.text == "📝 Добавить вакансию")
async def cmd_add_vacancy(message: Message, state: FSMContext):
    if not await is_hr_user(message.from_user.id):
        await message.answer("❌ Доступ только для HR-специалистов")
        return
        
    await message.answer(
        "📝 Добавление новой вакансии:\nВведите название должности:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(VacancyState.title)

@router.message(VacancyState.title)
async def process_vacancy_title(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Действие отменено", reply_markup=get_hr_keyboard())
        return
        
    await state.update_data(title=message.text)
    await message.answer("Теперь введите описание вакансии:")
    await state.set_state(VacancyState.description)

@router.message(VacancyState.description)  
async def process_vacancy_description(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Действие отменено", reply_markup=get_hr_keyboard())
        return
        
    await state.update_data(description=message.text)
    await message.answer("Введите требуемые навыки через пробел:\n\nПример: Python Django SQL English")
    await state.set_state(VacancyState.skills)

@router.message(VacancyState.skills)
async def process_vacancy_skills(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Действие отменено", reply_markup=get_hr_keyboard())
        return
        
    data = await state.get_data()
    
    # Сохраняем вакансию в БД
    vacancy_id = await db.add_vacancy(
        title=data['title'],
        description=data['description'],
        required_skills=message.text,
        created_by=message.from_user.id
    )

    vacancy_name = data["title"]
    
    # Показываем сообщение о успешном добавлении
    success_message = (
        f"✅ *Вакансия добавлена!*\n\n"
        f"📝 *Должность:* {data['title']}\n"
        f"🔧 *Требуемые навыки:* {message.text}\n"
        f"🆔 *ID вакансии:* {vacancy_id}"
    )
    
    await message.answer(success_message, parse_mode="Markdown", reply_markup=get_hr_keyboard())
    await state.clear()
    
    # # ===== ТОЧНО ТАКАЯ ЖЕ ПРОВЕРКА КАК В SEARCH.PY =====
    # skills = message.text.split()

    # await message.answer(f"🔍 Ищу сотрудников с навыками: {', '.join(skills)}...")

    # try:
    #     # Используем простой поиск (точно такой же как в search.py)
    #     user_ids = await db.search_employees_by_skills_simple2(skills)  # Получаем список user_id

    #     if not user_ids:
    #         search_result_message = "❌ Сотрудники с такими навыками не найдены"
    #     else:
    #         # Формируем сообщение для пользователя (опционально, можно убрать, если не нужно)
    #         search_result_message = "✅ Сотрудники найдены"
    #         print(map(str, user_ids));

    #     await message.answer(search_result_message, reply_markup=get_hr_keyboard())

    # except Exception as e:
    #     await message.answer(f"❌ Ошибка поиска: {str(e)}", reply_markup=get_hr_keyboard())

    # # Отправляем уведомления подходящим сотрудникам в фоновом режиме
    # notified_count = await notify_matching_employees(vacancy_name, vacancy_id, user_ids) #
    
    # if notified_count > 0:
    #     await message.answer(f"📨 Отправлено уведомлений: {notified_count} сотрудникам")
    # else:
    #     await message.answer("ℹ️ Не было отправлено ни одного уведомления")

@router.message(Command("vacancies"))
@router.message(F.text == "📋 Список вакансий")
async def cmd_list_vacancies(message: Message):
    if not await is_hr_user(message.from_user.id):
        await message.answer("❌ Доступ только для HR-специалистов")
        return
        
    vacancies = await db.get_vacancies()
    
    if not vacancies:
        await message.answer("📭 Нет активных вакансий")
        return
        
    response = "📋 *Активные вакансии:*\n\n"
    
    for vacancy in vacancies:
        response += f"🆔 *ID:* {vacancy['id']}\n"
        response += f"📝 *Должность:* {vacancy['title']}\n"
        response += f"🔧 *Навыки:* {vacancy['required_skills']}\n"
        response += f"📅 *Дата:* {vacancy['created_at']}\n"
        response += "─" * 30 + "\n"
    
    await message.answer(response, parse_mode="Markdown")

@router.message(Command("close_vacancy"))
async def cmd_close_vacancy(message: Message):
    if not await is_hr_user(message.from_user.id):
        await message.answer("❌ Доступ только для HR-специалистов")
        return
        
    # Извлекаем ID вакансии из команды /close_vacancy 123
    try:
        vacancy_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("❌ Укажите ID вакансии: /close_vacancy 123")
        return
    
    # Закрываем вакансию
    await db.close_vacancy(vacancy_id)
    await message.answer(f"✅ Вакансия #{vacancy_id} закрыта")
