FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt api/
RUN pip install --no-cache-dir -r api/requirements.txt

COPY . api/

ENV PYTHONPATH=/app

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
