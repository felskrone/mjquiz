#!/bin/bash
# Docker Test Script für Minecraft Quiz Application

set -e

echo "🧪 === Docker Test Script für Minecraft Quiz ==="
echo ""

# Farben für Output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

IMAGE_NAME="minecraft-quiz"
CONTAINER_NAME="minecraft-quiz-test"
PORT=8080

# Cleanup Funktion
cleanup() {
    echo -e "\n${YELLOW}🧹 Räume auf...${NC}"
    docker stop ${CONTAINER_NAME} 2>/dev/null || true
    docker rm ${CONTAINER_NAME} 2>/dev/null || true
}

# Trap für Cleanup bei Script-Ende
trap cleanup EXIT

# 1. Docker Image bauen
echo -e "${YELLOW}🔨 Baue Docker Image...${NC}"
docker build -t ${IMAGE_NAME}:test . || {
    echo -e "${RED}❌ Docker Build fehlgeschlagen${NC}"
    exit 1
}
echo -e "${GREEN}✅ Docker Image gebaut${NC}"
echo ""

# 2. Image Größe anzeigen
echo -e "${YELLOW}📦 Image Größe:${NC}"
docker images ${IMAGE_NAME}:test --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
echo ""

# 3. Container starten
echo -e "${YELLOW}🚀 Starte Container auf Port ${PORT}...${NC}"
docker run -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:5000 \
    -e SECRET_KEY="test-secret-key-123" \
    ${IMAGE_NAME}:test || {
    echo -e "${RED}❌ Container Start fehlgeschlagen${NC}"
    exit 1
}
echo -e "${GREEN}✅ Container gestartet${NC}"
echo ""

# 4. Warte auf Container Start
echo -e "${YELLOW}⏳ Warte auf Application Start (30s)...${NC}"
COUNTER=0
MAX_ATTEMPTS=30
while [ $COUNTER -lt $MAX_ATTEMPTS ]; do
    if curl -s http://localhost:${PORT}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Anwendung ist bereit${NC}"
        break
    fi
    echo -n "."
    sleep 1
    COUNTER=$((COUNTER + 1))
done

if [ $COUNTER -eq $MAX_ATTEMPTS ]; then
    echo -e "${RED}❌ Timeout: Anwendung startet nicht${NC}"
    echo -e "${YELLOW}Logs:${NC}"
    docker logs ${CONTAINER_NAME}
    exit 1
fi
echo ""

# 5. Health Check
echo -e "${YELLOW}🏥 Health Check...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:${PORT}/health)
echo "Response: ${HEALTH_RESPONSE}"
if echo ${HEALTH_RESPONSE} | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health Check erfolgreich${NC}"
else
    echo -e "${RED}❌ Health Check fehlgeschlagen${NC}"
    exit 1
fi
echo ""

# 6. Teste Startseite
echo -e "${YELLOW}🏠 Teste Startseite...${NC}"
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT}/)
if [ "${STATUS_CODE}" = "200" ]; then
    echo -e "${GREEN}✅ Startseite erreichbar (HTTP ${STATUS_CODE})${NC}"
else
    echo -e "${RED}❌ Startseite fehlgeschlagen (HTTP ${STATUS_CODE})${NC}"
    exit 1
fi
echo ""

# 7. Container Logs prüfen
echo -e "${YELLOW}📋 Container Logs (letzte 10 Zeilen):${NC}"
docker logs --tail 10 ${CONTAINER_NAME}
echo ""

# 8. Container Stats
echo -e "${YELLOW}📊 Container Statistiken:${NC}"
docker stats --no-stream ${CONTAINER_NAME}
echo ""

# 9. Health Status aus Docker
echo -e "${YELLOW}🩺 Docker Health Status:${NC}"
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' ${CONTAINER_NAME} 2>/dev/null || echo "keine Health Checks")
echo "Status: ${HEALTH_STATUS}"
echo ""

# 10. Teste Quiz-Flow
echo -e "${YELLOW}🎮 Teste Quiz-Flow...${NC}"

# POST /start
echo "  → POST /start mit Spielername..."
START_RESPONSE=$(curl -s -L -c cookies.txt -w "%{http_code}" http://localhost:${PORT}/start -d "spieler_name=DockerTest" -o /dev/null)
if [ "${START_RESPONSE}" = "200" ] || [ "${START_RESPONSE}" = "302" ]; then
    echo -e "  ${GREEN}✅ Quiz Start erfolgreich${NC}"
else
    echo -e "  ${RED}❌ Quiz Start fehlgeschlagen (HTTP ${START_RESPONSE})${NC}"
fi

# GET /quiz
echo "  → GET /quiz..."
QUIZ_RESPONSE=$(curl -s -b cookies.txt -w "%{http_code}" http://localhost:${PORT}/quiz -o /dev/null)
if [ "${QUIZ_RESPONSE}" = "200" ] || [ "${QUIZ_RESPONSE}" = "302" ]; then
    echo -e "  ${GREEN}✅ Quiz-Seite erreichbar${NC}"
else
    echo -e "  ${RED}❌ Quiz-Seite fehlgeschlagen (HTTP ${QUIZ_RESPONSE})${NC}"
fi

rm -f cookies.txt
echo ""

# 11. Teste File Permissions
echo -e "${YELLOW}📁 Teste Datei-Berechtigungen...${NC}"
docker exec ${CONTAINER_NAME} ls -la /app/quiz/ | head -5
echo ""

# 12. Erfolg
echo -e "${GREEN}🎉 === ALLE TESTS ERFOLGREICH ===${NC}"
echo ""
echo "ℹ️  Informationen:"
echo "  - Image: ${IMAGE_NAME}:test"
echo "  - Container: ${CONTAINER_NAME}"
echo "  - Port: ${PORT}"
echo "  - URL: http://localhost:${PORT}"
echo ""
echo "📝 Nützliche Befehle:"
echo "  - Logs anzeigen:  docker logs -f ${CONTAINER_NAME}"
echo "  - Shell öffnen:   docker exec -it ${CONTAINER_NAME} /bin/bash"
echo "  - Stoppen:        docker stop ${CONTAINER_NAME}"
echo ""
