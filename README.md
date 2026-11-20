# ☁️ CloudCoach — Asistente CLF-C02 con Amazon Bedrock

Aplicación web tipo chat (Streamlit) que conversa con un modelo fundacional de **Amazon Bedrock** (vía **LangChain**) especializado en la certificación **AWS Certified Cloud Practitioner (CLF-C02)**. Tiene tres perfiles de experto (Tutor, Examinador, Arquitecto), historial de conversación en la sesión y se ejecuta en Docker.

## Arquitectura

```
Navegador ──► Streamlit (app.py) ──► LangChain ChatBedrockConverse ──► boto3 ──HTTPS + Bearer──► Bedrock Runtime (Converse API) ──► Modelo (Claude / Nova)
                 │
                 └── st.session_state.messages  (historial por sesión)
```

## Estructura

```
├── app.py              # Interfaz de chat y flujo principal
├── src/
│   ├── config.py       # Lectura y validación de variables de entorno
│   ├── prompts.py      # Prompt base + perfiles de experto
│   └── llm.py          # Cliente Bedrock (LangChain), historial → mensajes, streaming
├── docs/PROMPTS.md     # Diseño del agente y casos de prueba
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example        # Plantilla de configuración (sin secretos)
└── .gitignore          # Excluye .env
```

## Requisitos previos
1. Cuenta de AWS con acceso a Amazon Bedrock.
2. Si usas un modelo de Anthropic: enviar una vez el formulario de caso de uso (consola de Bedrock → Model catalog → modelo de Anthropic).
3. Una **API key de Bedrock** (consola de Bedrock → *API keys*).
4. Ubuntu 22.04/24.04 con Docker Engine (y Python 3.10+ para correr sin Docker):

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER && newgrp docker
```

## Configuración

```bash
cp .env.example .env
chmod 600 .env
nano .env                 # pega tu AWS_BEARER_TOKEN_BEDROCK
```

| Variable | Obligatoria | Descripción |
|---|---|---|
| `AWS_BEARER_TOKEN_BEDROCK` | Sí | API key de Bedrock |
| `AWS_REGION` | No (us-east-1) | Región de Bedrock |
| `MODEL_ID` | No | ID del modelo / inference profile |
| `TEMPERATURE` | No (0.3) | Creatividad del modelo |
| `MAX_TOKENS` | No (1024) | Longitud máxima de cada respuesta |
| `MAX_HISTORY_MESSAGES` | No (20) | Mensajes del historial que se reenvían al modelo |

## Ejecución con Docker

```bash
docker build -t cloudcoach .
docker run --rm -p 8501:8501 --env-file .env cloudcoach
```
Abrir http://localhost:8501

> Ejecuta los comandos desde la raíz del proyecto.

## Ejecución local (sin Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Seguridad
- Ninguna credencial está en el código: todo se lee del entorno.
- `.env` está en `.gitignore` y en `.dockerignore` (no entra ni al repo ni a la imagen).
- Usa una API key de corta duración o con fecha de expiración y revócala al terminar el ejercicio.

## Errores comunes
| Error | Causa | Solución |
|---|---|---|
| `Falta la variable AWS_BEARER_TOKEN_BEDROCK` | No existe `.env` o no se pasó `--env-file` | Crear `.env` y usar `--env-file .env` |
| `AccessDeniedException` / `UnrecognizedClientException` | Key vencida, inválida o sin permisos | Generar otra key |
| `ResourceNotFoundException ... use case details` | Falta el formulario de Anthropic | Enviarlo en la consola o usar `us.amazon.nova-lite-v1:0` |
| `ValidationException ... on-demand throughput isn't supported` | Se usó el ID del modelo sin el prefijo del inference profile | Usar el ID con `us.` |
| `permission denied ... /var/run/docker.sock` | El usuario no está en el grupo `docker` | `sudo usermod -aG docker $USER` y `newgrp docker` |
| `externally-managed-environment` | `pip install` fuera del entorno virtual | `source .venv/bin/activate` |
