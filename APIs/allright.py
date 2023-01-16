from dotenv import dotenv_values

from datetime import datetime, timedelta, timezone, time
import aiohttp
import pathlib
import os


DIR = pathlib.Path(__file__).parent.parent.resolve()
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


async def get_token_allright(url: str, headers: dict, payload: dict, session: aiohttp.ClientSession):
    async with session.post(url, data=payload, headers=headers, ssl=False) as r:
        j = await r.json()
    return j['access_token']


async def fetch_allright(week=False, next_week=0):
    start = datetime.now().date()
    end = start
    if week:
        today = datetime.utcnow().today() + timedelta(days=next_week)
        monday = (today - timedelta(days=(today.weekday()+1))).date()
        start = monday 
        end = start + timedelta(days=7)
    print(end)
    url = f'https://allright.com/api/v1/lessons?filter[user_id]={me}&filter[from]={start}T21:00:00.000Z&filter[to]={end}T21:00:00.000Z'
    async with aiohttp.ClientSession() as session:
        token_allright = await get_token_allright(TOKEN_URL, HEADERS, PAYLOAD, session)
        async with session.get(
            url,
            ssl=False,
            headers={'authorization': f'Bearer {token_allright}'}) as response:
            lessons = await response.json()
    return lessons


async def extract_allright(week=False, next_week=0):
    data = await fetch_allright(week, next_week)
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
