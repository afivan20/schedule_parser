import gspread
from datetime import datetime
import calendar
import pathlib
import os

SHEET = 'schedule'
WORKSHEET = 'Расписание'
DIR = pathlib.Path(__file__).parent.resolve()
CREDENTIALS = 'schedule-api-360016-0ff068011fd8.json'

# номер колонки на странице Excel
DAY = {
    'Monday':2,
    'Tuesday':3,
    'Wednesday':4,
    'Thursday':5,
    'Friday':6,
    'Saturday':7,
    'Sunday':8
    }

def connect_excel():
    sa = gspread.service_account(os.path.join(DIR, CREDENTIALS))
    sheet = sa.open(SHEET) 
    worksheet = sheet.worksheet(WORKSHEET)
    return worksheet


def parse_excel():
    worksheet = connect_excel()
    date = datetime.now().date()
    weekday=calendar.day_name[date.weekday()]
    today = worksheet.col_values(DAY[weekday])
    result = []
    for time, student in enumerate(today):
        if student != '' and student != weekday:
            time = worksheet.acell(f'A{time+1}').value
            dt = datetime.strptime(f'{date}T{time}', '%Y-%m-%dT%H:%M')
            unix_time =  int(datetime.timestamp(dt))
            result.append((unix_time, student))

    return result
