FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
COPY libs ./libs
COPY services/api_service/requirements.txt ./service-requirements.txt

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r service-requirements.txt && \
    pip install --no-cache-dir ./libs/consultantos_core

COPY consultantos ./consultantos
COPY services/api_service/main.py ./main.py

ENV PYTHONPATH="/app"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
