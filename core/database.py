import os
from dotenv import load_dotenv
from psycopg2 import pool
from contextlib import contextmanager
load_dotenv()
db_url = os.getenv("POSTGRES_URL")

connection_poll=pool.SimpleConnectionPool(
    1,5,db_url
)

@contextmanager
def get_db():
    conn=connection_poll.getconn()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        connection_poll.putconn(conn)