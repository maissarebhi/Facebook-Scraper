from fastapi import FastAPI
from facebookScraper import facebookScraper
import uvicorn
app = FastAPI()


@app.get("/{pagename}")
async def read_item(pagename,user,pwd):
    fb=facebookScraper(user,pwd)
    return fb.collect_page(pagename)