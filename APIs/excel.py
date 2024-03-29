import gspread_asyncio
from gspread_asyncio import AsyncioGspreadClientManager, AsyncioGspreadWorksheet
from google.oauth2.service_account import Credentials

import asyncio
from datetime import datetime, timedelta
import pathlib
import os
from util import async_timed, async_timeout
# номер колонки на странице Excel
DAY = {
    'Monday':1,
    'Tuesday':2,
    'Wednesday':3,
    'Thursday':4,
    'Friday':5,
    'Saturday':6,
    'Sunday':7
    }
TEMP_WORKSHEET = None

def get_creds():
    DIR = pathlib.Path(__file__).parent.parent.resolve()
    creds = Credentials.from_service_account_file(os.path.join(DIR, ".schedule-api-360016-0ff068011fd8.json"))
    scoped = creds.with_scopes(["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    return scoped



async def get_worksheet(agcm: AsyncioGspreadClientManager, sheet_name: str, worksheet_name: str):
    agc = await agcm.authorize()
    sheet = await agc.open(sheet_name)
    worksheet = await sheet.worksheet(worksheet_name)
    return worksheet

async def extract_excel(worksheet: AsyncioGspreadWorksheet, all_week=False, next_week=0):
    data: list[list] = await worksheet.batch_get([f"{col}2:{col}30"for col in ('ABCDEFGH')]) # get all data from columns A-H
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())+timedelta(days=next_week) # Monday yyy-mm-dd
    week_of_day = 1 if all_week else DAY[datetime.now().date().strftime('%A')]

    result = []
    while week_of_day <= 7:
        for i, row in enumerate(data[week_of_day]): # iterate by column's rows (итерируемся по строкам в столбце)
            if row: # name of the student
                lesson_time = data[0][i][0] # get time from first column (TIME)
                
                day = monday+(timedelta(days=week_of_day-1))
                dt = datetime.strptime(f'{day}T{lesson_time}', '%Y-%m-%dT%H:%M')
                unix_time =  int(datetime.timestamp(dt))
                result.append((unix_time, *row))
        week_of_day += 1
        if not all_week: break
    return result

@async_timed()
@async_timeout(5)
async def asyncio_excel(week=False, next_week=0):
    global TEMP_WORKSHEET
    if TEMP_WORKSHEET is None:
        agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds) # ClientManger gets credentials
        worksheet =  await asyncio.create_task(get_worksheet(agcm, "schedule", "Расписание")) # get the worksheet
        TEMP_WORKSHEET = worksheet # save worksheet, to reuse quicker
    extracted_data = await extract_excel(TEMP_WORKSHEET, week, next_week)
    return extracted_data



