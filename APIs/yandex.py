from dotenv import dotenv_values

import aiohttp
import datetime
import pathlib
import os
import time as t


DIR = pathlib.Path(__file__).parent.parent.resolve()
env = dotenv_values(os.path.join(DIR, '.env'))
secret1 = env['Session_id']
secret2 = env['sessionid2']
secret3 = env['english.auth-token']


headers = {
    'cookie': f'Session_id={secret1} sessionid2={secret2} english.auth-token={secret3}',
    }

async def fetch_yandex(week: bool, next_week=0):
    today = datetime.datetime.utcnow().today()
    start = int(t.mktime(today.date().timetuple())) # сегодня unix time
    end = start + 86400
    if week:
        monday = (today - datetime.timedelta(days=(today.weekday()+1))).date()+datetime.timedelta(days=next_week) # понедельник
        start = int(t.mktime(monday.timetuple()))
        end = start + 604800
    url = f'https://practicum.yandex.ru/flow/api/tutor/speaking-sessions?from={start}&to={end}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url,ssl=False, headers=headers) as response:
            data = await response.json()
            return data['data']['speaking_sessions']


async def extract_yandex(week=False, next_week=0):
    result=[]
    data = await fetch_yandex(week, next_week)
    for lesson in data:
        if lesson['state']=='scheduled':
            date = lesson['start_at']
            time = date
            name = lesson['student']['public_name']
            result.append((time, name))
    return result



