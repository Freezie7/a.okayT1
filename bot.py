import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.view_profile import router as view_profile_router
from handlers.skills import router as skills_router
from handlers.main_commands import router as main_router  # Добавляем новый роутер
from handlers.career import router as career_router
from handlers.vacancies import router as vacancies_router
from handlers.coupons import router as coupons_router
from database import db

async def on_startup():
    print("✅ БОТ УСПЕШНО ЗАПУЩЕН")

async def main():
    await db.init_coupons_table()
    bot = Bot(token=config.TOKEN_BOT)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем все роутеры
    routers = [
        start_router,
        profile_router, 
        view_profile_router,
        skills_router,
        career_router,
        vacancies_router,  # Должен быть здесь!
        main_router,
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