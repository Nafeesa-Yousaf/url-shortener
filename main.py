from fastapi import FastAPI, status, Request
from service.url_service import UrlService
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl
from util.redis_config import redis_client
app=FastAPI()

@app.post("/url_shortner")
def url_shortner(request:Request,url:HttpUrl):
    code= UrlService().get_short_code(org_url=url.unicode_string())
    short_url=str(request.base_url)+code
    return {"short_url":short_url}

@app.get("/{short_url}")
def get_website(short_url:str):
    cached_url=redis_client.get(short_url)
    if cached_url:
        return RedirectResponse(url=cached_url,status_code=status.HTTP_302_FOUND)
    url=UrlService().get_website(short_url)
    return RedirectResponse(url=url,status_code=status.HTTP_302_FOUND)
