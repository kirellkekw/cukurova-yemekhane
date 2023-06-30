from fastapi import FastAPI, Query
import requests
import re
import jsonpickle
import datetime

r = requests.get(url="https://yemekhane.cu.edu.tr/yemeklistejson.asp")
r.encoding = "ISO-8859-9"
r = re.sub(r'<meta .*>', '', r.text)

calendar = jsonpickle.decode(r)

app = FastAPI()


@app.get(path="/", description="Get root tree of the API.")
async def root():
    return calendar


@app.get(path="/today/", description="Get today's content. Will return error message if there is no content for today.")
async def bugün():
    today = datetime.date.today().strftime("%d.%m.%Y")
    try:
        return calendar[today]
    except KeyError:
        return {"error": "No content for today."}

@app.get(path="/tomorrow/", description="Get tomorrow's content. Will return error message if there is no content for tomorrow.")
async def yarın():
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
    try:
        return calendar[tomorrow]
    except KeyError:
        return {"error": "No content for tomorrow."}
    
@app.get(path="/closest/", description="Get closest day's content. Will return content with date included.")
async def en_yakın():

    closestDate:str = list(calendar.keys())[0]
    data:str = calendar[closestDate]
    data["date"] = closestDate
    return data


@app.get(path="/date/", description="Get chosen day's content with query parameter.")
async def gün(tarih: str = Query(enum=list(calendar.keys()))):
    try:
        return calendar[tarih]
    except KeyError:
        return {"error": "No content for this date or meal."}



@app.get(path="/meal/", description="Get chosen day's chosen meal with query parameters. Will return error message if chosen meal is not available.")
async def yemek(tarih:str=Query(enum=list(calendar.keys())), yemek:str=Query(enum=["1", "2", "3", "4"])):
    try:
        return calendar[tarih][f"yemek{yemek}"]
    except KeyError:
        return {"error": "No content for this date or meal."}
    
    
for day in calendar:
    @app.get(path=f"/{day}/", description="Get chosen day's content.")
    async def gün():
        return calendar[day]