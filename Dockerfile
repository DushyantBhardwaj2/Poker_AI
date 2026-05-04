FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for XGBoost and Psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and packages first for better caching
COPY requirements.txt .
COPY packages/ packages/

# Install dependencies in stages to prevent OOM on small build instances
RUN pip install --no-cache-dir fastapi uvicorn pydantic sqlalchemy psycopg2-binary python-dotenv joblib
RUN pip install --no-cache-dir pandas numpy scipy
RUN pip install --no-cache-dir xgboost
RUN pip install --no-cache-dir -e ./packages/domain

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Start command with PORT variable support for Render
CMD ["sh", "-c", "uvicorn apps.api.interfaces.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
