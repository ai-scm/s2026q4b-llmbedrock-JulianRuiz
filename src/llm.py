"""Integración con Amazon Bedrock a través de LangChain (Parte B).

ChatBedrockConverse usa por debajo el cliente boto3 "bedrock-runtime" y la
Converse API de Bedrock, que tiene el mismo formato de mensajes para todos los
modelos (Claude, Nova, Llama...). Cambiar de modelo = cambiar MODEL_ID.

Autenticación: boto3 detecta la variable AWS_BEARER_TOKEN_BEDROCK y envía la
API key como cabecera "Authorization: Bearer ...". Por eso aquí no se pasa
ninguna credencial explícita.
"""

from collections.abc import Iterator

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.config import Settings


def create_llm(settings: Settings) -> ChatBedrockConverse:
    """Crea el cliente del modelo fundacional."""
    return ChatBedrockConverse(
        model=settings.model_id,
        region_name=settings.aws_region,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
    )


def build_messages(
    system_prompt: str, history: list[dict], max_history: int
) -> list[BaseMessage]:
    """Convierte el historial de Streamlit (lista de dicts) en mensajes de LangChain.

    El modelo NO tiene memoria: en cada llamada le reenviamos el system prompt
    """
    recent = history[-max_history:]
    # La Converse API exige que la conversación empiece con un mensaje del usuario.
    while recent and recent[0]["role"] != "user":
        recent = recent[1:]

    messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
    for msg in recent:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    return messages


def _chunk_text(content) -> str:
    """Extrae el texto de un fragmento."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def stream_reply(llm: ChatBedrockConverse, messages: list[BaseMessage]) -> Iterator[str]:
    """Devuelve la respuesta en fragmentos (streaming) para mostrarla mientras se genera."""
    for chunk in llm.stream(messages):
        text = _chunk_text(chunk.content)
        if text:
            yield text
