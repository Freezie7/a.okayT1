from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import logging
import sys
import os
from database import db
from keyboards.main_kb import get_main_keyboard

router = Router()
logger = logging.getLogger(__name__)


# ===== КОМАНДЫ ДЛЯ КУПОНОВ =====

@router.message(Command("coupons"))
async def cmd_coupons(message: Message):
    """Показать доступные купоны"""
    await show_available_coupons(message)


@router.message(F.text == "🎁 Магазин купонов")
async def coupons_shop_button(message: Message):
    """Обработчик кнопки магазина купонов"""
    await show_available_coupons(message)


async def show_available_coupons(message: Message):
    """Показать доступные для покупки купоны"""
    try:
        coupons = await db.get_available_coupons()

        if not coupons:
            await message.answer(
                "🎁 <b>Магазин купонов</b>\n\n"
                "На данный момент нет доступных купонов.\n"
                "Следите за обновлениями!",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            return

        # Получаем XP пользователя
        user_xp = await db.get_user_xp(message.from_user.id)
        if user_xp is None:
            user_xp = 0

        response = f"🎁 <b>Магазин купонов</b>\n\n"
        response += f"⭐ <b>Ваш XP:</b> {user_xp}\n\n"
        response += "<b>Доступные купоны:</b>\n\n"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        # Группируем купоны по партнерам
        partners = {}
        for coupon in coupons:
            if coupon['partner'] not in partners:
                partners[coupon['partner']] = []
            partners[coupon['partner']].append(coupon)

        for partner, partner_coupons in partners.items():
            response += f"🏪 <b>{partner}</b>\n"

            for coupon in partner_coupons:
                status = "🟢" if user_xp >= coupon['xp_cost'] else "🔴"
                response += f"{status} <b>{coupon['name']}</b> - {coupon['xp_cost']} XP\n"
                response += f"   {coupon['description']}\n"
                response += f"   Осталось: {coupon['remaining']} шт.\n\n"

                # Добавляем кнопку если достаточно XP
                if user_xp >= coupon['xp_cost']:
                    keyboard.inline_keyboard.append([
                        InlineKeyboardButton(
                            text=f"🎫 Купить {coupon['name']} - {coupon['xp_cost']} XP",
                            callback_data=f"buy_coupon_{coupon['id']}"
                        )
                    ])

        response += "👇 Выберите купон для покупки:"

        # Добавляем кнопку для просмотра своих купонов
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="📋 Мои купоны",
                callback_data="my_coupons"
            )
        ])

        await message.answer(response, parse_mode="HTML", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error in show_available_coupons: {e}")
        await message.answer("❌ Ошибка при загрузке купонов.")


@router.callback_query(F.data.startswith("buy_coupon_"))
async def process_buy_coupon(callback: CallbackQuery):
    """Обработчик покупки купона"""
    try:
        logger.info(f"Processing coupon purchase: {callback.data}")

        coupon_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id

        # Уведомляем пользователя о начале обработки
        await callback.answer("Обрабатываем покупку...")

        # Совершаем покупку
        result, error = await db.purchase_coupon(user_id, coupon_id)

        if error:
            await callback.message.answer(f"❌ {error}")
            return

        # Получаем информацию о купоне
        coupons = await db.get_available_coupons()
        purchased_coupon = next((c for c in coupons if c['id'] == coupon_id), None)

        if purchased_coupon:
            response = f"🎉 <b>Поздравляем с покупкой!</b>\n\n"
            response += f"🏪 <b>Партнер:</b> {purchased_coupon['partner']}\n"
            response += f"🎫 <b>Купон:</b> {purchased_coupon['name']}\n"
            response += f"📝 <b>Описание:</b> {purchased_coupon['description']}\n"
            response += f"💸 <b>Списано XP:</b> {result['xp_cost']}\n"
            response += f"⭐ <b>Осталось XP:</b> {result['remaining_xp']}\n\n"
            response += "💡 Для использования купона обратитесь в HR-отдел"

            await callback.message.answer(response, parse_mode="HTML")

        await callback.answer("✅ Купон успешно приобретен!")

    except Exception as e:
        logger.error(f"Error in process_buy_coupon: {e}")
        await callback.answer("❌ Ошибка при покупке купона.")


@router.callback_query(F.data == "my_coupons")
async def show_my_coupons(callback: CallbackQuery):
    """Показать купоны пользователя"""
    try:
        user_id = callback.from_user.id
        coupons = await db.get_user_coupons(user_id)

        if not coupons:
            await callback.message.answer(
                "У вас пока нет купонов 😢\n"
                "Посетите 🎁 Магазин купонов чтобы приобрести первый купон!",
                parse_mode="HTML"
            )
            await callback.answer()
            return

        response = "📋 <b>Ваши купоны:</b>\n\n"

        for coupon in coupons:
            status = "✅ Использован" if coupon['is_used'] else "🟢 Активен"
            response += f"🏪 <b>{coupon['partner']}</b>\n"
            response += f"🎫 <b>{coupon['name']}</b>\n"
            response += f"📝 {coupon['description']}\n"
            response += f"📅 Получен: {coupon['purchase_date'][:10]}\n"
            response += f"📊 Статус: {status}\n"

            if coupon['is_used'] and coupon['used_date']:
                response += f"📅 Использован: {coupon['used_date'][:10]}\n"

            response += "─" * 30 + "\n\n"

        response += "💡 Для использования купонов обратитесь в HR-отдел"

        await callback.message.answer(response, parse_mode="HTML")
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in show_my_coupons: {e}")
        await callback.message.answer("❌ Ошибка при загрузке ваших купонов.")
        await callback.answer()


# ===== КОМАНДА ДЛЯ ПРОСМОТРА СВОИХ КУПОНОВ =====

@router.message(Command("my_coupons"))
async def cmd_my_coupons(message: Message):
    """Показать купоны пользователя"""
    try:
        user_id = message.from_user.id
        coupons = await db.get_user_coupons(user_id)

        if not coupons:
            await message.answer(
                "У вас пока нет купонов 😢\n"
                "Посетите 🎁 Магазин купонов чтобы приобрести первый купон!",
                parse_mode="HTML"
            )
            return

        response = "📋 <b>Ваши купоны:</b>\n\n"

        for coupon in coupons:
            status = "✅ Использован" if coupon['is_used'] else "🟢 Активен"
            response += f"🏪 <b>{coupon['partner']}</b>\n"
            response += f"🎫 <b>{coupon['name']}</b>\n"
            response += f"📝 {coupon['description']}\n"
            response += f"📅 Получен: {coupon['purchase_date'][:10]}\n"
            response += f"📊 Статус: {status}\n"

            if coupon['is_used'] and coupon['used_date']:
                response += f"📅 Использован: {coupon['used_date'][:10]}\n"

            response += "─" * 30 + "\n\n"

        response += "💡 Для использования купонов обратитесь в HR-отдел"

        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in cmd_my_coupons: {e}")
        await message.answer("❌ Ошибка при загрузке ваших купонов.")