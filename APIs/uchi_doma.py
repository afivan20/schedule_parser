from dotenv import dotenv_values

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import aiohttp
import pathlib
import os


DIR = pathlib.Path(__file__).parent.parent.resolve()
env = dotenv_values(os.path.join(DIR, '.env'))
distance_learning_uid = env['distance_learning_uid']


async def fetch_uchi_doma():
    today = datetime.utcnow().today()
    monday = (today - timedelta(days=(today.weekday()+1))).date()
    url = f'http://app.doma.uchi.ru/api/v1/teacher/calendar_events?start_date={monday}'
    cookies={"distance_learning_uid":distance_learning_uid}
    async with aiohttp.ClientSession() as session:
        async with session.get(url ,ssl=False, cookies=cookies) as response:
            data = await response.json()
    return data['calendar_events']

    
async def extract_uchi_doma(week=False):
    result = []
    data = await fetch_uchi_doma()
    for lesson in data:
        time = datetime.strptime(lesson['start_time'], '%Y-%m-%dT%H:%M:%S.000Z')
        unix_time =  int(datetime.timestamp(time.replace(tzinfo=timezone.utc)))
        name = lesson['course_node_name']
        if not week: # Если только за сегодняшний день
            today = datetime.now(tz=ZoneInfo('Europe/Moscow'))
            if not today.date() == time.date(): 
                continue
        result.append((unix_time, name))
    return result           


