# settings.py
from pathlib import Path
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

VECTOR_PATH = Path(__file__).parent / "chromadb_data"
COLLECTION_NAME = "manual_resolve"

PDF_PATH = Path(__file__).parent / "ingest" / "DaVinci_Resolve_19_Reference_Manual.pdf"
ENRICHED_PATH = Path(__file__).parent / "ingest" / "manual_enriched.json"
CHUNKS_PATH = Path(__file__).parent / "ingest" / "manual_chunks.json"

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"          # más barato para traducción/detección
ANSWER_MODEL = "gpt-4o"             # respuestas

TOP_K = 25                          # recuperación inicial
RETURN_K = 10                       # tras rerank/merge
MULTILINGUAL = True                 # activar flujo multilingüe
USE_HYDE = False                    # si quieres añadir “query hipotética”
TEMPERATURE = 0.2

# sinónimos/alias por tema (mejorables con el tiempo)
QUERY_EXPANSIONS_EN = ["deliver page", "render", "quick export", "individual clips", "render this clip"]
QUERY_EXPANSIONS_FR = ["rendu", "page Deliver", "exportation rapide", "clips individuels"]
QUERY_EXPANSIONS_ES = ["render", "página Deliver", "exportación rápida", "clips individuales"]
