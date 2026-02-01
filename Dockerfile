# Stage 1: Build frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend + serve frontend
FROM python:3.12-slim
WORKDIR /app

# Install git (needed for pip git dependencies) and backend dependencies
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download Skyfield ephemeris
RUN python -c "from skyfield.api import Loader; Loader('/app/backend/app/data')('de421.bsp')"

# Copy backend code
COPY backend/ ./backend/
COPY config/ ./config/

# Copy built frontend into backend static dir
COPY --from=frontend-build /app/frontend/dist ./backend/static/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app/backend"]
