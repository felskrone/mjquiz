# Minecraft Quiz Anwendung

Eine webbasierte Minecraft-Quiz-Anwendung, die mit Flask entwickelt wurde und Ihr Wissen über Minecraft testet sowie die Top 10 Highscores verfolgt.

## Funktionen

- 🎮 Interaktives Multiple-Choice-Quiz mit 15 Minecraft-Fragen
- 🏆 Top 10 Highscore-Bestenliste
- 💾 Textdatei-Speicher für Ergebnis-Persistenz
- 🎨 Minecraft-thematisches UI-Design
- 📱 Responsives Design für Mobilgeräte und Desktop
- ☁️ Bereit für Deployment auf Render.com
- 🇩🇪 Vollständig in Deutsch implementiert (Code)

## Projektstruktur

```
/workspace/
├── quiz/                      # Hauptanwendung
│   ├── __init__.py           # Python-Paket-Marker
│   ├── anwendung.py          # Flask-Hauptanwendung
│   ├── datenbank.py          # Textdatei-Operationen
│   ├── quiz_lader.py         # Fragen-Parser
│   ├── questions.txt         # Quiz-Fragen-Daten
│   ├── highscores.txt        # Top 10 Highscores
│   ├── templates/            # HTML-Templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── quiz.html
│   │   └── results.html
│   └── static/               # Statische Dateien
│       └── css/
│           └── style.css
├── pyproject.toml            # Python-Abhängigkeiten & Projektkonfiguration
├── render.yaml               # Render.com Deployment-Konfiguration
└── .env.example              # Umgebungsvariablen-Vorlage
```

## Lokale Entwicklung

### Voraussetzungen

- Python 3.11 oder höher
- uv oder pip Paketmanager

### Installation

1. Repository klonen:
```bash
cd /workspace
```

2. Virtuelle Umgebung erstellen:
```bash
python -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate
```

3. Abhängigkeiten installieren:

**Mit uv (empfohlen - schneller):**
```bash
uv pip install .
```

**Mit pip:**
```bash
pip install .
```

4. `.env`-Datei aus der Vorlage erstellen:
```bash
cp .env.example .env
```

5. `.env` bearbeiten und SECRET_KEY setzen:
```
SECRET_KEY=ihr-geheimer-schluessel-hier
```

**Secret Key generieren:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Anwendung starten

**Option 1: Direkt mit Python**
```bash
python -m quiz.anwendung
```

**Option 2: Mit UV**
```bash
uv run python -m quiz.anwendung
```

**Option 3: Mit Task (empfohlen)**
```bash
task run              # Normale Ausführung
task dev              # Entwicklungsmodus
task serve            # Produktion mit Gunicorn
```

Die Anwendung ist dann verfügbar unter: **http://localhost:5000**

### Task installieren (optional)

```bash
# macOS
brew install go-task

# Linux
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d

# Weitere Optionen: https://taskfile.dev/installation/
```

## Deployment auf Render.com

### Automatisches Deployment

1. Account auf [Render.com](https://render.com) erstellen
2. GitHub-Repository verbinden
3. Render erkennt automatisch die `render.yaml`-Datei und richtet den Service ein
4. Die SECRET_KEY-Umgebungsvariable wird automatisch generiert
5. Ihre App wird deployed

### Manuelles Deployment

1. Neuen Web Service auf Render.com erstellen
2. Service konfigurieren:
   - **Umgebung**: Python
   - **Build-Befehl**: `pip install .`
   - **Start-Befehl**: `gunicorn quiz.anwendung:app`
   - **Python-Version**: 3.11
3. Umgebungsvariable hinzufügen:
   - **SECRET_KEY**: (Sicheren zufälligen Schlüssel generieren)
4. Deployen!

## Neue Fragen hinzufügen

Bearbeiten Sie die `quiz/questions.txt`-Datei nach folgendem Format:

```
Question1: What is the primary material used to craft a crafting table?
Answer 1: Stone
Answer 2: Iron
Answer 3: Wood
Answer 4: Diamond
Correct Answer: 3

Question2: How many obsidian blocks are needed...
Answer 1: 8 blocks
Answer 2: 10 blocks
Answer 3: 12 blocks
Answer 4: 14 blocks
Correct Answer: 2
```

**Format-Regeln:**
- Jede Frage muss genau 6 Zeilen haben
- Fragen durch Leerzeile trennen
- Korrekte Antwort muss eine Zahl von 1-4 sein
- Fragen-Nummerierung (Question1, Question2, etc.) sollte fortlaufend sein

## Datenspeicherung

Die Anwendung verwendet eine Textdatei zum Speichern von Highscores:
- **Datei**: `quiz/highscores.txt`
- **Format**: Pipe-delimitiert (|)
- **Felder**: spieler_name, punktzahl, gesamte_fragen, prozentsatz, abgeschlossen_am
- **Automatik**: Behält nur die Top 10 Ergebnisse

**Vorteile:**
- ✅ Einfach zu debuggen und inspizieren
- ✅ Keine Datenbank-Setup erforderlich
- ✅ Bessere Persistenz auf Render.com Free Tier
- ✅ Human-readable Format

## API-Endpunkte

- `GET /` - Startseite mit Highscores
- `POST /start` - Quiz-Session initialisieren
- `GET /quiz` - Aktuelle Frage anzeigen
- `POST /submit` - Antwort absenden und fortfahren
- `GET /results` - Endergebnisse anzeigen
- `GET /health` - Health-Check-Endpunkt

**Health-Check-Antwort:**
```json
{
  "status": "healthy",
  "geladene_fragen": 15
}
```

## Verwendete Technologien

- **Backend**: Flask 3.0.0
- **Datenspeicher**: Textdatei (pipe-delimitiert)
- **Server**: Gunicorn 21.2.0
- **Frontend**: HTML, CSS (Minecraft-Theme)
- **Deployment**: Render.com
- **Paketmanager**: UV (10-100x schneller als pip)

## Sicherheitsfeatures

- ✅ Session-basiertes Quiz-State-Management
- ✅ Eingabevalidierung für Spielernamen und Antworten
- ✅ Atomare Datei-Schreiboperationen
- ✅ Umgebungsbasierte Secret-Key-Konfiguration
- ✅ CSRF-Schutz via Flask-Sessions
- ✅ Health-Checks für Monitoring

## Tests durchführen

Führen Sie die Anwendung lokal aus und testen Sie:

1. Ein Quiz abschließen und überprüfen, ob Ergebnis gespeichert wird
2. 11+ Quizze mit verschiedenen Punktzahlen absolvieren
3. Überprüfen, dass nur Top 10 Ergebnisse behalten werden
4. Edge-Cases testen (leerer Name, ungültige Antworten)
5. Auf mehreren Browsern und Geräten testen

**Health-Check:**
```bash
curl http://localhost:5000/health
```

## Code-Besonderheiten

Diese Anwendung ist vollständig in **Deutsch** implementiert:

- ✅ Alle Funktionsnamen auf Deutsch (z.B. `initialisiere_speicher()`, `lade_quiz_fragen()`)
- ✅ Alle Variablennamen auf Deutsch (z.B. `spieler_name`, `punktzahl`, `frage`)
- ✅ Alle Klassennamen auf Deutsch (z.B. `QuizFrage`)
- ✅ Alle Docstrings auf Deutsch mit Google-Style Format
- ✅ Alle Kommentare auf Deutsch
- ✅ Dictionary-Keys auf Deutsch
- ✅ Session-Variablen auf Deutsch

**Beispiel:**
```python
def speichere_ergebnis(spieler_name: str, punktzahl: int, gesamte_fragen: int) -> None:
    """Speichere ein Quiz-Ergebnis und behalte nur die Top 10 Ergebnisse.

    Argumente:
        spieler_name: Der Name des Spielers.
        punktzahl: Anzahl der richtigen Antworten.
        gesamte_fragen: Gesamtzahl der Fragen im Quiz.
    """
```

## Performance

Diese Anwendung verwendet **UV** anstelle von pip:
- ⚡ 10-100x schneller bei der Paketinstallation
- 🦀 In Rust geschrieben (von Astral/Ruff-Team)
- 🎯 Bessere Dependency-Resolution
- 📦 Kleinerer Cache-Footprint

## Mitwirken

Dies ist ein persönliches Projekt. Fühlen Sie sich frei, es zu forken und für eigene Zwecke zu modifizieren!

## Lizenz

Dieses Projekt ist Open Source und für Bildungszwecke verfügbar.

## Support

Für Probleme oder Fragen erstellen Sie bitte ein Issue im Repository.

## Changelog

### Version 1.0.0
- ✅ SQLite zu Textdatei-Speicher konvertiert
- ✅ Code nach `/quiz` reorganisiert
- ✅ Vollständige deutsche Implementierung
- ✅ Einfaches Setup ohne Docker
- ✅ UV-Integration für schnelle Installation

---

**Generiert mit AI (Copilot oder Claude)**
