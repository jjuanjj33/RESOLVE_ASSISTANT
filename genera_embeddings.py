import openai, json, time, os
from settings import *

# API key
openai.api_key = OPENAI_API_KEY

# Carga el JSON de fragmentos
with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Nombre del modelo embedding recomendado
embedding_model = EMBEDDING_MODEL

enriched_chunks = []
for idx, chunk in enumerate(chunks):
    texto = chunk["text"]
    try:
        response = openai.embeddings.create(
            input=texto,
            model=embedding_model
        )
        embedding = response.data[0].embedding
        chunk["embedding"] = embedding
        enriched_chunks.append(chunk)
        print(f"Fragmento {idx+1}/{len(chunks)} procesado")
    except Exception as e:
        print(f"Error en fragmento {idx+1}: {e}")
        continue
    # Pausa breve para evitar límites de la API (puedes bajar a 0.2 si eres impaciente)
    time.sleep(0.5)

# Guarda el resultado enriquecido
with open(ENRICHED_PATH, "w", encoding="utf-8") as f:
    json.dump(enriched_chunks, f, ensure_ascii=False, indent=2)

print("¡Embeddings creados y guardados en manual_enriched.json!")