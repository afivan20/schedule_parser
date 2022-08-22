import gspread
from datetime import date
import calendar
from bot import send_message

SHEET = 'schedule'
WORKSHEET = 'Расписание'
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
    sa = gspread.service_account(CREDENTIALS)
    sheet = sa.open(SHEET) 
    worksheet = sheet.worksheet(WORKSHEET)
    return worksheet


def parse_excel():
    worksheet = connect_excel()
    my_date = date.today()
    weekday=calendar.day_name[my_date.weekday()]
    today = worksheet.col_values(DAY[weekday])
    result = []
    for time, student in enumerate(today):
        if student != '' and student != weekday:
            result.append((worksheet.acell(f'A{time+1}').value, student))

    send_message(f'private - {result}')


if __name__ == '__main__':
    parse_excel()



