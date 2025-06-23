"""
Основной файл для запуска бота
"""
import asyncio

from aiogram.client.bot import Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram_sqlite_storage.sqlitestore import SQLStorage

from commands import ADMIN_COMMANDS
from dialogs.add_workout import router as add_workout_router

API_TOKEN = "7597769409:AAH2iFXOfr8aENH5Ea2CVos8k2wtd42CYW8"
bot = Bot(token=API_TOKEN)
storage = SQLStorage("database.db", serializing_method="pickle")
dp = Dispatcher(storage=storage)

# Регистрация хендлеров
dp.include_router(add_workout_router)


async def main():
    # TODO Инициализация базы данных
    # TODO Запуск планировщика
    await bot.delete_webhook(drop_pending_updates=True) # Накопленные сообщения во время неработы бота будут удалены
    await bot.set_my_commands(ADMIN_COMMANDS)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())