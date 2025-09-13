import streamlit as st
import openai
from settings import *
from retrieval import retrieve                  # detecta idioma, expande consulta, busca y devuelve contexto

# ---------- Config UI ----------
st.set_page_config(
    page_title="DaVinci Resolve Assistant",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="auto"
)

# ---------- Estilos (look & feel Resolve) ----------
st.markdown("""
    <style>
    body, .stApp { background-color: #232629; color: #ffffff; font-family: 'Segoe UI', 'Arial', sans-serif; }
    .block-container { background-color: #232629; border-radius: 10px; padding: 2rem; }
    .stButton>button {
        color: #ffffff; background-color: #3f4450; border: 1px solid #868686;
        border-radius: 12px; font-weight: bold; transition: 0.2s;
    }
    .stButton>button:hover { background-color: #0082ff; color: #fff700; }
    .stTextInput>div>div>input { background-color: #232629; color: #fff; border: 1px solid #868686; border-radius: 8px; }
    .chat-bubble {
        background: linear-gradient(90deg, #2c3136 80%, #323743 100%);
        color: #fff; padding: 1rem; border-radius: 1rem; margin-bottom: 1rem; border-left: 6px solid #f9d65d;
    }
    </style>
""", unsafe_allow_html=True)

# OpenAI API key
openai.api_key = OPENAI_API_KEY

# ---------- Helpers ----------
def construir_prompt(pregunta, contextos, paginas, lang_code: str) -> str:
    """
    Construye un prompt RAG, forzando respuesta en el idioma detectado (lang_code).
    """
    contexto = "\n\n".join([f"[Página {paginas[i]}]: {c}" for i, c in enumerate(contextos)])
    return (
        "Eres un asistente experto en DaVinci Resolve. "
        "Responde únicamente usando el contexto proporcionado, citando la página al final de cada afirmación relevante "
        "en formato (p. N). No inventes nada que no esté en el contexto. "
        "Si no hay respuesta en el contexto, dilo claramente.\n\n"
        f"Responde en el idioma del usuario (código: {lang_code}).\n\n"
        f"Contexto:\n{contexto}\n\n"
        f"Pregunta ({lang_code}): {pregunta}\n\n"
        "Respuesta:"
    )

# ---------- Título/UI ----------
st.title("🎬 DaVinci Resolve Assistant")
st.markdown("<h4 style='color:#f9d65d;'>Resuelve tus dudas como un editor profesional</h4>", unsafe_allow_html=True)
st.write("Pregunta en el idioma que quieras y te responderé con citas al manual oficial.")

# Historial en sesión
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Entrada de la pregunta
pregunta = st.text_input("¿Cuál es tu duda?", "")

# Botón principal
if st.button("Consultar"):
    if not pregunta.strip():
        st.warning("Escribe una pregunta.")
    else:
        # 1) Recuperación multilingüe (detecta idioma, expande consulta, bilingüe ES/EN/FR, etc.)
        lang, contextos, paginas = retrieve(pregunta)

        # 2) Construir prompt con el contexto recuperado y el idioma detectado
        prompt = construir_prompt(pregunta, contextos, paginas, lang)

        # 3) Llamada al modelo de respuesta final
        with st.spinner("Buscando respuesta..."):
            rsp = openai.chat.completions.create(
                model=ANSWER_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=TEMPERATURE,
            )
            result = rsp.choices[0].message.content.strip()

        # 4) Guardar en historial
        st.session_state.chat_history.append({"user": pregunta, "bot": result, "pages": paginas})

# Mostrar historial (últimos primero)
for entrada in reversed(st.session_state.chat_history):
    st.markdown(
        f'<div class="chat-bubble"><b>Tú:</b> {entrada["user"]}<br/><b>Assistant:</b> {entrada["bot"]}</div>',
        unsafe_allow_html=True
    )
    # Páginas citadas (debug útil para auditar la recuperación)
    if entrada.get("pages"):
        st.caption("Páginas de contexto: " + ", ".join(sorted(set(entrada["pages"]), key=lambda x: int(x))))
