FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Required by faiss/torch runtime on Debian slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better layer caching
COPY rag_system/requirements.txt /app/rag_system/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install -r /app/rag_system/requirements.txt

# Copy app code
COPY rag_system /app/rag_system

WORKDIR /app/rag_system

# Default dataset mount point for container runs
ENV TRINETRI_DATASET_DIR=/app/datasets

CMD ["python", "main.py"]
