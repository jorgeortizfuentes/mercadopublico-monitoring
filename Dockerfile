# Usar imagen base oficial de Python optimizada
FROM python:3.12-slim

# Argumentos de construcción
ARG BUILD_ENV=production

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

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
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python", "run.py"]
