"""Configuración de la aplicación (factor III de Twelve-Factor: config en el entorno).

Todos los valores se leen del .env (en local) o de --env-file (en Docker).
No hay valores por defecto en el código: si falta una variable, la app se
detiene con un mensaje que dice cuál es.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Carga el .env. override=False: si la variable ya viene del entorno (Docker), esa gana.
load_dotenv(override=False)

REQUIRED_VARS = [
    "AWS_BEARER_TOKEN_BEDROCK",
    "AWS_REGION",
    "MODEL_ID",
    "TEMPERATURE",
    "MAX_TOKENS",
    "MAX_HISTORY_MESSAGES",
]


@dataclass(frozen=True)
class Settings:
    aws_region: str
    model_id: str
    temperature: float
    max_tokens: int
    max_history_messages: int


def get_settings() -> Settings:
    """Lee y valida la configuración. Lanza ValueError si falta o es inválida."""
    missing = [name for name in REQUIRED_VARS if not os.getenv(name)]
    if missing:
        raise ValueError(
            f"Faltan variables en el .env: {', '.join(missing)}. "
            "Copia .env.example a .env y completa todos los valores."
        )

    try:
        return Settings(
            aws_region=os.environ["AWS_REGION"],
            model_id=os.environ["MODEL_ID"],
            temperature=float(os.environ["TEMPERATURE"]),
            max_tokens=int(os.environ["MAX_TOKENS"]),
            max_history_messages=int(os.environ["MAX_HISTORY_MESSAGES"]),
        )
    except ValueError as err:
        raise ValueError(
            "TEMPERATURE debe ser un número decimal (ej. 0.3) y MAX_TOKENS y "
            f"MAX_HISTORY_MESSAGES números enteros (ej. 1024 y 20). Detalle: {err}"
        ) from err
