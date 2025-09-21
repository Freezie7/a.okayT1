import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config_hr
from handlers_hr.start_hr import router as start_router  # Добавляем импорт
from handlers_hr.vacancies_hr import router as vacancies_router
from handlers_hr.search import router as search_router
from handlers_hr.analytics import router as analytics_router
from handlers_hr.coupons import router as coupons_router

async def on_startup():
    print("✅ HR-БОТ УСПЕШНО ЗАПУЩЕН")
    print("🤵 HR-панель готова к работе!")

async def main():
    bot = Bot(token=config_hr.HR_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем все роутеры (start должен быть первым!)
    routers = [
        start_router,      # Добавляем start роутер
        vacancies_router,
        search_router, 
        analytics_router,
        coupons_router
    ]
    
    for router in routers:
        dp.include_router(router)
    
    dp.startup.register(on_startup)
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())