"""
cukurova-yemekhane
An unofficial API interface for Çukurova University's dining hall food list.

This project is provided as is, without any warranty or support,
and is not affiliated with Çukurova University in any way.

This project is licensed under the GNU General Public License v3.0.
For more information, please visit https://www.gnu.org/licenses/gpl-3.0.html.
"""


import asyncio
import datetime
import re
import requests
import uvicorn
import jsonpickle
from fastapi import FastAPI

# pylint: disable=global-statement


def load_calendar():
    """
    Loads the food list from the website.
    """
    req = requests.get(
        url="https://yemekhane.cu.edu.tr/yemeklistejson.asp", timeout=60)
    req.encoding = "ISO-8859-9"
    req = re.sub(r'<meta .*>', '', req.text)

    return jsonpickle.decode(req)


calendar = load_calendar()


async def refresh_food_list():
    """
    Refreshes the food list every 24 hours.
    This project runs on vercel, so this probably won't be used, but it's here just in case.
    """
    global calendar  # needed to modify the global calendar object

    while True:
        await asyncio.sleep(60*60*24)  # check every 24 hours
        new_calendar = load_calendar()  # load the new food list preemptively
        calendar = new_calendar  # update the global calendar object with the new food list


app = FastAPI()


@app.on_event("startup")  # run this function when the server starts
async def startup_event():
    """Creates sub-processes to run in the background when the server starts."""
    asyncio.create_task(refresh_food_list())


@app.get(path="/root", description="Get root tree of the API.")
async def get_all_root():
    """Endpoint to get the root tree of the API."""
    try:
        return calendar
    except KeyError:
        return {"error": "No data available, please try again later."}


@app.get(
    path="/{day}",
    description="Get content for a specific day."
)
async def get_by_day(day: str):
    """Endpoint to get content for a specific day, with a shorter path."""

    if day == r"{date}":
        return {"error": "Please enter a valid date in /DD.MM.YYYY format." +
                " Example: /01.01.2024 or /31.12.2024"
                }

    try:
        return calendar[day]
    except KeyError:
        return {"error": "No content for this date or meal."}


@app.get(
    path="/today",
    description="Get today's content. Will return error message if there is no content for today."
)
async def get_today():
    """Endpoint to get today's content."""
    today_date = datetime.date.today().strftime("%d.%m.%Y")
    try:
        data = calendar[today_date]
        data["date"] = today_date
        return data
    except KeyError:
        return {"error": "No content for today."}


@app.get(
    path="/tomorrow",
    description="Get tomorrow's content. " +
    "Will return error message if there is no content for tomorrow."
)
async def get_tomorrow():
    """Endpoint to get tomorrow's content."""
    tomorrow_date = (datetime.date.today() +
                     datetime.timedelta(days=1)).strftime("%d.%m.%Y")
    try:
        data = calendar[tomorrow_date]
        data["date"] = tomorrow_date
        return data
    except KeyError:
        return {"error": "No content for tomorrow."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=2000, loop="asyncio")
