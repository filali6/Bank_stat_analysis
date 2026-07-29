FROM python:3.11-slim

WORKDIR /app

# Copier seulement requirements.txt d'abord : Docker met cette étape en
# cache tant que les dépendances ne changent pas, donc les rebuilds
# pendant le dev (juste du code modifié) sont rapides.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
