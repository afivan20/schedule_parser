import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
BOT = Bot(TOKEN)
ME=os.getenv("chat_id")

def send_message(text):
    BOT.send_message(chat_id=ME, text=text, parse_mode = 'HTML')