FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Ensure the application package is importable
ENV PYTHONPATH=/app

RUN groupadd -r app && useradd --no-log-init -r -g app app

WORKDIR /app

# install build deps then python deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# ensure gunicorn is available for production server (use a specific version)
RUN pip install --no-cache-dir gunicorn==20.1.0

COPY . /app
RUN chown -R app:app /app

USER app
EXPOSE 8080

# Use gunicorn with uvicorn workers for production-like server
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8080", "app.main:app"]
