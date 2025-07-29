FROM python:3.13-slim

ARG MONGO_DB_NAME
ARG MONGO_URL

ENV MONGO_DB_NAME=${MONGO_DB_NAME}
ENV MONGO_URL=${MONGO_URL}
ENV ADMIN_INITIAL_USERNAME=${ADMIN_INITIAL_USERNAME}
ENV ADMIN_INITIAL_PASSWORD=${ADMIN_INITIAL_PASSWORD}
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV HF_HOME=/app/cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/cache/sentence_transformers
ENV HF_HUB_CACHE=/app/cache/huggingface/hub

# Criar usuário e diretórios
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/cache/huggingface /app/cache/sentence_transformers

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN addgroup --system app && adduser --system --group app

COPY . .

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

RUN python scripts/init_data.py

RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]