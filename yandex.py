import requests
import datetime
from bot import send_message
from dotenv import dotenv_values
import pathlib
import os


DIR = pathlib.Path(__file__).parent.resolve()
env = dotenv_values(os.path.join(DIR, '.env'))
secret1 = env['Session_id']
secret2 = env['sessionid2']
secret3 = env['english.auth-token']


headers = {
    'cookie': f'Session_id={secret1} sessionid2={secret2} english.auth-token={secret3}',
    }

def lessons_data(delta):
    utc = datetime.datetime.utcnow()
    start = int(datetime.datetime.timestamp(utc))
    end = int(datetime.datetime.timestamp(utc+datetime.timedelta(days=delta)))
    url = f'https://practicum.yandex.ru/flow/api/tutor/speaking-sessions?from={start}&to={end}'
    r = requests.get(url, headers=headers)
    data = r.json()
    return data


def parse_yandex(delta=1):
    data = lessons_data(delta)
    result=[]
    for lesson in data['data']['speaking_sessions']:
        if lesson['state']=='scheduled':
            date = lesson['start_at']
            time = date
            name = lesson['student']['public_name']
            result.append((time, name))
    return result
