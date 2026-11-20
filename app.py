"""CloudCoach: asistente conversacional para el AWS Cloud Practitioner (CLF-C02).

Interfaz de chat en Streamlit + modelo fundacional en Amazon Bedrock (vía LangChain).
Ejecutar:  streamlit run app.py
"""

import streamlit as st
from botocore.exceptions import BotoCoreError, ClientError

from src.config import get_settings
from src.llm import build_messages, create_llm, stream_reply
from src.prompts import DEFAULT_PROFILE, PROFILES, WELCOME_MESSAGE, build_system_prompt

st.set_page_config(page_title="CloudCoach · AWS CLF-C02", page_icon="☁️", layout="centered")

# ---------- 1. Configuración (se detiene con un mensaje claro si falta algo) ----------
try:
    settings = get_settings()
except ValueError as err:
    st.error(str(err))
    st.stop()


# El cliente del modelo se crea una sola vez y se reutiliza entre recargas.
# Streamlit re-ejecuta el script completo en cada interacción; sin la caché se crearía un cliente nuevo en cada mensaje.
@st.cache_resource
def get_llm():
    return create_llm(settings)


llm = get_llm()

# ---------- 2. Estado de la sesión (historial de conversación) ----------
# st.session_state sobrevive a las re-ejecuciones del script mientras la pestaña
# del navegador siga abierta. Cada usuario/pestaña tiene su propio historial.
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"|"assistant", "content": str}]
if "profile" not in st.session_state:
    st.session_state.profile = DEFAULT_PROFILE

# ---------- 3. Barra lateral: perfil de experto y controles ----------
with st.sidebar:
    st.header("⚙️ Perfil del experto")
    profile = st.radio(
        "¿Cómo quieres que te ayude?",
        options=list(PROFILES.keys()),
        format_func=lambda p: f"{PROFILES[p]['icon']} {p}",
        key="profile",
    )
    st.caption(PROFILES[profile]["description"])

    st.divider()
    if st.button("🗑️ Nueva conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(f"Modelo: `{settings.model_id}`")
    st.caption(f"Región: `{settings.aws_region}`")
    st.caption(f"Mensajes en el historial: {len(st.session_state.messages)}")

# ---------- 4. Área de chat ----------
st.title("☁️ CloudCoach")
st.caption("Asistente para preparar el AWS Certified Cloud Practitioner (CLF-C02)")

with st.chat_message("assistant", avatar="☁️"):
    st.markdown(WELCOME_MESSAGE)

# Repinta todo el historial (Streamlit borra la pantalla en cada re-ejecución).
for msg in st.session_state.messages:
    avatar = "☁️" if msg["role"] == "assistant" else "🧑‍🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Sugerencias rápidas solo cuando la conversación está vacía.
suggestion = None
if not st.session_state.messages:
    cols = st.columns(3)
    examples = [
        "¿Qué es el modelo de responsabilidad compartida?",
        "Hazme una pregunta de práctica sobre precios",
        "¿Cuándo usar S3 vs EBS vs EFS?",
    ]
    for col, text in zip(cols, examples):
        if col.button(text, use_container_width=True):
            suggestion = text

prompt = st.chat_input("Escribe tu pregunta sobre AWS…") or suggestion

if prompt:
    # 4.1 Guardar y mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    # 4.2 Construir el contexto: system prompt del perfil + historial reciente
    messages = build_messages(
        build_system_prompt(profile),
        st.session_state.messages,
        settings.max_history_messages,
    )

    # 4.3 Llamar a Bedrock y mostrar la respuesta en streaming
    with st.chat_message("assistant", avatar="☁️"):
        try:
            reply = st.write_stream(stream_reply(llm, messages))
        except ClientError as err:
            code = err.response.get("Error", {}).get("Code", "Error")
            reply = None
            st.error(f"Bedrock respondió con un error ({code}): {err.response['Error'].get('Message', err)}")
        except BotoCoreError as err:
            reply = None
            st.error(f"No se pudo conectar con Bedrock: {err}")

    # 4.4 Guardar la respuesta en el historial (solo si hubo respuesta)
    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()  # repinta desde el historial (oculta las sugerencias iniciales)
    else:
        # Se quita la pregunta sin respuesta para no dejar el historial inconsistente.
        st.session_state.messages.pop()
