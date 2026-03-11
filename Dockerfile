# Minecraft Quiz Application - Docker Image
# Basierend auf Ubuntu mit Python 3.11

FROM ubuntu:22.04

# Metadaten
LABEL maintainer="Minecraft Quiz Team"
LABEL description="Minecraft Quiz Anwendung mit Flask und Textdatei-Speicher"
LABEL version="1.0.0"

# Verhindere interaktive Prompts während der Installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Setze Arbeitsverzeichnis
WORKDIR /app

# Installiere System-Abhängigkeiten und Python 3.11
RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    curl \
    ca-certificates \
    && add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Erstelle Symlinks für Python
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Kopiere pyproject.toml zuerst (für besseres Layer-Caching)
COPY pyproject.toml .



# Erstelle nicht-root Benutzer für Sicherheit
RUN useradd -m -u 1000 quizapp && \
    chown -R quizapp:quizapp /app

# Kopiere Anwendungscode
COPY --chown=quizapp:quizapp quiz/ /app/quiz/
COPY --chown=quizapp:quizapp .env.example /app/.env

# Erstelle Verzeichnis für Highscores
RUN mkdir -p /app/data && \
    chown -R quizapp:quizapp /app/data

# Wechsle zu nicht-root Benutzer
USER quizapp

# Installiere uv (schneller Python Package Installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/quizapp/.local/bin:$PATH"

# Installiere Python-Abhängigkeiten mit uv
RUN uv venv
RUN uv sync

# Exponiere Port 5000
EXPOSE 5000

# Gesundheitscheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Umgebungsvariablen
ENV FLASK_APP=quiz.anwendung
ENV FLASK_ENV=production
ENV SECRET_KEY=change-this-secret-key-in-production

# Startbefehl
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "quiz.anwendung:app"]