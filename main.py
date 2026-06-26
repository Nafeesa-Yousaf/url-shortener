from fastapi import FastAPI, status, Request
from service.url_service import UrlService
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl
app=FastAPI()

@app.post("/url_shortner")
def url_shortner(request:Request,url:HttpUrl):
    code= UrlService().get_short_code(org_url=url.unicode_string())
    short_url=str(request.base_url)+code
    return {"short_url":short_url}

@app.get("/{short_url}")
def get_website(short_url:str):
    url=UrlService().get_website(short_url)
    return RedirectResponse(url=url,status_code=status.HTTP_302_FOUND)
