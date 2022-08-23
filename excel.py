import gspread
from datetime import datetime, timedelta
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
    start = datetime.now()
    start_date = start.date()
    weekday=calendar.day_name[start_date.weekday()]
    column = worksheet.col_values(DAY[weekday])
    result = []
    for i, student in enumerate(column):
        if student != '' and student != weekday:
            time = worksheet.acell(f'A{i+1}').value
            dt = datetime.strptime(f'{start_date}T{time}', '%Y-%m-%dT%H:%M')
            if start <= dt:
                unix_time =  int(datetime.timestamp(dt))
                result.append((unix_time, student))   
    

   


    end = start+timedelta(hours=24)
    end_date = end.date()
    weekday=calendar.day_name[end_date.weekday()]
    column = worksheet.col_values(DAY[weekday])
    for i, student in enumerate(column):
        if student != '' and student != weekday:
            time = worksheet.acell(f'A{i+1}').value
            dt = datetime.strptime(f'{end_date}T{time}', '%Y-%m-%dT%H:%M')
            if start <= dt <= end:
                unix_time =  int(datetime.timestamp(dt))
                result.append((unix_time, student))

    return result
