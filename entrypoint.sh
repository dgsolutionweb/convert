#!/bin/bash

# Verificar se o diretório de downloads existe
if [ ! -d "/app/downloads" ]; then
  mkdir -p /app/downloads
  echo "Diretório de downloads criado."
fi

# Ajustar permissões
chmod -R 777 /app/downloads

# Iniciar a aplicação
exec python app.py 