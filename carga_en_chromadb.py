import chromadb, json
from settings import *

# Carga el JSON enriquecido
with open(ENRICHED_PATH, "r", encoding="utf-8") as f:
    enriched_chunks = json.load(f)

# Prepara los datos para ChromaDB
texts = [chunk["text"] for chunk in enriched_chunks]
metadatas = [{"page": chunk["page"]} for chunk in enriched_chunks]
embeddings = [chunk["embedding"] for chunk in enriched_chunks]

# Inicializa ChromaDB en modo local
import chromadb.config
client = chromadb.PersistentClient(path=VECTOR_PATH)
collection = client.create_collection(
    name = COLLECTION_NAME,
    metadata = {"hnsw:space": "cosine"})

# Inserta los datos
ids = [f"frag_{i}" for i in range(len(texts))]
collection.add(
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids)

print("¡Base vectorial creada e inicializada con ChromaDB!")