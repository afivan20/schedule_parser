from yandex import parse_yandex
from excel import parse_excel
from allright import parse_allright
from datetime import datetime, timedelta
from bot import send_message


excel = parse_excel()
yandex = parse_yandex()
allright = parse_allright()


schedule = [*excel, *allright, *yandex]
schedule.sort()

text = ''
for lesson in schedule:
    timestamp = lesson[0]
    student = lesson[1]
    utc = datetime.utcfromtimestamp(timestamp)
    Moscow_time = (utc + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
    text += f'{Moscow_time} {student}\n'
send_message(text=text)