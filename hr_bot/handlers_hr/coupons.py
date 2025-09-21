from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from states_hr import CouponState
from database_utils import db

from keyboards_hr import get_hr_keyboard, get_cancel_keyboard, get_coupons_management_keyboard

router = Router()


# ===== КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ КУПОНАМИ =====

@router.message(F.text == "🎫 Управление купонами")
async def manage_coupons(message: Message):
    """Главное меню управления купонами"""
    await message.answer(
        "🎫 <b>Управление партнерскими купонами</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_coupons_management_keyboard()
    )


@router.message(F.text == "🔙 Назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    """Вернуться в главное меню"""
    await state.clear()
    await message.answer("🔙 Назад",

    reply_markup=get_hr_keyboard()
    )


@router.message(F.text == "📊 Статус купонов")
async def coupons_status(message: Message):
    """Показать статус всех купонов"""
    try:
        coupons = await db.get_all_coupons()

        if not coupons:
            await message.answer("❌ Нет активных купонов")
            return

        response = "📊 <b>Статус купонов:</b>\n\n"

        for coupon in coupons:
            status_emoji = "🟢" if coupon['remaining_quantity'] > 10 else "🟡" if coupon['remaining_quantity'] > 0 else "🔴"
            percent = (coupon['remaining_quantity'] / coupon['total_quantity']) * 100 if coupon['total_quantity'] > 0 else 0
            response += f"{status_emoji} <b>{coupon['partner_name']}</b> - {coupon['coupon_name']}\n"
            response += f"   Осталось: {coupon['remaining_quantity']}/{coupon['total_quantity']} ({percent:.1f}%)\n\n"

        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(F.text == "📋 Список купонов")
async def coupons_list(message: Message):
    """Показать полный список купонов"""
    try:
        coupons = await db.get_all_coupons()

        if not coupons:
            await message.answer("❌ Нет купонов в базе")
            return

        response = "📋 <b>Все купоны:</b>\n\n"

        for coupon in coupons:
            status = "🟢 Активен" if coupon['is_active'] else "🔴 Неактивен"
            response += f"ID: {coupon['id']}\n"
            response += f"🏪 <b>{coupon['partner_name']}</b> - {coupon['coupon_name']}\n"
            response += f"📝 {coupon['description']}\n"
            response += f"💰 Стоимость: {coupon['xp_cost']} XP\n"
            response += f"📦 Осталось: {coupon['remaining_quantity']}/{coupon['total_quantity']}\n"
            response += f"📊 Статус: {status}\n"
            response += "─" * 30 + "\n\n"

        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(F.text == "➕ Добавить купоны")
async def add_coupons_start(message: Message, state: FSMContext):
    """Начать процесс добавления купонов"""
    await message.answer(
        "Введите ID купона и количество через пробел:\n"
        "Например: <code>5 10</code> - добавить 10 купонов к ID 5\n"
        "Максимальное количество не изменится!\n\n"
        "Или введите ❌ Отмена для выхода",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(CouponState.add_quantity)


@router.message(CouponState.add_quantity, F.text)
async def add_coupons_process(message: Message, state: FSMContext):
    """Обработка добавления купонов"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_coupons_management_keyboard())
        return

    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Неверный формат")

        coupon_id = int(parts[0])
        quantity = int(parts[1])

        if quantity <= 0:
            await message.answer("❌ Количество должно быть больше 0")
            return

        # Получаем текущее состояние купона
        coupon = await db.get_coupon(coupon_id)
        if not coupon:
            await message.answer("❌ Купон с таким ID не найден")
            return

        # Проверяем, не превысит ли новое количество максимальное
        new_quantity = coupon['remaining_quantity'] + quantity
        if new_quantity > coupon['total_quantity']:
            await message.answer(
                f"❌ Нельзя добавить больше {coupon['total_quantity'] - coupon['remaining_quantity']} купонов\n"
                f"Максимальное количество: {coupon['total_quantity']}"
            )
            return

        result = await db.increase_coupon_quantity(coupon_id, quantity)

        if not result:
            await message.answer("❌ Ошибка при добавлении купонов")
            return

        coupon = await db.get_coupon(coupon_id)

        await message.answer(
            f"✅ Успешно добавлено {quantity} купонов\n"
            f"🏪 {coupon['partner_name']} - {coupon['coupon_name']}\n"
            f"📦 Теперь: {result['remaining_quantity']}/{coupon['total_quantity']}\n"
            f"📊 Максимум: {coupon['total_quantity']}",
            reply_markup=get_coupons_management_keyboard()
        )

        await state.clear()

    except ValueError:
        await message.answer("❌ Неверный формат. Пример: <code>5 10</code>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(F.text == "➖ Уменьшить купоны")
async def decrease_coupons_start(message: Message, state: FSMContext):
    """Начать процесс уменьшения купонов"""
    await message.answer(
        "Введите ID купона и количество через пробел:\n"
        "Например: <code>5 5</code> - уменьшить на 5 купонов ID 5\n"
        "Максимальное количество останется прежним!\n\n"
        "Или введите ❌ Отмена для выхода",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(CouponState.decrease_quantity)


@router.message(CouponState.decrease_quantity, F.text)
async def decrease_coupons_process(message: Message, state: FSMContext):
    """Обработка уменьшения купонов"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_coupons_management_keyboard())
        return

    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Неверный формат")

        coupon_id = int(parts[0])
        quantity = int(parts[1])

        if quantity <= 0:
            await message.answer("❌ Количество должно быть больше 0")
            return

        result = await db.decrease_coupon_quantity(coupon_id, quantity)

        if not result:
            await message.answer("❌ Недостаточно купонов или купон не найден")
            return

        coupon = await db.get_coupon(coupon_id)

        await message.answer(
            f"✅ Успешно уменьшено на {quantity} купонов\n"
            f"🏪 {coupon['partner_name']} - {coupon['coupon_name']}\n"
            f"📦 Осталось: {result['remaining_quantity']}/{coupon['total_quantity']}\n"
            f"📊 Максимум: {coupon['total_quantity']}",
            reply_markup=get_coupons_management_keyboard()
        )

        await state.clear()

    except ValueError:
        await message.answer("❌ Неверный формат. Пример: <code>5 5</code>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(Command("set_coupon"))
async def set_coupon_command(message: Message):
    """Установить точное количество купонов"""
    text = message.text.split()
    if len(text) != 3:
        await message.answer(
            "Использование: /set_coupon <id> <количество>\n"
            "Пример: /set_coupon 5 25 - установить 25 купонов для ID 5\n"
            "Не может превышать максимальное количество!"
        )
        return

    try:
        coupon_id = int(text[1])
        quantity = int(text[2])

        if quantity < 0:
            await message.answer("❌ Количество не может быть отрицательным")
            return

        result = await db.set_coupon_quantity(coupon_id, quantity)

        if not result:
            await message.answer("❌ Купон не найден")
            return

        coupon = await db.get_coupon(coupon_id)

        await message.answer(
            f"✅ Установлено количество: {quantity}\n"
            f"🏪 {coupon['partner_name']} - {coupon['coupon_name']}\n"
            f"📦 Теперь: {result['remaining_quantity']}/{coupon['total_quantity']}\n"
            f"📊 Максимум: {coupon['total_quantity']}",
            reply_markup=get_coupons_management_keyboard()
        )

    except ValueError:
        await message.answer("❌ Неверный формат чисел")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(F.text == "🆕 Создать купон")
async def create_coupon_start(message: Message, state: FSMContext):
    """Начать процесс создания купона"""
    await message.answer(
        "🎫 <b>Создание нового купона</b>\n\n"
        "Введите название партнера (например: OZON, DNS, ЛитРес):",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(CouponState.create_coupon_partner)


@router.message(CouponState.create_coupon_partner, F.text)
async def process_coupon_partner(message: Message, state: FSMContext):
    """Обработка названия партнера"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_coupons_management_keyboard())
        return

    await state.update_data(partner_name=message.text)

    await message.answer(
        "📝 Теперь введите название купона (например: Подарочный сертификат 500₽):",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(CouponState.create_coupon_name)


@router.message(CouponState.create_coupon_name, F.text)
async def process_coupon_name(message: Message, state: FSMContext):
    """Обработка названия купона"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_coupons_management_keyboard())
        return

    await state.update_data(coupon_name=message.text)

    await message.answer(
        "📄 Теперь введите описание купона:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(CouponState.create_coupon_description)


@router.message(CouponState.create_coupon_description, F.text)
async def process_coupon_description(message: Message, state: FSMContext):
    """Обработка описания купона"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_coupons_management_keyboard())
        return

    await state.update_data(description=message.text)

    await message.answer(
        "💰 Теперь введите стоимость купона в XP:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(CouponState.create_coupon_xp_cost)


@router.message(CouponState.create_coupon_xp_cost, F.text)
async def process_coupon_xp_cost(message: Message, state: FSMContext):
    """Обработка стоимости купона"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_coupons_management_keyboard())
        return

    try:
        xp_cost = int(message.text)
        if xp_cost <= 0:
            await message.answer("❌ Стоимость должна быть положительной")
            return

        await state.update_data(xp_cost=xp_cost)

        await message.answer(
            "📦 Теперь введите количество купонов (по умолчанию 100):",
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(CouponState.create_coupon_quantity)

    except ValueError:
        await message.answer("❌ Введите число")


@router.message(CouponState.create_coupon_quantity, F.text)
async def process_coupon_quantity(message: Message, state: FSMContext):
    """Обработка количества купонов"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_coupons_management_keyboard())
        return

    data = await state.get_data()

    try:
        quantity = int(message.text) if message.text.strip() else 100
        if quantity <= 0:
            await message.answer("❌ Количество должно быть положительным")
            return

        # Создаем купон
        coupon_id, error = await db.create_coupon(
            data['partner_name'],
            data['coupon_name'],
            data['description'],
            data['xp_cost'],
            quantity
        )

        if error:
            await message.answer(f"❌ {error}", reply_markup=get_coupons_management_keyboard())
            await state.clear()
            return

        await message.answer(
            f"✅ <b>Купон успешно создан!</b>\n\n"
            f"🏪 <b>Партнер:</b> {data['partner_name']}\n"
            f"🎫 <b>Название:</b> {data['coupon_name']}\n"
            f"📝 <b>Описание:</b> {data['description']}\n"
            f"💰 <b>Стоимость:</b> {data['xp_cost']} XP\n"
            f"📦 <b>Количество:</b> {quantity}\n"
            f"🆔 <b>ID купона:</b> {coupon_id}",
            parse_mode="HTML",
            reply_markup=get_coupons_management_keyboard()
        )

        await state.clear()

    except ValueError:
        await message.answer("❌ Введите число")


@router.message(F.text == "🗑️ Удалить купон")
async def delete_coupon_start(message: Message, state: FSMContext):
    """Начать процесс удаления купона"""
    await message.answer(
        "🗑️ <b>Удаление купона</b>\n\n"
        "Введите ID купона для удаления:",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(CouponState.delete_coupon)


@router.message(CouponState.delete_coupon, F.text)
async def process_delete_coupon(message: Message, state: FSMContext):
    """Обработка удаления купона"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено", reply_markup=get_coupons_management_keyboard())
        return

    try:
        coupon_id = int(message.text)

        # Получаем информацию о купоне
        coupon = await db.get_coupon(coupon_id)
        if not coupon:
            await message.answer("❌ Купон с таким ID не найден", reply_markup=get_coupons_management_keyboard())
            await state.clear()
            return

        # Удаляем купон
        success, error = await db.delete_coupon(coupon_id)

        if error:
            await message.answer(f"❌ {error}", reply_markup=get_coupons_management_keyboard())
        else:
            await message.answer(
                f"✅ <b>Купон успешно удален!</b>\n\n"
                f"🏪 {coupon['partner_name']} - {coupon['coupon_name']}\n"
                f"🆔 ID: {coupon_id}",
                parse_mode="HTML",
                reply_markup=get_coupons_management_keyboard()
            )

        await state.clear()

    except ValueError:
        await message.answer("❌ Введите числовой ID купона")