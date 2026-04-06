FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY ai-gym-frontend/package*.json ./
RUN npm ci

COPY ai-gym-frontend/ ./
RUN npm run build

FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user for safer runtime defaults.
RUN useradd --create-home --shell /bin/bash appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir mediapipe==0.10.14 && pip install --no-cache-dir -r requirements.txt

COPY api ./api
COPY src ./src
COPY player_profile.json ./player_profile.json
COPY ai-gym-frontend/package*.json ./ai-gym-frontend/
COPY --from=frontend-builder /frontend/build ./ai-gym-frontend/build

# MediaPipe model assets must be readable by the runtime user.
RUN chmod -R a+rX /usr/local/lib/python3.10/site-packages

# Ensure application files are readable by the runtime user.
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
