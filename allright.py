from datetime import datetime
import requests
from bot import send_message
from dotenv import dotenv_values

env = dotenv_values('.env')
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
    'scope': 'login-form',
    'client_id': 'fronendClient'
    }


def token(url, headers, payload):
    session = requests.Session()
    r = session.post(url, headers=headers, data=payload)
    j = r.json()
    return j['access_token']


def lessons():
    today = datetime.now().strftime('%Y-%m-%d')
    url = f'https://allright.com/api/v1/lessons?filter[user_id]={me}&filter[upcomming][start]={today}'
    response = requests.get(
        url,
        headers={
        'authorization': f'Bearer {token(TOKEN_URL, HEADERS, PAYLOAD)}',
        'User-Agent': user_agent
        }
    )
    lessons = response.json()
    return lessons


def schedule(data):
    result = []
    for item in data['data']:
        time = item['attributes']['time-start']

        # только сегодняшние занятия
        if datetime.today().strftime('%Y-%m-%d') == time[:10]:
            
            # используя родительский id найти имя ребенка
            parent_id = item['attributes']['student-id']
            for item in data['included']:
                if int(item['id']) == parent_id:
                    student_id = item['relationships']['user-metum']['data']['id']
                    for i in data['included']:
                        if student_id == i['id']:
                            name = i['attributes']['child-name']
                            result.append((name, time[:16]))
    return result           

def parse_allright():
    data = lessons()
    result = schedule(data)
    send_message(f'allright - {result}')

if __name__ == '__main__':
    parse_allright()
