"""Haupt-Flask-Anwendung für das Minecraft-Quiz.

Diese Anwendung bietet eine webbasierte Quiz-Schnittstelle mit Ergebnis-Tracking
und Highscore-Anzeige.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

from .datenbank import initialisiere_speicher, speichere_ergebnis, hole_top_10_ergebnisse
from .quiz_lader import lade_quiz_fragen, QuizFrage


# Lade Umgebungsvariablen
load_dotenv()

# Initialisiere Flask-App
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Lade Quiz-Fragen beim Start
QUIZ_FRAGEN = []


def initialisiere_anwendung() -> None:
    """Initialisiere die Anwendung: Speicher und Fragen laden."""
    global QUIZ_FRAGEN

    # Initialisiere Speicher
    initialisiere_speicher()

    # Lade Quiz-Fragen
    try:
        QUIZ_FRAGEN = lade_quiz_fragen()
        print(f"✅ {len(QUIZ_FRAGEN)} Quiz-Fragen geladen")
    except Exception as e:
        print(f"❌ Fehler beim Laden der Quiz-Fragen: {e}")
        raise


@app.route('/')
def index():
    """Startseite mit Top 10 Highscores und Quiz-Start-Formular.

    Rückgabe:
        Gerendertes index.html Template.
    """
    top_ergebnisse = hole_top_10_ergebnisse()
    return render_template('index.html', top_ergebnisse=top_ergebnisse)


@app.route('/start', methods=['POST'])
def start():
    """Initialisiere Quiz-Session mit Spielername.

    Rückgabe:
        Weiterleitung zur Quiz-Seite oder Startseite bei Fehler.
    """
    spieler_name = request.form.get('spieler_name', '').strip()

    # Validiere Spielername
    if not spieler_name:
        flash('Bitte gib deinen Namen ein, um das Quiz zu starten.', 'error')
        return redirect(url_for('index'))

    if len(spieler_name) > 50:
        flash('Name muss 50 Zeichen oder weniger sein.', 'error')
        return redirect(url_for('index'))

    # Initialisiere Session
    session['spieler_name'] = spieler_name
    session['aktuelle_fragen_index'] = 0
    session['punktzahl'] = 0
    session['gesamte_fragen'] = len(QUIZ_FRAGEN)
    session['quiz_gestartet'] = True

    return redirect(url_for('quiz'))


@app.route('/quiz')
def quiz():
    """Zeige aktuelle Quiz-Frage an.

    Rückgabe:
        Gerendertes quiz.html Template oder Weiterleitung bei ungültiger Session.
    """
    # Prüfe ob Quiz-Session gültig ist
    if not session.get('quiz_gestartet'):
        flash('Bitte starte ein neues Quiz.', 'error')
        return redirect(url_for('index'))

    aktuelle_index = session.get('aktuelle_fragen_index', 0)
    gesamte_fragen = session.get('gesamte_fragen', 0)

    # Prüfe ob Quiz abgeschlossen ist
    if aktuelle_index >= gesamte_fragen:
        return redirect(url_for('results'))

    # Hole aktuelle Frage
    frage = QUIZ_FRAGEN[aktuelle_index]
    fragen_nummer = aktuelle_index + 1

    return render_template(
        'quiz.html',
        frage=frage,
        fragen_nummer=fragen_nummer,
        gesamte_fragen=gesamte_fragen
    )


@app.route('/submit', methods=['POST'])
def submit():
    """Verarbeite Antwort-Übermittlung und gehe zur nächsten Frage.

    Rückgabe:
        Weiterleitung zur nächsten Frage oder Ergebnisseite.
    """
    # Prüfe ob Quiz-Session gültig ist
    if not session.get('quiz_gestartet'):
        flash('Bitte starte ein neues Quiz.', 'error')
        return redirect(url_for('index'))

    aktuelle_index = session.get('aktuelle_fragen_index', 0)
    gesamte_fragen = session.get('gesamte_fragen', 0)

    # Prüfe ob Quiz bereits abgeschlossen ist
    if aktuelle_index >= gesamte_fragen:
        return redirect(url_for('results'))

    # Hole übermittelte Antwort
    try:
        ausgewaehlte_antwort = int(request.form.get('antwort', 0))
    except (ValueError, TypeError):
        flash('Ungültige Antwortauswahl.', 'error')
        return redirect(url_for('quiz'))

    # Validiere Antwortbereich
    if ausgewaehlte_antwort not in [1, 2, 3, 4]:
        flash('Bitte wähle eine gültige Antwort (1-4).', 'error')
        return redirect(url_for('quiz'))

    # Prüfe ob Antwort korrekt ist
    aktuelle_frage = QUIZ_FRAGEN[aktuelle_index]
    if ausgewaehlte_antwort == aktuelle_frage.korrekte_antwort:
        session['punktzahl'] = session.get('punktzahl', 0) + 1

    # Gehe zur nächsten Frage
    session['aktuelle_fragen_index'] = aktuelle_index + 1

    # Prüfe ob Quiz abgeschlossen ist
    if session['aktuelle_fragen_index'] >= gesamte_fragen:
        return redirect(url_for('results'))

    return redirect(url_for('quiz'))


@app.route('/results')
def results():
    """Zeige finales Quiz-Ergebnis an und speichere Punktzahl.

    Rückgabe:
        Gerendertes results.html Template oder Weiterleitung bei ungültiger Session.
    """
    # Prüfe ob Quiz-Session gültig ist
    if not session.get('quiz_gestartet'):
        flash('Bitte starte ein neues Quiz.', 'error')
        return redirect(url_for('index'))

    spieler_name = session.get('spieler_name', 'Unbekannt')
    punktzahl = session.get('punktzahl', 0)
    gesamte_fragen = session.get('gesamte_fragen', 0)

    # Berechne Prozentsatz
    prozentsatz = (punktzahl / gesamte_fragen * 100) if gesamte_fragen > 0 else 0.0

    # Speichere Ergebnis
    try:
        speichere_ergebnis(spieler_name, punktzahl, gesamte_fragen)
    except Exception as e:
        print(f"Fehler beim Speichern des Ergebnisses: {e}")
        flash('Fehler beim Speichern deines Ergebnisses.', 'error')

    # Lösche Quiz-Session
    session.pop('spieler_name', None)
    session.pop('aktuelle_fragen_index', None)
    session.pop('punktzahl', None)
    session.pop('gesamte_fragen', None)
    session.pop('quiz_gestartet', None)

    return render_template(
        'results.html',
        spieler_name=spieler_name,
        punktzahl=punktzahl,
        gesamte_fragen=gesamte_fragen,
        prozentsatz=prozentsatz
    )


@app.route('/health')
def health():
    """Health-Check-Endpunkt für Monitoring.

    Rückgabe:
        JSON-Antwort mit Status.
    """
    return {'status': 'healthy', 'geladene_fragen': len(QUIZ_FRAGEN)}, 200


if __name__ == '__main__':
    initialisiere_anwendung()

    # Überwache auch .txt Dateien für Auto-Reload
    import glob
    extra_files = glob.glob('quiz/*.txt')

    # Debug-Modus aktiviert Auto-Reload bei Dateiänderungen
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True, extra_files=extra_files)
