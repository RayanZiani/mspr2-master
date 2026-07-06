FROM python:3.11-slim

RUN groupadd --system app && useradd --system --gid app app

WORKDIR /app

COPY siege/api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

COPY siege/api/main.py siege/api/config.py siege/api/auth.py siege/api/permissions.py api/
COPY siege/api/db/ api/db/
COPY siege/api/routes/ api/routes/
COPY siege/api/services/ api/services/

RUN chown -R app:app /app

ENV PYTHONPATH=/app

USER app

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
