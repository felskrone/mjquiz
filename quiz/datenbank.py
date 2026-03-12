"""Datenbankoperationen für die Minecraft-Quiz-Anwendung.

Dieses Modul verwaltet die Initialisierung der Highscore-Textdatei,
die Persistierung von Ergebnissen und das Abrufen der Top 10 Highscores.
"""

import os
from datetime import datetime
from typing import List, Dict, Any




# Pfad zur Highscore-Datei
HIGHSCORES_DATEI = os.path.join(os.path.dirname(__file__), 'data/highscores.txt')


def initialisiere_speicher() -> None:
    """Initialisiere die highscores.txt Datei, falls sie nicht existiert.

    Erstellt eine neue Datei mit Header-Zeile, wenn die Datei noch nicht vorhanden ist.
    """
    if not os.path.exists(HIGHSCORES_DATEI):
        with open(HIGHSCORES_DATEI, 'w', encoding='utf-8') as f:
            f.write('spieler_name|punktzahl|gesamte_fragen|prozentsatz|abgeschlossen_am\n')


def speichere_ergebnis(spieler_name: str, punktzahl: int, gesamte_fragen: int) -> None:
    """Speichere ein Quiz-Ergebnis und behalte nur die Top 10 Ergebnisse.

    Berechnet den Prozentsatz, fügt das neue Ergebnis hinzu, sortiert alle Ergebnisse
    und behält nur die besten 10. Verwendet atomare Dateioperationen.

    Argumente:
        spieler_name: Der Name des Spielers.
        punktzahl: Anzahl der richtigen Antworten.
        gesamte_fragen: Gesamtzahl der Fragen im Quiz.

    Löst aus:
        IOError: Wenn die Datei nicht geschrieben werden kann.
    """
    # Berechne Prozentsatz
    prozentsatz = (punktzahl / gesamte_fragen * 100) if gesamte_fragen > 0 else 0.0

    # Erstelle Zeitstempel
    abgeschlossen_am = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Lese bestehende Ergebnisse
    bestehende_ergebnisse = hole_top_10_ergebnisse()

    # Füge neues Ergebnis hinzu
    neues_ergebnis = {
        'spieler_name': spieler_name,
        'punktzahl': punktzahl,
        'gesamte_fragen': gesamte_fragen,
        'prozentsatz': prozentsatz,
        'abgeschlossen_am': abgeschlossen_am
    }
    bestehende_ergebnisse.append(neues_ergebnis)

    # Sortiere nach Punktzahl (absteigend), dann nach Zeitstempel (absteigend)
    bestehende_ergebnisse.sort(
        key=lambda x: (x['punktzahl'], x['abgeschlossen_am']),
        reverse=True
    )

    # Behalte nur Top 10
    top_ergebnisse = bestehende_ergebnisse[:10]

    # Schreibe zurück in Datei (atomare Operation)
    temp_datei = HIGHSCORES_DATEI + '.tmp'
    try:
        with open(temp_datei, 'w', encoding='utf-8') as f:
            # Schreibe Header
            f.write('spieler_name|punktzahl|gesamte_fragen|prozentsatz|abgeschlossen_am\n')

            # Schreibe Ergebnisse
            for ergebnis in top_ergebnisse:
                zeile = f"{ergebnis['spieler_name']}|{ergebnis['punktzahl']}|" \
                       f"{ergebnis['gesamte_fragen']}|{ergebnis['prozentsatz']:.1f}|" \
                       f"{ergebnis['abgeschlossen_am']}\n"
                f.write(zeile)

        # Atomare Ersetzung
        os.replace(temp_datei, HIGHSCORES_DATEI)
    except Exception as e:
        # Bereinige temporäre Datei bei Fehler
        if os.path.exists(temp_datei):
            os.remove(temp_datei)
        raise IOError(f"Fehler beim Speichern der Ergebnisse: {e}")


def hole_top_10_ergebnisse() -> List[Dict[str, Any]]:
    """Hole die Top 10 Highscores aus der Datei.

    Rückgabe:
        Liste von Dictionaries mit Ergebnisinformationen,
        sortiert nach Punktzahl absteigend. Maximale Länge: 10 Einträge.
    """
    # Prüfe ob Datei existiert
    if not os.path.exists(HIGHSCORES_DATEI):
        return []

    ergebnisse = []

    try:
        with open(HIGHSCORES_DATEI, 'r', encoding='utf-8') as f:
            zeilen = f.readlines()

        # Überspringe Header-Zeile
        if len(zeilen) <= 1:
            return []

        # Parse jede Zeile
        for zeile in zeilen[1:]:
            zeile = zeile.strip()
            if not zeile:
                continue

            try:
                # Trenne Felder
                teile = zeile.split('|')
                if len(teile) != 5:
                    # Überspringe fehlerhafte Zeilen
                    print(f"Warnung: Überspringe fehlerhafte Zeile: {zeile}")
                    continue

                # Erstelle Dictionary
                ergebnis = {
                    'spieler_name': teile[0],
                    'punktzahl': int(teile[1]),
                    'gesamte_fragen': int(teile[2]),
                    'prozentsatz': float(teile[3]),
                    'abgeschlossen_am': teile[4]
                }
                ergebnisse.append(ergebnis)

            except (ValueError, IndexError) as e:
                # Überspringe fehlerhafte Zeilen
                print(f"Warnung: Fehler beim Parsen der Zeile '{zeile}': {e}")
                continue

        return ergebnisse

    except Exception as e:
        print(f"Fehler beim Lesen der Highscores: {e}")
        return []
