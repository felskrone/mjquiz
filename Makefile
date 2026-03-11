.PHONY: help build run stop clean logs test health shell dev-run

# Variablen
IMAGE_NAME = minecraft-quiz
CONTAINER_NAME = minecraft-quiz
PORT = 5000

help: ## Zeige diese Hilfe
	@echo "Verfügbare Make-Befehle:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Docker Image bauen
	@echo "🔨 Baue Docker Image..."
	docker build -t $(IMAGE_NAME):latest .

run: ## Container starten
	@echo "🚀 Starte Container..."
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):5000 \
		-v $$(pwd)/data:/app/data \
		-e SECRET_KEY=$$(python -c "import secrets; print(secrets.token_hex(32))") \
		$(IMAGE_NAME):latest
	@echo "✅ Container gestartet auf http://localhost:$(PORT)"

run-interactive: ## Container interaktiv starten (für Debugging)
	@echo "🐛 Starte Container interaktiv..."
	docker run -it --rm \
		--name $(CONTAINER_NAME)-debug \
		-p $(PORT):5000 \
		-v $$(pwd)/data:/app/data \
		$(IMAGE_NAME):latest /bin/bash

compose-up: ## Mit Docker Compose starten
	@echo "🚀 Starte mit Docker Compose..."
	docker-compose up -d
	@echo "✅ Anwendung verfügbar auf http://localhost:$(PORT)"

compose-down: ## Docker Compose stoppen
	@echo "🛑 Stoppe Docker Compose..."
	docker-compose down

stop: ## Container stoppen
	@echo "🛑 Stoppe Container..."
	docker stop $(CONTAINER_NAME) || true

clean: stop ## Container und Image entfernen
	@echo "🧹 Räume auf..."
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME):latest || true

clean-all: ## Alle Images und Container entfernen
	@echo "🧹 Räume alles auf..."
	docker-compose down -v
	docker rm -f $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME):latest || true

logs: ## Container Logs anzeigen
	@echo "📋 Zeige Logs..."
	docker logs -f $(CONTAINER_NAME)

logs-compose: ## Docker Compose Logs anzeigen
	@echo "📋 Zeige Docker Compose Logs..."
	docker-compose logs -f

test: ## Health Check durchführen
	@echo "🏥 Führe Health Check durch..."
	@curl -s http://localhost:$(PORT)/health | python -m json.tool || echo "❌ Health Check fehlgeschlagen"

health: ## Container Health Status prüfen
	@echo "🏥 Health Status:"
	@docker inspect --format='{{.State.Health.Status}}' $(CONTAINER_NAME) || echo "❌ Container nicht gefunden"

shell: ## Shell im laufenden Container öffnen
	@echo "🐚 Öffne Shell im Container..."
	docker exec -it $(CONTAINER_NAME) /bin/bash

stats: ## Container Ressourcen anzeigen
	@echo "📊 Container Statistiken:"
	docker stats --no-stream $(CONTAINER_NAME)

dev-run: ## Entwicklungsmodus mit Live-Reload
	@echo "🔧 Starte im Entwicklungsmodus..."
	docker run -it --rm \
		--name $(CONTAINER_NAME)-dev \
		-p $(PORT):5000 \
		-v $$(pwd)/quiz:/app/quiz \
		-v $$(pwd)/data:/app/data \
		-e FLASK_ENV=development \
		$(IMAGE_NAME):latest

rebuild: clean build run ## Clean, Build und Run in einem Schritt

ps: ## Zeige laufende Container
	@echo "🐳 Laufende Container:"
	@docker ps --filter name=$(CONTAINER_NAME)

images: ## Zeige Images
	@echo "📦 Docker Images:"
	@docker images $(IMAGE_NAME)

size: ## Zeige Image Größe
	@echo "📦 Image Größe:"
	@docker images $(IMAGE_NAME) --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

deploy: build run ## Build und Deploy in einem Schritt
	@echo "✅ Deployment abgeschlossen!"
	@make test

full-test: build ## Vollständiger Test: Build, Run, Test, Clean
	@echo "🧪 Starte vollständigen Test..."
	@make run
	@sleep 5
	@make test
	@make stop
	@echo "✅ Test abgeschlossen!"
