# ─────────────────────────────────────────────────────────────
# CareerLens AI — Universal Production Dockerfile
# Multi-stage build: React 19 Frontend + FastAPI Backend
# Runs on Render, Koyeb, Railway, Fly.io, Hugging Face, or VPS
# ─────────────────────────────────────────────────────────────

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend with Built Frontend Assets
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend

# Copy compiled frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

WORKDIR /app/backend

EXPOSE 8000

# Shell form expands ${PORT} dynamically on Render/Railway/Fly
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
