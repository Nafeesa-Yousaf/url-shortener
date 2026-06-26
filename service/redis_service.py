from util.redis_config import redis_client
from fastapi import Request, HTTPException, status
import logging

class RedisService():
    def __init__(self):
        pass

    def rate_limit(self,request:Request):
        client_ip=request.client.host
        redis_key=f"rate_limit:{client_ip}"
        pipeline = redis_client.pipeline()        
        pipeline.incr(redis_key)
        pipeline.expire(redis_key, 10)        
        result = pipeline.exec()
        current_request=result[0]
        if current_request and int(current_request)>10:
            logging.warning(f"🚫 [RATE LIMIT BLOCK] IP {client_ip} exceeded request threshold!")
            raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests."
            )

    def get_url(self,code:str):
        return redis_client.get(code)
    
    def store_data(self,key:str,value:str):
        return redis_client.set(key=key, value=value, ex=1296000)