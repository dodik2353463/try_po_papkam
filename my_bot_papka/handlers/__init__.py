""" Пакет с обработчиком событий """
from aiogram import Dispatcher

from handlers import anketa, start

def include_router(dp: Dispatcher):
    """ Подключает роутеры со всех модулей """
    dp.include_routers(
        start.router,
        anketa.router_start
    )
    dp.startup.register(anketa.on_startup)