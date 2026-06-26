from core.database import get_db
from psycopg2.extras import RealDictCursor

class UrlRepo():

    def add_url(self, url:str)->int:
        with get_db() as conn:
            cur=conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """Insert into short_urls (original_url) values (%s) RETURNING id""",
                (url,)
            )
            res=cur.fetchone()
            conn.commit()
            return res["id"]
    
    def fetch_url(self,id:int)->str:
        with get_db() as conn:
            cur=conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """Select original_url from short_urls where id=%s""",
                (id,)
            )
            res=cur.fetchall()
            return res[0]["original_url"]