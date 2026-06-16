FROM python:3.11-slim

WORKDIR /app

# Copie requirements.txt depuis siege/api (contexte Docker à la racine)
COPY siege/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code de l'API dans un sous-dossier "api" pour préserver les imports
COPY siege/api/ ./api/

ENV PYTHONPATH=/app

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
