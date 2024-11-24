# Usar imagen base oficial de Python optimizada
FROM python:3.12-slim

# Argumentos de construcción
ARG BUILD_ENV=production
ARG WORKERS=auto

# Variables de entorno para Python y Uvicorn
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    WORKERS=${WORKERS} \
    PORT=5353

# Crear usuario no root
RUN useradd -m -s /bin/bash app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios necesarios
WORKDIR /app
RUN mkdir -p /app/data /app/db && \
    chown -R app:app /app

# Copiar requirements e instalar dependencias
COPY --chown=app:app requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY --chown=app:app . .

# Cambiar al usuario no root
USER app

# Puerto de la aplicación
EXPOSE ${PORT}

# Script de inicio para configurar workers
COPY --chown=app:app docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Usar script de entrada para configurar workers
ENTRYPOINT ["/docker-entrypoint.sh"]

# docker build -t mp-monitoring .
# docker run -p 5353:5353 mp-monitoring