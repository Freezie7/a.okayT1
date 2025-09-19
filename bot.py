import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Хранилище состояний в памяти

import config
from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.view_profile import router as view_profile_router

async def on_startup():
    print("✅ БОТ УСПЕШНО ЗАПУЩЕН")

async def main():
    bot = Bot(token=config.TOKEN_BOT)
    dp = Dispatcher(storage=MemoryStorage())  # Добавляем хранилище для FSM
    
    # Подключаем роутеры (обработчики)
    routers = [start_router, profile_router, view_profile_router]
    for router in routers:
        dp.include_router(router)
    
    dp.startup.register(on_startup)
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())