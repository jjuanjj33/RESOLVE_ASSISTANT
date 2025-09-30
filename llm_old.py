from typing import List, Union
from groq import Groq
import openai
from settings import *

# openai.api_key = OPENAI_API_KEY
client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Helpers internos
def _build_rag_prompt(question: str, contexts: List[str], pages: List[Union[str, int]], lang_code: str) -> str:
    """
    Construye un prompt RAG con citas por página. Si no hay contexto, lo declara.
    """
    if contexts and pages:
        ctx_blocks = "\n\n".join([f"[Página {str(pages[i])}]: {c}" for i, c in enumerate(contexts)])
    else:
        ctx_blocks = "(No hay contexto disponible para esta consulta.)"

    return (
        "Eres un asistente experto en DaVinci Resolve. "
        "Responde únicamente usando el contexto proporcionado, citando la página al final de cada afirmación relevante "
        "en formato (p. N). No inventes nada que no esté en el contexto. "
        "Si no hay respuesta en el contexto, dilo claramente.\n\n"
        f"Responde en el idioma del usuario (código: {lang_code}).\n\n"
        f"Contexto:\n{ctx_blocks}\n\n"
        f"Pregunta ({lang_code}): {question}\n\n"
        "Respuesta:"
    )
    
# API pública
def detect_lang(text: str) -> str:
    """
    Devuelve el código ISO-639-1 del idioma del usuario (ej. 'es', 'en').
    Si MULTILINGUAL es False, fuerza 'en'.
    """
    if not MULTILINGUAL:
        return "en"

    msgs = [
        {"role": "system", "content": "Devuelve solo el código ISO-639-1 del idioma del usuario."},
        {"role": "user", "content": text[:800]},
    ]
    out = openai.chat.completions.create(model=CHAT_MODEL, messages=msgs, temperature=0)
    return out.choices[0].message.content.strip().lower()[:2]


def translate(text: str, target: str = "en") -> str:
    """
    Traduce 'text' al idioma 'target'. Sin adornos, tono técnico cuando 'target' es 'en'.
    """
    if target == "en":
        system = "Traduce al inglés técnico de posproducción, sin adornos."
    else:
        system = f"Traduce al {target} de forma neutral y precisa, sin adornos."

    msgs = [
        {"role": "system", "content": system},
        {"role": "user", "content": text},
    ]
    out = openai.chat.completions.create(model=CHAT_MODEL, messages=msgs, temperature=0)
    return out.choices[0].message.content.strip()


def embed(texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """
    Genera embeddings con EMBEDDING_MODEL.
    - Si 'texts' es str → devuelve List[float]
    - Si 'texts' es List[str] → devuelve List[List[float]]
    """
    single = isinstance(texts, str)
    payload = [texts] if single else texts
    resp = openai.embeddings.create(model=EMBEDDING_MODEL, input=payload)
    embs = [d.embedding for d in resp.data]
    return embs[0] if single else embs


def answer(question: str, contexts: List[str], pages: List[Union[str, int]], lang: str) -> str:
    """
    Orquesta la respuesta final usando ANSWER_MODEL y el prompt RAG.
    - 'lang' debe ser el ISO-639-1 detectado.
    - 'contexts' y 'pages' deben ir alineados (mismo orden/longitud).
    """
    prompt = _build_rag_prompt(question, contexts, pages, lang_code=lang)
    rsp = openai.chat.completions.create(
        model=ANSWER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
    )
    return rsp.choices[0].message.content.strip()