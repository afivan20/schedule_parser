from dotenv import dotenv_values

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import aiohttp
import pathlib
import os


DIR = pathlib.Path(__file__).parent.parent.resolve()
env = dotenv_values(os.path.join(DIR, '.env'))
distance_learning_uid = env['distance_learning_uid']


async def fetch_uchi_ru(next_week=0):
    today = datetime.utcnow().today()
    monday = (today - timedelta(days=(today.weekday()+1))).date()+timedelta(days=next_week)
    url = f'http://app.doma.uchi.ru/api/v1/teacher/calendar_events?start_date={monday}'
    cookies={"distance_learning_uid":distance_learning_uid}
    async with aiohttp.ClientSession() as session:
        async with session.get(url ,ssl=False, cookies=cookies) as response:
            data = await response.json()
    return data['calendar_events']


async def extract_uchi_ru(week=False, next_week=0):
    result = []
    data = await fetch_uchi_ru(next_week)
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


