from fastapi import FastAPI, Query
import requests
import re
import jsonpickle

r = requests.get(url="https://yemekhane.cu.edu.tr/yemeklistejson.asp")
r.encoding = "ISO-8859-9"
r = re.sub(r'<meta .*>', '', r.text)

calendar = jsonpickle.decode(r)

app = FastAPI()

@app.get(path="/", description="Get root tree of the API.")
async def root():
    return calendar

@app.get(path="/gün/", description="Get chosen day's content with query parameter.")
async def gün(tarih: str = Query(enum=list(calendar.keys()))):
    return calendar[tarih]

@app.get(path="/yemek/", description="Get chosen day's chosen meal with query parameters. Will fail if chosen meal is not available.")
async def yemek(tarih:str=Query(enum=list(calendar.keys())), yemek:str=Query(enum=["1", "2", "3", "4"])):
    return calendar[tarih][f"yemek{yemek}"]

for day in calendar:

    @app.get(path=f"/{day}/", description="Get chosen day's content.")
    async def gün():
        return calendar[day]
    
    if calendar[day]["yemek1"] != None:
        @app.get(path=f"/{day}/yemek1/", description="Get chosen day's first meal.")
        async def yemek1():
            return calendar[day]["yemek1"]
    
    if calendar[day]["yemek2"] != None:
        @app.get(path=f"/{day}/yemek2/", description="Get chosen day's second meal.")
        async def yemek2():
            return calendar[day]["yemek2"]
    
    if calendar[day]["yemek3"] != None:
        @app.get(path=f"/{day}/yemek3/", description="Get chosen day's third meal.")
        async def yemek3():
            return calendar[day]["yemek3"]
    
    if calendar[day]["yemek4"] != None:
        @app.get(path=f"/{day}/yemek4/", description="Get chosen day's fourth meal.")
        async def yemek4():
            return calendar[day]["yemek4"]