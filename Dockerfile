# Imagen base oficial de Python, variante "slim" (Debian mínima, más liviana).
FROM python:3.12-slim

# No generar .pyc y mostrar los logs al instante (sin buffer).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Primero solo requirements: si el código cambia pero las dependencias no,
# Docker reutiliza esta capa en caché y el build es mucho más rápido.
COPY requirements.txt .
RUN pip install --default-timeout=120 --retries 10 -r requirements.txt

# Luego el código de la aplicación (.dockerignore evita copiar .env, .git, etc.).
COPY . .

# Usuario sin privilegios: buena práctica de seguridad.
RUN useradd --create-home appuser
USER appuser

# Puerto por defecto de Streamlit (solo documenta; se publica con -p).
EXPOSE 8501

# 0.0.0.0 para aceptar conexiones desde fuera del contenedor.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false"]
