from fastapi import FastAPI
from service.url_service import UrlService

app=FastAPI()

@app.post("/url_shortner")
def url_shortner(url:str):
    return UrlService().get_short_url(org_url=url)

@app.get("/")
def get_website(short_url:str):
    return UrlService().get_website(short_url)
