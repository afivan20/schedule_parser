from datetime import datetime, timedelta, timezone
import requests
from dotenv import dotenv_values
import pathlib
import os


DIR = pathlib.Path(__file__).parent.resolve()
env = dotenv_values(os.path.join(DIR, '.env'))
password = env['password']
auth = env['authorization']
login = env['email']
user_agent = env['user_agent']
me = env['me']


TOKEN_URL = 'https://allright.com/oauth/token'
HEADERS = {
    'authorization': auth,
    'User-Agent': user_agent
    }
PAYLOAD = {
    'grant_type': 'password',
    'username': login,
    'password': password,
    }


def token(url, headers, payload):
    session = requests.Session()
    r = session.post(url, headers=headers, data=payload)
    j = r.json()
    return j['access_token']


def allright_lessons(week=False):
    start = datetime.now().date()
    end = start + timedelta(days=2)
    if week:
        today = datetime.utcnow().today()
        monday = (today - timedelta(days=(today.weekday()+1))).date()
        start = monday
        end = start + timedelta(days=8)
    url = f'https://allright.com/api/v1/lessons?filter[user_id]={me}&filter[from]={start}&filter[to]={end}'
    response = requests.get(
        url,
        headers={
        'authorization': f'Bearer {token(TOKEN_URL, HEADERS, PAYLOAD)}',
        }
    )
    lessons = response.json()
    return lessons


def get_allright(data):
    result = []
    for item in data['data']:
        # только активные уроки (state=2)
        if item['attributes'].get('state') != 2:
            continue
        

        time = datetime.strptime(item['attributes']['time-start'], '%Y-%m-%dT%H:%M:%S.000Z')
        unix_time =  int(datetime.timestamp(time.replace(tzinfo=timezone.utc)))
        # используя родительский id найти имя ребенка
        try:
            parent_id = item['attributes']['student-id']
        except KeyError:
            continue
        for item in data['included']:
            if int(item['id']) == parent_id:
                student_id = item['relationships']['user-metum']['data']['id']
                for i in data['included']:
                    if student_id == i['id']:
                        name = i['attributes']['child-name']
                        result.append((unix_time, name))
    return result           
