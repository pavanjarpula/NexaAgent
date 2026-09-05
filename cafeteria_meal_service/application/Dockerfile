FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir fastapi uvicorn "weaviate-client>=4.0.0" pandas httpx

COPY . .

CMD ["uvicorn", "application.main:app", "--host", "0.0.0.0", "--port", "8000"]
