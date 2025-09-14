import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from retrieval import *
from llm import *
from db import log_qa

APP_NAME = os.getenv("APP_NAME", "resolve-rag-api")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "0") == "1"

# CORS: por defecto permite todo. Puedes fijar CORS_ALLOW_ORIGINS="https://tu-frontend.com,https://otra.com"
_raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "*")
ALLOWED_ORIGINS = "*" if _raw_origins.strip() == "*" else [o.strip() for o in _raw_origins.split(",")]

app = Flask(APP_NAME)
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})


@app.get("/health")
def health():
    return jsonify({"ok": True, "app": APP_NAME}), 200


@app.post("/ask")
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    debug = bool(data.get("debug", False))

    if not question:
        return jsonify({"error": "Missing 'question'"}), 400

    # 1) Recuperación de contexto (idioma + fragmentos + páginas)
    lang, contexts, pages = retrieve(question)  # devuelve (lang, ctx, pages)

    # 2) Respuesta final con citas
    final_answer = answer(question, contexts, pages, lang)
        
    # 2.1) Log en BBDD (best-effort)
    try:
        row_id = log_qa(question, final_answer)
        print(f"[DB] confirmado insert id={row_id}")
    except Exception as e:
        print(f"[DB] error insert: {e}")

    payload = {
        "answer": final_answer,
        "lang": lang,
        "citations": [{"page": p} for p in pages],
    }

    if debug:
        payload["debug"] = {
            "pages": pages,
            "contexts": contexts,
        }

    return jsonify(payload), 200


@app.post("/suggest-terms")
def suggest_terms():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Missing 'question'"}), 400

    lang = detect_lang(question)
    keywords = expand_queries(question, lang)
    return jsonify({"lang": lang, "keywords": keywords}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)