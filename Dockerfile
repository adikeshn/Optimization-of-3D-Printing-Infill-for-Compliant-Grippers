# Stage 1: Build the React frontend
FROM node:20-slim AS frontend
WORKDIR /site
COPY project/site/package*.json ./
RUN npm install
COPY project/site/ ./
RUN npm run build

# Stage 2: Lightweight Python API
FROM python:3.11-slim

WORKDIR /app

COPY project/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY project/ .
COPY --from=frontend /site/dist ./site/dist

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "60", "--workers", "2"]