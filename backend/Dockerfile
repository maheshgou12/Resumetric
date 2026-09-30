FROM python:3.11-slim

WORKDIR /app

# System deps for pdfminer, psycopg2, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Shell form so Render's $PORT is honored (exec form can't expand it)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
