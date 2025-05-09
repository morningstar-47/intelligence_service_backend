# Dockerfile
FROM python:3.11-slim

WORKDIR /app/

# Définir des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Installer les dépendances système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY pyproject.toml /app/

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copier le code source
COPY . /app/

# Exécuter en tant qu'utilisateur non-root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
