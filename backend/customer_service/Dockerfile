# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# System deps needed by some wheels (e.g. psycopg2-binary)
RUN apt-get update -y && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps first (better layer caching)
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# App code
COPY . /app

ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Change the module below if your FastAPI app lives elsewhere
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
