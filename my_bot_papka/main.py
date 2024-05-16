""" импорт asyncio """
import asyncio
from aiogram import Bot, Dispatcher
from handlers import include_router
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    """ подключение роутеров и запуск бота """
    include_router(dp)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
