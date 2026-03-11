# Docker Deployment Guide

Diese Anleitung erklärt, wie man die Minecraft Quiz Anwendung mit Docker betreibt.

## 🐳 Voraussetzungen

- Docker Engine 20.10+ oder Docker Desktop
- Docker Compose 2.0+ (optional, aber empfohlen)

## ⚡ Besonderheiten

Diese Docker-Images verwenden **uv** statt pip für die Installation von Python-Paketen:
- ✅ Bis zu 10-100x schnellere Paket-Installation
- ✅ Besseres Dependency Resolution
- ✅ Kleinerer Image Footprint
- ✅ Von Astral (Ruff-Entwickler)

## 🚀 Schnellstart mit Docker Compose

### 1. Repository klonen oder herunterladen

```bash
git clone <repository-url>
cd minecraft-quiz
```

### 2. Anwendung starten

```bash
docker-compose up -d
```

Die Anwendung ist nun verfügbar unter: http://localhost:5000

### 3. Logs anzeigen

```bash
docker-compose logs -f minecraft-quiz
```

### 4. Anwendung stoppen

```bash
docker-compose down
```

## 🔨 Manueller Docker Build & Run

### Image bauen

```bash
docker build -t minecraft-quiz:latest .
```

### Container starten

```bash
docker run -d \
  --name minecraft-quiz \
  -p 5000:5000 \
  -e SECRET_KEY="your-secret-key-here" \
  -v $(pwd)/data:/app/data \
  minecraft-quiz:latest
```

### Container verwalten

```bash
# Status prüfen
docker ps

# Logs anzeigen
docker logs -f minecraft-quiz

# Container stoppen
docker stop minecraft-quiz

# Container entfernen
docker rm minecraft-quiz

# Image entfernen
docker rmi minecraft-quiz:latest
```

## 🔧 Konfiguration

### Umgebungsvariablen

Erstelle eine `.env` Datei im Projektverzeichnis:

```bash
SECRET_KEY=dein-geheimer-schluessel-hier
FLASK_ENV=production
```

Dann starte mit:

```bash
docker-compose --env-file .env up -d
```

### Verfügbare Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `SECRET_KEY` | Flask Secret Key für Sessions | `change-this-secret-key-in-production` |
| `FLASK_ENV` | Flask Umgebung | `production` |
| `FLASK_APP` | Flask App Modul | `quiz.anwendung` |

## 📊 Persistente Daten

Die Highscores werden in einer Textdatei gespeichert. Um diese Daten zu persistieren:

### Mit Docker Compose (automatisch)

```yaml
volumes:
  - ./data:/app/data
```

Die Highscores werden in `./data/` auf dem Host gespeichert.

### Mit Docker Run

```bash
docker run -d \
  -v $(pwd)/data:/app/data \
  minecraft-quiz:latest
```

## 🏥 Health Check

Der Container enthält einen eingebauten Health Check:

```bash
# Status prüfen
docker inspect --format='{{.State.Health.Status}}' minecraft-quiz

# Health Check manuell ausführen
docker exec minecraft-quiz curl -f http://localhost:5000/health
```

Erwartete Antwort:
```json
{
  "status": "healthy",
  "geladene_fragen": 15
}
```

## 🔍 Debugging

### In Container einloggen

```bash
docker exec -it minecraft-quiz /bin/bash
```

### Logs in Echtzeit anzeigen

```bash
docker logs -f minecraft-quiz
```

### Ressourcennutzung prüfen

```bash
docker stats minecraft-quiz
```

## 🚢 Produktion Deployment

### 1. Sicheren Secret Key generieren

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Mit Secret Key starten

```bash
docker run -d \
  --name minecraft-quiz \
  -p 5000:5000 \
  -e SECRET_KEY="<generierter-key>" \
  -v /var/minecraft-quiz/data:/app/data \
  --restart unless-stopped \
  minecraft-quiz:latest
```

### 3. Mit Reverse Proxy (Nginx)

Beispiel Nginx-Konfiguration:

```nginx
server {
    listen 80;
    server_name quiz.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔄 Updates

### Image aktualisieren

```bash
# Neuestes Image pullen
docker pull minecraft-quiz:latest

# Container neu erstellen
docker-compose down
docker-compose up -d
```

### Rollback

```bash
# Vorherige Version wiederherstellen
docker tag minecraft-quiz:latest minecraft-quiz:backup
docker-compose down
docker-compose up -d
```

## 🧪 Testing

### Image lokal testen

```bash
# Build
docker build -t minecraft-quiz:test .

# Run mit Test-Port
docker run -d -p 8080:5000 --name quiz-test minecraft-quiz:test

# Test
curl http://localhost:8080/health

# Cleanup
docker stop quiz-test && docker rm quiz-test
```

## 📦 Image-Größe

Das fertige Image hat ca. 250-350 MB Größe:

```bash
docker images minecraft-quiz
```

## 🆘 Troubleshooting

### Port bereits in Verwendung

```bash
# Anderen Port verwenden
docker run -p 8080:5000 minecraft-quiz:latest
```

### Container startet nicht

```bash
# Logs prüfen
docker logs minecraft-quiz

# Interaktiv starten für Debugging
docker run -it --rm minecraft-quiz:latest /bin/bash
```

### Datei-Berechtigungen

Wenn Highscores nicht gespeichert werden:

```bash
# Berechtigungen korrigieren
sudo chown -R 1000:1000 ./data
```

## 🔐 Sicherheit

- ✅ Nicht-Root-Benutzer (UID 1000)
- ✅ Minimale System-Abhängigkeiten
- ✅ Health Checks integriert
- ✅ Secrets via Umgebungsvariablen
- ✅ Read-only Filesystem möglich

### Read-Only Filesystem

```bash
docker run -d \
  --read-only \
  --tmpfs /tmp \
  -v $(pwd)/data:/app/data \
  minecraft-quiz:latest
```

## 📚 Weitere Ressourcen

- [Docker Dokumentation](https://docs.docker.com/)
- [Docker Compose Dokumentation](https://docs.docker.com/compose/)
- [Flask in Production](https://flask.palletsprojects.com/en/3.0.x/deploying/)
