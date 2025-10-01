from pathlib import Path
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

VECTOR_PATH = Path(__file__).parent / "chromadb_data"
COLLECTION_NAME = "manual_resolve"

PDF_PATH = Path(__file__).parent / "ingest" / "DaVinci_Resolve_19_Reference_Manual.pdf"
ENRICHED_PATH = Path(__file__).parent / "ingest" / "manual_enriched.json"
CHUNKS_PATH = Path(__file__).parent / "ingest" / "manual_chunks.json"

EMBEDDING_MODEL = "text-embedding-3-small"          # embeddings en Groq
CHAT_MODEL = "openai/gpt-oss-20b"             # más barato para traducción/detección
ANSWER_MODEL = "openai/gpt-oss-120b"          # respuestas

TOP_K = 25                          # recuperación inicial
RETURN_K = 10                       # tras rerank/merge
MULTILINGUAL = True                 # activar flujo multilingüe
USE_HYDE = False                    # si quieres añadir “query hipotética”
TEMPERATURE = 0.2

# sinónimos/alias por tema (mejorables con el tiempo)
QUERY_EXPANSIONS_EN = ["deliver page", "render", "quick export", "individual clips", "render this clip"]
QUERY_EXPANSIONS_FR = ["rendu", "page Deliver", "exportation rapide", "clips individuels"]
QUERY_EXPANSIONS_ES = ["render", "página Deliver", "exportación rápida", "clips individuales"]


# --- DB (PostgreSQL / RDS) ---
PG_HOST = os.getenv("PGHOST", "test.cxcwgyue8y8m.eu-west-3.rds.amazonaws.com")
PG_PORT = int(os.getenv("PGPORT", "5432"))
PG_DB   = os.getenv("PGDATABASE", "postgres")
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASSWORD = os.getenv("AWS_BBDD_PASS")
PG_SSLMODE = os.getenv("PGSSLMODE", "prefer")

DB_CONFIG = {
    "host": PG_HOST, "port": PG_PORT, "dbname": PG_DB,
    "user": PG_USER, "password": PG_PASSWORD, "sslmode": PG_SSLMODE
}