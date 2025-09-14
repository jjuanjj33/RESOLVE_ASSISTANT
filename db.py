from psycopg2.pool import SimpleConnectionPool
from settings import *
from typing import Optional
import psycopg2

_POOL: Optional[SimpleConnectionPool] = None

def _pool() -> SimpleConnectionPool:
    global _POOL
    if _POOL is None:
        # min/max ajustables
        _POOL = SimpleConnectionPool(minconn=1, maxconn=5, **DB_CONFIG)
    return _POOL

def log_qa(pregunta: str, respuesta: str) -> int:
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.preguntas_respuestas (preguntas, respuestas, fecha) VALUES (%s, %s, NOW()) RETURNING id",
                    (pregunta, respuesta),
                )
                inserted_id = cur.fetchone()[0]
                print(f"[DB] inserted id={inserted_id}")
                return inserted_id
    finally:
        conn.close()