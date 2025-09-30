import chromadb
from settings import *
from llm import *
from typing import List


def expand_queries(q: str, lang: str) -> List[str]:
    alts = [q]
    if "export" in q.lower() or "exporter" in q.lower() or "exportar" in q.lower():
        if lang == "es": alts += QUERY_EXPANSIONS_ES
        elif lang == "fr": alts += QUERY_EXPANSIONS_FR
        else: alts += QUERY_EXPANSIONS_EN
    # dedupe simple
    seen, out = set(), []
    for t in alts:
        if t not in seen: out.append(t); seen.add(t)
    return out

def connect_collection():
    client = chromadb.PersistentClient(path=str(VECTOR_PATH))
    return client.get_collection(COLLECTION_NAME)

def retrieve(q_user: str):
    col = connect_collection()
    lang = detect_lang(q_user)
    queries = expand_queries(q_user, lang)
    emb = [embed(t) for t in queries]

    # bilingüe: añadimos traducción EN si no es inglés
    if lang != "en":
        queries.append(translate(q_user, "en"))
        emb.append(embed(queries[-1]))

    res = col.query(query_embeddings=emb, n_results=TOP_K, include=["documents","metadatas","distances"])
    # aplanar, ordenar por distancia y devolver los mejores RETURN_K
    items = []
    for qi in range(len(emb)):
        for d, m, s in zip(res["documents"][qi], res["metadatas"][qi], res["distances"][qi]):
            items.append((s, m.get("page"), d))
    items.sort(key=lambda x: x[0])
    items = items[:RETURN_K]
    ctx = [d for _,_,d in items]
    pages = [str(p) for _,p,_ in items]
    return lang, ctx, pages