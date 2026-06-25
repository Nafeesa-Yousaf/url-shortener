from core.database import get_db
from psycopg2.extras import RealDictCursor

class UrlRepo():

    def add_url(self, url:str)->int:
        with get_db() as conn:
            cur=conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """Insert into url (url_str) values (%s)""",
                (url,)
            )
            res=cur.fetchone()
            conn.commit()
            return res["id"]
    
    def fetch_url(self,id:int)->str:
        with get_db() as conn:
            cur=conn.cursor(cursor_factor=RealDictCursor)
            cur.execute(
                """Select url_str from url where id=%s""",
                (id)
            )
            res=cur.fetchall()
            return res