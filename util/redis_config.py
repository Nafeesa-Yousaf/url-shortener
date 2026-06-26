from dotenv import load_dotenv
import os
from upstash_redis import Redis

load_dotenv()
upstash_url=os.getenv("UPSTASH_URL")
upstash_token=os.getenv("UPSTASH_TOKEN")

redis_client=Redis(url=upstash_url,token=upstash_token)
