#!/bin/bash
set -e

# Validar que las variables estén definidas
REQUIRED_VARS=("PORT" "WORKERS" "UVICORN_BACKLOG" "UVICORN_LIMIT_CONCURRENCY")

# Verificar cada variable
for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
        echo "Error: Variable $VAR no está definida o está vacía."
        exit 1
    fi
done

# Calcular número de workers si es auto
if [ "$WORKERS" = "auto" ]; then
    # Obtener cores disponibles
    CORES=$(nproc)
    
    # Limitar según número de cores
    if [ "$CORES" -le 2 ]; then
        WORKERS=$(( CORES + 1 ))
    elif [ "$CORES" -le 4 ]; then
        WORKERS=$(( CORES * 2 ))
    else
        WORKERS=8  # Máximo 8 workers
    fi
fi

# Inicializar la aplicación
echo "Initializing application..."
if ! python init_app.py; then
    echo "Initialization failed, exiting..."
    exit 1
fi

echo "Initialization successful, starting server..."

# Configuraciones de Uvicorn
UVICORN_BACKLOG=${UVICORN_BACKLOG:-2048}
UVICORN_LIMIT_CONCURRENCY=${UVICORN_LIMIT_CONCURRENCY:-1000}
UVICORN_KEEP_ALIVE=${UVICORN_KEEP_ALIVE:-5}

# Ejecutar el servidor Uvicorn
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers $WORKERS \
    --loop uvloop \
    --http httptools \
    --proxy-headers \
    --forwarded-allow-ips '*' \
    --backlog $UVICORN_BACKLOG \
    --limit-concurrency $UVICORN_LIMIT_CONCURRENCY \
    --timeout-keep-alive $UVICORN_KEEP_ALIVE