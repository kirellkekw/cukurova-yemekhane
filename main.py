from fastapi import FastAPI
import requests
import re
import jsonpickle
import uvicorn
import datetime

import asyncio

r = requests.get(url="https://yemekhane.cu.edu.tr/yemeklistejson.asp")
r.encoding = "ISO-8859-9"
r = re.sub(r'<meta .*>', '', r.text)

calendar = jsonpickle.decode(r)


async def refresh_food_list():
    global calendar

    """Purge files older than max_file_age defined in config.py from download_directory"""

    print("File purge subprocess started.")  # debug

    while True:
        await asyncio.sleep(60*60*24)  # check every day
        r = requests.get(url="https://yemekhane.cu.edu.tr/yemeklistejson.asp")
        r.encoding = "ISO-8859-9"
        r = re.sub(r'<meta .*>', '', r.text)

        calendar = jsonpickle.decode(r)


app = FastAPI()


@app.on_event("startup")  # run this function when the server starts
async def startup_event():
    """Creates sub-processes to run in the background when the server starts."""
    asyncio.create_task(refresh_food_list())


@app.get(path="/", description="Get root tree of the API.")
async def root():
    return calendar


@app.get(path="/day/{day}")
async def day(day: str):
    try:
        return calendar[day]
    except KeyError:
        return {"error": "No content for this date or meal."}


@app.get(path="/today", description="Get today's content. Will return error message if there is no content for today.")
async def today():
    today = datetime.date.today().strftime("%d.%m.%Y")
    try:
        return calendar[today]
    except KeyError:
        return {"error": "No content for today."}


@app.get(path="/tomorrow", description="Get tomorrow's content. Will return error message if there is no content for tomorrow.")
async def tomorrow():
    tomorrow = (datetime.date.today() +
                datetime.timedelta(days=1)).strftime("%d.%m.%Y")
    try:
        return calendar[tomorrow]
    except KeyError:
        return {"error": "No content for tomorrow."}


@app.get(path="/closest", description="Get closest day's content. Will return content with date included.")
async def closest_day():
    closestDay: str = list(calendar.keys())[0]
    data: str = calendar[closestDay]
    data["date"] = closestDay
    return data

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=2000, loop="asyncio")
