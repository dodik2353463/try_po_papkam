from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import asyncio

import keyboards.anketa as kbss
import states.anketa as state_user

from datetime import datetime

from database.database import *
import database.take_info as take_info

router_start = Router()

start_txt = 'Привет!\nЭто бот подарит тебе настроение, рассказав о сегодяншнем празднике.'

@router_start.message(F.text.lower().in_({'задать время рассылки', '/set_time'}))
async def set_settings_rassilka(message: Message, state: FSMContext):
    await message.answer('Отправьте время в формате ЧЧ:ММ')
    await state.set_state(state_user.User.time)

@router_start.message(state_user.User.time)
async def set_time(message: Message, state: FSMContext):
    if message.content_type != 'text':
        await message.answer('Вы должны ввести сообщение. Попробуйте еще раз')
        return
    
    if ':' not in message.text:
        await message.answer('Введенное время должно содержать двоеточие (:)')
        return
    hours, minute = str(message.text).split(':')
    if not(hours.isdigit()) or not(minute.isdigit()):
        await message.answer('Час и минута - целые числа')
        return
    if len(hours) != 2 or len(minute) != 2:
        await message.answer('Час и минута должны состоять из двух цифр')
        return
    
    elif not(0 <= int(hours) <= 23):
        await message.answer('Неправильно указан час')
        return
    elif not(0 <= int(minute) <= 59):
        await message.answer('Неправильно указана минута')
        return
    
    #FileClass.get_or_none(user_id_tg=message.from_user.id)
    if FileClass.get_or_none(user_id_tg=message.from_user.id) == None:
        FileClass.create(user_id_tg=message.from_user.id, time=datetime.time(hours, minute))
    else:
        user = FileClass.get(user_id_tg=message.from_user.id)
        user.time =  datetime.time(hours, minute)
        user.save()
    
    await message.answer(f'Установлено время рассылки на {hours}:{minute}')
    await state.clear()

async def get_time_notify():
    """Получить время ближайшей рассылки"""
    now = datetime.now()
    users = FileClass.filter(FileClass.time > now).order_by(FileClass.time.asc())
    if users.count() > 0:
        return users.first()

async def send_admin():
    """Параллельный процесс для рассылки сообщений"""
    from  import get_bot
    bot = get_bot()
    send_time, send_id = await get_time_notify()
    await bot.send_message(send_id, "Бот запущен!")
    while True:
        print(datetime.now().time(), send_time)
        now_time = datetime.now().time()
        now_time = datetime.time(now_time.hour, now_time.minute)
        if send_time and send_time == now_time:
            # рассылка уведомлений всем пользователям
            for user in FileClass.filter(time=send_time):
                await bot.send_message(user.tg_user, 'ping')

            send_time = await get_time_notify()
            print(send_time)


        now_time = (datetime.datetime.now() + datetime.timedelta(minutes=1))
        now_time = datetime.datetime(now_time.year, now_time.month, now_time.day,
                            now_time.hour, now_time.minute)
        seconds = (now_time - datetime.now()).seconds + 1
        print(datetime.datetime.now().time(), now_time.time(), seconds)
        await asyncio.sleep(seconds)


async def on_startup():
    """Обертка для запуска параллельного процесса"""
    asyncio.create_task(send_admin())
