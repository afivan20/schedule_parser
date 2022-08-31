from yandex import get_yandex, yandex_lessons
from excel import get_excel
from allright import get_allright, allright_lessons
from datetime import datetime, timedelta
from bot import send_message


def schedule(week=False):
    try:
        excel = get_excel(week)
    except Exception as e:
        excel = []
        send_message(text=f'excel-error: {e}')
        

    try:
        data = yandex_lessons(week)
        yandex = get_yandex(data)
    except Exception as e:
        yandex = []
        send_message(text=f'yandex-error: {e}')
        

    try:
        data = allright_lessons(week)
        allright = get_allright(data)
    except Exception as e:
        allright = []
        send_message(text=f'allright-error: {e}')
        
    data = yandex + allright + excel
    data.sort()

    if data != []:
        text = ''
        weekday = ''
        for lesson in data:
            timestamp = lesson[0]
            student = lesson[1]
            utc = datetime.utcfromtimestamp(timestamp)
            Moscow_time = (utc + timedelta(hours=3)).strftime('<b>%H:%M</b> %a %d-%m')
            
            # визуально разбить по дням неделям
            if weekday == '' or weekday != utc.strftime('%A'):
                weekday = utc.strftime('%A')
                text += f'\n<b>{weekday}</b>\n'+'-'*25+'\n'

            text += f'{Moscow_time} {student}\n'

        total=len(data)
        text += f'\n<b>TOTAL: {total}</b>'
        send_message(text=text)
    else:
        send_message(text='Ничего не найдено.')


