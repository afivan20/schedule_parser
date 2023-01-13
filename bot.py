from dotenv import dotenv_values
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, MessageHandler, ApplicationBuilder, ContextTypes, filters
import pytz

import asyncio
import logging
from datetime import datetime, timedelta, time
import pathlib
import os

from APIs.uchi_doma import extract_uchi_doma
from APIs.yandex import extract_yandex
from APIs.allright import extract_allright
from APIs.asyncio_excel import  main


logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", datefmt='%b-%d-%Y %H:%M:%S %p', level=logging.INFO)
logger = logging.getLogger('bot.py')

DIR = pathlib.Path(__file__).parent.resolve()
env = dotenv_values(os.path.join(DIR, '.env'))
BANK = env['BANK']
ME = int(env['chat_id'])
token = env['BOT_TOKEN']

application = ApplicationBuilder().token(token).build()


CONTACTS = {}


def output(data: list) -> str:
    data.sort()
    if data != []:
        text = ''
        weekday = ''
        for lesson in data:
            timestamp = lesson[0]
            student = lesson[1]
            utc = datetime.utcfromtimestamp(timestamp)
            Moscow_time = (utc + timedelta(hours=3)).strftime('<b>%H:%M</b> %a %d-%m')
            
            # визуально разбить по дням неделям
            if weekday == '' or weekday != utc.strftime('%A'):
                weekday = utc.strftime('%A')
                text += f'\n<b>{weekday}</b>\n'+'-'*25+'\n'

            text += f'{Moscow_time} {student}\n'

        total=len(data)
        text += f'\n<b>TOTAL: {total}</b>'
        return text
    else:
        return 'Ничего не найдено.'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    button = KeyboardButton('Отправить телефон ✅', request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await context.bot.send_message(chat_id=chat.id, reply_markup=reply_markup,
                             text='Чтобы продолжить, нажмине на кнопу отправить телефон 👇')
    



async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    all_data: list[list] = await asyncio.gather(extract_uchi_doma(), extract_yandex(), main(), extract_allright()) 
    all_data: list = sum(all_data, []) # сложить все списки
    text = output(all_data)
    await context.bot.send_message(chat_id=update.message.chat.id, parse_mode ='HTML', text=text)


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    all_week = True
    all_data: list[list] = await asyncio.gather(extract_uchi_doma(all_week), extract_yandex(all_week), main(all_week), extract_allright(all_week)) 
    all_data: list = sum(all_data, [])
    text = output(all_data)
    await context.bot.send_message(chat_id=update.message.chat.id, parse_mode ='HTML', text=text)


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    CONTACTS[contact.user_id] = {"first_name": contact.first_name, "phone_number": contact.phone_number}
    logger.warning(f'Добавлен новый пользователь #{contact.user_id}: {CONTACTS[contact.user_id]}')
    menu = ReplyKeyboardMarkup([['правила', 'реквизиты для оплаты']], resize_keyboard=True, one_time_keyboard=True)
    await context.bot.send_message(chat_id=contact.user_id, reply_markup=menu, parse_mode='Markdown', text='Что вас интересует: ***правила*** или ***реквизиты для оплаты***?')


async def request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    if not chat_id in CONTACTS:
        await start(update, context)
        return
    if update.message.text == 'правила':
        with open(f"{os.path.join(DIR, 'static/rules.pdf')}", "rb") as file:
            logger.warning(f'Запрос правил от {update.message.chat.id}: {CONTACTS[update.message.chat.id]}')
            await context.bot.send_document(chat_id=chat_id, document=file, filename='Правила.pdf')
    elif update.message.text == 'реквизиты для оплаты':
        logger.warning(f'Запрос реквизитов от {update.message.chat.id}: {CONTACTS[update.message.chat.id]}')
        await context.bot.send_message(chat_id=chat_id, text=BANK)
    else:
        return


async def notify_everyday(context: ContextTypes.DEFAULT_TYPE):
    all_data: list[list] = await asyncio.gather(extract_uchi_doma(), extract_yandex(), main(), extract_allright()) 
    all_data: list = sum(all_data, []) # сложить все списки
    text = output(all_data)
    await context.bot.send_message(chat_id=ME, parse_mode ='HTML', text=text)

start_handler = CommandHandler('start', start)
today_handler = CommandHandler('today', today, block=False, filters=filters.User(user_id=ME))
week_handler = CommandHandler('week', week, block=False, filters=filters.User(user_id=ME))
contact_handler = MessageHandler(filters.CONTACT, contact)
text_handler =  MessageHandler(filters.Text(['правила', 'реквизиты для оплаты']), request)


if __name__ == '__main__':
    application.add_handler(start_handler)
    application.add_handler(today_handler)
    application.add_handler(week_handler)
    application.add_handler(contact_handler)
    application.add_handler(text_handler)

    job_queue = application.job_queue
    job_minute = job_queue.run_daily(notify_everyday, time=time(8,00, tzinfo=pytz.timezone('Europe/Moscow')))

    application.run_polling()

