FROM python:3.11-slim

WORKDIR /app

# Copy application code
COPY src/decentralis-announcement-server/ /app

# Keep Python output unbuffered (helpful for logs)
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/* || true

CMD ["python", "main.py"]
