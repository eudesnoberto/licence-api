# Dockerfile para Koyeb
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (cache layer)
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY api/ .

# Expor porta (Koyeb usa variável PORT)
ENV PORT=8000
EXPOSE $PORT

# Comando para iniciar
CMD python app.py

