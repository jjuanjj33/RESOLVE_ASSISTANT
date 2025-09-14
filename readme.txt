Resolve Assistant — RAG over DaVinci Resolve 19 manual

Summary
-------
Backend in Flask with two main endpoints (/ask and /suggest-terms), static frontend (index.html + app.js) and persistent retrieval in ChromaDB.
OpenAI is used for embeddings, language detection, translation, and final response.
Q/A are logged in PostgreSQL.

Minimal structure
-----------------
- app.py .................. Flask API (/health, /ask, /suggest-terms)
- retrieval.py ............ Connection to ChromaDB + retrieve + query expansion
- llm.py .................. Language detection, translation, embeddings and RAG response
- settings.py ............. Configuration (models, paths, env vars, DB)
- db.py ................... Best-effort insertion into PostgreSQL
- index.html / app.js ..... Simple frontend calling the API; API_BASE defaults to http://localhost:8000

Requirements
------------
- Python 3.x
- OpenAI key in environment variable OPENAI_API_KEY.
- Existing ChromaDB vector store in ./chromadb_data with collection manual_resolve.
  (The API reads from the persistent store; PDF ingestion is not part of this runtime repo.)

Installation
------------
1). Create environment and install:
    pip install -r requirements.txt

2). Environment variables (minimum):
    - OPENAI_API_KEY ...................... OpenAI key
    - (Optional CORS) CORS_ALLOW_ORIGINS .. default "*"
    - (Optional API) APP_NAME, PORT, DEBUG (PORT defaults to 8000)
    - (Optional DB) PGHOST, PGPORT, PGDATABASE, PGUSER, AWS_BBDD_PASS, PGSSLMODE

Execution
---------
Backend:
    python app.py
    - Runs on 0.0.0.0:PORT (default 8000).

Frontend:
    - Open index.html in browser.
    - app.js calls the API at API_BASE='http://localhost:8000' (adjust if deployed remotely).

Endpoints
---------
GET /health
    → {"ok": true, "app": "<APP_NAME>"} (health check)

POST /ask
    JSON Body: { "question": "<text>", "debug": <optional bool> }
    Response: {
        "answer": "<final text>",
        "lang": "<iso-639-1>",
        "citations": [{"page":"<n>"}...],
        "debug": { "pages":[...], "contexts":[...] } // if debug=true
    }

    - Internal flow: detect language → expand query → embeddings → query ChromaDB → compose RAG response with citations (p. N).

POST /suggest-terms
    JSON Body: { "question": "<text>" }
    Response: { "lang":"<iso>", "keywords":[...] } (expansion based on export/render terms)

Models and parameters (default)
-------------------------------
- Embeddings: text-embedding-3-small (EMBEDDING_MODEL)
- Chat/detection/translation: gpt-4o-mini (CHAT_MODEL)
- Final answer: gpt-4o (ANSWER_MODEL), temperature=0.2
- Retrieval: TOP_K=25, RETURN_K=10; collection: "manual_resolve" in ./chromadb_data
 -Language-based expansions for export/render terms.

DB persistence (optional)
-------------------------
- Inserts (question, answer, date) into public.preguntas_respuestas. If it fails, response is not interrupted (best-effort).

Notes
-----
- CORS allows all by default; define CORS_ALLOW_ORIGINS to restrict domains.
- The PDF and ingestion routes are in settings.py but not required to serve the API if the vector store already exists.