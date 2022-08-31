import requests
import datetime
from dotenv import dotenv_values
import pathlib
import os
import time as t


DIR = pathlib.Path(__file__).parent.resolve()
env = dotenv_values(os.path.join(DIR, '.env'))
secret1 = env['Session_id']
secret2 = env['sessionid2']
secret3 = env['english.auth-token']


headers = {
    'cookie': f'Session_id={secret1} sessionid2={secret2} english.auth-token={secret3}',
    }

def yandex_lessons(week=False):
    today = datetime.datetime.utcnow().today()
    start = int(t.mktime(today.date().timetuple())) # сегодня unix time
    end = start + 86400
    if week:
        monday = (today - datetime.timedelta(days=(today.weekday()+1))).date() # понедельник
        start = int(t.mktime(monday.timetuple()))
        end = start + 604800
    url = f'https://practicum.yandex.ru/flow/api/tutor/speaking-sessions?from={start}&to={end}'
    r = requests.get(url, headers=headers)
    data = r.json()
    return data


def get_yandex(data):
    result=[]
    for lesson in data['data']['speaking_sessions']:
        if lesson['state']=='scheduled':
            date = lesson['start_at']
            time = date
            name = lesson['student']['public_name']
            result.append((time, name))
    return result

