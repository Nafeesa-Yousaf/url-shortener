from fastapi import FastAPI, status, Request, Response, Depends
from service.url_service import UrlService
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl
from util.redis_config import redis_client
import logging
from service.redis_service import RedisService
app=FastAPI()

@app.get("/favicon.png", include_in_schema=False)
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/url_shortner",dependencies=[Depends(RedisService().rate_limit)])
def url_shortner(request:Request,url:HttpUrl):
    logging.info(f"📥 [POST /url_shortner] Request received for: {url.unicode_string()}")
    code= UrlService().get_short_code(org_url=url.unicode_string())
    short_url=str(request.base_url)+code
    logging.info(f"✅ [SUCCESS] Short url generated")
    return {"short_url":short_url,"message": "This link will expire in 15 days."}

@app.get("/{short_url}", dependencies=[Depends(RedisService().rate_limit)])
def get_website(short_url:str):
    cached_url=RedisService().get_url(short_url)
    if cached_url:
        logging.info(f"🚀 [REDIS HIT] found inside Upstash memory!")
        return RedirectResponse(url=cached_url,status_code=status.HTTP_302_FOUND)
    logging.warning(f"⚠️ [CACHE MISS] token '{short_url}' not found in Redis. Fetching from PostgreSQL...")
    url=UrlService().get_website(short_url)
    logging.info(f"💾 [DB RESOLVED] Found in PostgreSQL. Redirecting to: {url}")
    return RedirectResponse(url=url,status_code=status.HTTP_302_FOUND)
