FROM python:3.11-slim

WORKDIR /app

# Copie requirements.txt depuis siege/api (contexte Docker à la racine)
COPY siege/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code de l'API depuis siege/api
COPY siege/api/ .

# Copie le certificat SSL MySQL (pour connexion Aiven)
RUN mkdir -p /app/database
COPY database/ca.pem/ca.pem /app/database/ca.pem

ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
