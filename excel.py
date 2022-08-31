import gspread
from datetime import datetime, timedelta
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


def extract_data(worksheet, column, day):
    result = []
    for i, line in enumerate(column, start=1):
        if i == 1: continue
        if line != '':
            time = worksheet.acell(f'A{i}').value
            dt = datetime.strptime(f'{day}T{time}', '%Y-%m-%dT%H:%M')
            unix_time =  int(datetime.timestamp(dt))
            student = line
            result.append((unix_time, student))
    return result

def get_excel(week=False):
    
    worksheet = connect_excel()
    today = datetime.now().date()
    weekday = today.strftime('%A')

    if week:
        monday = today - timedelta(days=today.weekday()) # Monday yyy-mm-dd
        result = []
        for i, column_number in enumerate(DAY.values()):
            column = worksheet.col_values(column_number)
            day = monday+(timedelta(days=i))
            result += extract_data(worksheet, column, day )

    else:
        column = worksheet.col_values(DAY[weekday])
        result = extract_data(worksheet, column, today)

    return result


