# Stage 1: Build the React frontend
FROM node:20-slim AS frontend
WORKDIR /site
COPY project/site/package*.json ./
RUN npm install
COPY project/site/ ./
RUN npm run build

# Stage 2: Python app
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    libgl1 \
    libglu1-mesa \
    libxrender1 \
    libxcursor1 \
    libxi6 \
    libxinerama1 \
    libxrandr2 \
    libxft2 \
    libsm6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY project/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY project/ .
COPY --from=frontend /site/dist ./site/dist

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "120"]