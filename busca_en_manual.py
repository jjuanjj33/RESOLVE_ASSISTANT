import chromadb, openai
from settings import *

# Inicializa el cliente y accede a la colección
client = chromadb.PersistentClient(path=VECTOR_PATH)
collection = client.get_collection(COLLECTION_NAME)

# Simula una consulta (ejemplo: pregunta de prueba)
pregunta = "¿Cómo exporto un proyecto en DaVinci Resolve?"
# Aquí necesitarías crear el embedding de la pregunta con OpenAI:
openai.api_key = OPENAI_API_KEY

embedding_model = EMBEDDING_MODEL
response = openai.embeddings.create(input=pregunta,
                                    model=embedding_model)
query_embedding = response.data[0].embedding

# Busca los fragmentos más relevantes
resultados = collection.query(
    query_embeddings=[query_embedding],
    n_results=3)

for i, doc in enumerate(resultados["documents"][0]):
    print(f"\n--- Resultado {i+1} ---")
    print(doc)
    print(f"Página: {resultados['metadatas'][0][i]['page']}")