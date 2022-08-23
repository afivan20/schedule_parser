from yandex import parse_yandex
from excel import parse_excel
from allright import parse_allright
from datetime import datetime, timedelta
from bot import send_message



try:
    excel = parse_excel()
except Exception as e:
    send_message(text=f'excel-error: {e}')
    excel = []

try:
    yandex = parse_yandex()
except Exception as e:
    send_message(text=f'yandex-error: {e}')
    yandex = []

try:
    allright = parse_allright()
except Exception as e:
    send_message(text=f'allright-error: {e}')
    allright = []

schedule = yandex + allright + excel
schedule.sort()

text = ''
for lesson in schedule:
    timestamp = lesson[0]
    student = lesson[1]
    utc = datetime.utcfromtimestamp(timestamp)
    Moscow_time = (utc + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
    text += f'{Moscow_time} {student}\n'
send_message(text=text)