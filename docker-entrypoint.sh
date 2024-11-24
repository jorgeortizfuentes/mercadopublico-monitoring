#!/bin/bash
set -e

# Calcular número de workers si es auto
if [ "$WORKERS" = "auto" ]; then
    WORKERS=$(( $(nproc) * 2 + 1 ))
fi

# Inicializar la aplicación
echo "Initializing application..."
python init_app.py

# Si la inicialización fue exitosa, iniciar el servidor
if [ $? -eq 0 ]; then
    echo "Initialization successful, starting server..."
    
    # Ejecutar uvicorn con los workers calculados
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers $WORKERS \
        --loop uvloop \
        --http httptools \
        --proxy-headers \
        --forwarded-allow-ips '*' \
        --backlog ${UVICORN_BACKLOG:-2048} \
        --limit-concurrency ${UVICORN_LIMIT_CONCURRENCY:-1000} \
        --timeout-keep-alive ${UVICORN_KEEP_ALIVE:-5}
else
    echo "Initialization failed, exiting..."
    exit 1
fi
