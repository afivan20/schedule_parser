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

def lessons_data():
    now = datetime.datetime.now()
    start = int(datetime.datetime.timestamp(now))
    end = int(datetime.datetime.timestamp(now+datetime.timedelta(hours=15)))
    url = f'https://practicum.yandex.ru/flow/api/tutor/speaking-sessions?from={start}&to={end}'
    r = requests.get(url, headers=headers)
    data = r.json()
    return data


def parse_data():
    data = lessons_data()
    result=[]
    for lesson in data['data']['speaking_sessions']:
        if lesson['state']=='scheduled':
            date = (datetime.datetime.utcfromtimestamp(lesson['start_at'])+datetime.timedelta(hours=3)).strftime('%H:%M')
            time = date
            name = lesson['student']['public_name']
            result.append((name, time))
    return result

def yandex_run():
    result = parse_data()
    send_message(f'Yandex - {result}')

if __name__ == '__main__':
    yandex_run()