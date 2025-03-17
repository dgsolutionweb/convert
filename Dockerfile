FROM python:3.11-slim

WORKDIR /app

# Instalar ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar arquivos do projeto
COPY . .

# Tornar o script de entrada executável
RUN chmod +x /app/entrypoint.sh

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Criar diretório para downloads
RUN mkdir -p downloads && chmod 777 downloads

# Expor a porta
EXPOSE 5000

# Definir variável de ambiente para produção
ENV FLASK_ENV=production

# Usar o script de entrada
ENTRYPOINT ["/app/entrypoint.sh"] 