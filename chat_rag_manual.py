import chromadb, openai
from settings import *

# Conexión a la base persistente
client = chromadb.PersistentClient(path=VECTOR_PATH)
collection = client.get_collection(COLLECTION_NAME)

# API key de OpenAI
openai.api_key = OPENAI_API_KEY

embedding_model = EMBEDDING_MODEL
openai_model = ANSWER_MODEL

def buscar_contexto(pregunta, n=5):
    # Genera embedding de la pregunta
    response = openai.embeddings.create(
        input=pregunta,
        model=embedding_model
    )
    pregunta_embedding = response.data[0].embedding
    # Busca los n fragmentos más relevantes
    resultados = collection.query(
        query_embeddings=[pregunta_embedding],
        n_results=n
    )
    contextos = resultados["documents"][0]
    paginas = [str(meta["page"]) for meta in resultados["metadatas"][0]]
    return contextos, paginas

def construir_prompt(pregunta, contextos, paginas):
    # Une los fragmentos en un solo contexto para el prompt
    contexto = "\n\n".join(
        [f"[Página {paginas[i]}]: {c}" for i, c in enumerate(contextos)]
    )
    prompt = (
        "Eres un asistente experto en DaVinci Resolve. "
        "Responde únicamente usando el contexto proporcionado, "
        "citando la página si es posible. "
        "No inventes nada que no esté en el contexto. "
        "Si no hay respuesta en el contexto, dilo claro.\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Pregunta: {pregunta}\n\n"
        "Respuesta:"
    )
    return prompt

def main():
    print("¡Consulta el manual de DaVinci Resolve como un pro! (escribe 'salir' para terminar)")
    while True:
        pregunta = input("\n¿Qué quieres saber?: ")
        if pregunta.lower() == "salir":
            break
        contextos, paginas = buscar_contexto(pregunta)
        prompt = construir_prompt(pregunta, contextos, paginas)
        respuesta = openai.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        print("\n>>>", respuesta.choices[0].message.content.strip())

if __name__ == "__main__":
    main()
