# Stage 1: Build the React Frontend
FROM node:20-slim AS frontend-builder

WORKDIR /app/ui
COPY ui/package.json ui/package-lock.json ./
# Use npm ci if package-lock exists, else npm install
RUN npm install

COPY ui/ ./
RUN npm run build

# Stage 2: Setup Python Backend and serve
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies if required (e.g. for numpy/torch)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all project files
COPY . /app/

# Copy the built React UI from Stage 1
COPY --from=frontend-builder /app/ui/dist /app/ui/dist

# Generate all demo .npy and .pth fixtures
RUN python tools/generate_feature_fixtures.py || true
RUN python tools/generate_frame_fixture.py || true
RUN python tools/generate_ledger_fixtures.py || true
RUN python tools/generate_trojan_fixtures.py || true
RUN python tools/generate_tta_fixtures.py || true

# Set default VAJRA environment variables
ENV VAJRA_ENVIRONMENT="production" \
    VAJRA_REQUIRE_API_KEY="false" \
    VAJRA_API_KEY="render-demo-key" \
    VAJRA_MODEL_SECRET="render-demo-secret" \
    PORT=8000

EXPOSE $PORT

# Start FastAPI and serve both backend and static frontend
CMD ["sh", "-c", "uvicorn engine.api_gateway:app --host 0.0.0.0 --port ${PORT}"]
