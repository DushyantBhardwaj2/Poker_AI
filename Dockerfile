FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for XGBoost and Psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install the local domain package in editable mode for the container
RUN pip install -e ./packages/domain

# Expose the port FastAPI will run on
EXPOSE 8000

# Start command
CMD ["uvicorn", "apps.api.interfaces.main:app", "--host", "0.0.0.0", "--port", "8000"]
