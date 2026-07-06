FROM python:3.11-slim

RUN groupadd --system app && useradd --system --gid app app

WORKDIR /app

COPY requirements.txt api/
RUN pip install --no-cache-dir -r api/requirements.txt

COPY main.py config.py api/
COPY db/ api/db/
COPY models/ api/models/
COPY routes/ api/routes/
COPY services/ api/services/

RUN chown -R app:app /app

ENV PYTHONPATH=/app

USER app

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
