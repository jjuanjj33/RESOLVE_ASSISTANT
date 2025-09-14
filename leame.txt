Resolve Assistant — RAG sobre el manual de DaVinci Resolve 19

Resumen
-------
Backend en Flask con dos endpoints principales (/ask y /suggest-terms), frontend estático (index.html + app.js) y recuperación en ChromaDB persistente.
Se usa OpenAI para embeddings, detección de idioma, traducción y respuesta final.
Se registran los Q/A en PostgreSQL.

Estructura mínima
-----------------
- app.py .................. API Flask (/health, /ask, /suggest-terms)
- retrieval.py ............ Conexión a ChromaDB + retrieve + expansión de consulta
- llm.py .................. Detección de idioma, traducción, embeddings y respuesta RAG
- settings.py ............. Configuración (modelos, paths, env vars, DB)
- db.py ................... Inserción best-effort en PostgreSQL
- index.html / app.js ..... Front simple que llama a la API; API_BASE por defecto http://localhost:8000

Requisitos
----------
- Python 3.x
- Clave de OpenAI en la variable de entorno OPENAI_API_KEY.
- Vector store ChromaDB existente en `./chromadb_data` con la colección `manual_resolve`.
  (La API lee del almacén persistente; la ingesta del PDF no forma parte de este repo de ejecución.)

Instalación
-----------
1) Crear entorno e instalar:
   pip install -r requirements.txt

2) Variables de entorno (mínimas):
   - OPENAI_API_KEY ...................... clave de OpenAI
   - (Opcional CORS) CORS_ALLOW_ORIGINS .. por defecto "*"
   - (Opcional API) APP_NAME, PORT, DEBUG  (PORT por defecto 8000)
   - (Opcional DB) PGHOST, PGPORT, PGDATABASE, PGUSER, AWS_BBDD_PASS, PGSSLMODE

Ejecución
---------
Backend:
   python app.py
   - Levanta en 0.0.0.0:PORT (8000 por defecto).

Frontend:
   - Abrir index.html en el navegador.
   - app.js llama a la API en API_BASE='http://localhost:8000' (ajústalo si despliegas remoto).

Endpoints
---------
GET /health
  → {"ok": true, "app": "<APP_NAME>"}  (comprobación de vida)

POST /ask
  Body JSON: { "question": "<texto>", "debug": <bool opcional> }
  Respuesta: {
    "answer": "<texto final>",
    "lang": "<iso-639-1>",
    "citations": [{"page":"<n>"}...],
    "debug": { "pages":[...], "contexts":[...] } // si debug=true
  }
  - Flujo interno: detecta idioma → expande consulta → embeddings → consulta a ChromaDB
    → compone respuesta RAG con citas (p. N).

POST /suggest-terms
  Body JSON: { "question": "<texto>" }
  Respuesta: { "lang":"<iso>", "keywords":[...] }  (expansión basada en términos de export/render)

Modelos y parámetros (por defecto)
----------------------------------
- Embeddings: text-embedding-3-small  (EMBEDDING_MODEL)
- Chat/detección/traducción: gpt-4o-mini (CHAT_MODEL)
- Respuesta final: gpt-4o (ANSWER_MODEL), temperature=0.2
- Recuperación: TOP_K=25, RETURN_K=10; colección: "manual_resolve" en ./chromadb_data
- Expansiones por idioma para términos de exportación/render.

Persistencia en BBDD (opcional)
-------------------------------
- Inserta (pregunta, respuesta, fecha) en public.preguntas_respuestas. Si falla, no interrumpe la respuesta (best-effort).

Notas
-----
- CORS permite todo por defecto; define CORS_ALLOW_ORIGINS para restringir dominios.
- El PDF y rutas de ingestión están en settings.py pero no son necesarios para servir la API si ya existe el vector store.