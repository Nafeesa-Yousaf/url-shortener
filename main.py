from fastapi import FastAPI, status
from service.url_service import UrlService
from fastapi.responses import RedirectResponse

app=FastAPI()

@app.post("/url_shortner")
def url_shortner(url:str):
    return UrlService().get_short_url(org_url=url)

@app.get("/{short_url}")
def get_website(short_url:str):
    url=UrlService().get_website(short_url)
    return RedirectResponse(url=url,status_code=status.HTTP_302_FOUND)
