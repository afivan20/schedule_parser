from dotenv import dotenv_values

import aiohttp
from aiohttp import ClientTimeout
import datetime
import pathlib
import os
from util import async_timed


DIR = pathlib.Path(__file__).parent.parent.resolve()
env = dotenv_values(os.path.join(DIR, '.env'))
secret = env['_app_session']


async def fetch_gb():
    headers = {'Cookie': f"_app_session={secret}"}
    url = 'https://gb.ru/api/v2/schedule'
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=3)) as session:
        async with session.get(url,ssl=False, headers=headers) as response:
            data = await response.json()
            return data['lessons']
        

@async_timed()
async def extract_gb(week=False, next_week=0):
    today = datetime.datetime.today().date()
    end = today
    if week:
        today = (today - datetime.timedelta(days=(today.weekday())))+datetime.timedelta(days=next_week) # понедельник
        end = today + datetime.timedelta(days=6)
    result=[]
    data = await fetch_gb()
    print(today, end)
    for lesson in data:
        
        start_lesson = datetime.datetime.fromisoformat(lesson['datetime'])

        if today <= start_lesson.date() <= end:
            unix_time =  int(datetime.datetime.timestamp(start_lesson))
            result.append((unix_time, lesson['title']))
    return result

