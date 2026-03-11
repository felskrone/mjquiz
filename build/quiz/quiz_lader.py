"""Quiz-Fragen-Lader für die Minecraft-Quiz-Anwendung.

Dieses Modul parst die questions.txt Datei und gibt strukturierte Frage-Objekte zurück.
"""

import os
from dataclasses import dataclass
from typing import List


@dataclass
class QuizFrage:
    """Repräsentiert eine einzelne Quiz-Frage mit Multiple-Choice-Antworten.

    Attribute:
        frage_text: Der Text der Frage.
        antwort_1: Erste Antwortoption.
        antwort_2: Zweite Antwortoption.
        antwort_3: Dritte Antwortoption.
        antwort_4: Vierte Antwortoption.
        korrekte_antwort: Die korrekte Antwortnummer (1-4).
    """
    frage_text: str
    antwort_1: str
    antwort_2: str
    antwort_3: str
    antwort_4: str
    korrekte_antwort: int

    def hole_antwort(self, antwort_nummer: int) -> str:
        """Hole den Antworttext für eine gegebene Antwortnummer.

        Argumente:
            antwort_nummer: Antwortnummer (1-4).

        Rückgabe:
            Der Antworttext.

        Löst aus:
            ValueError: Wenn antwort_nummer nicht zwischen 1-4 liegt.
        """
        if antwort_nummer == 1:
            return self.antwort_1
        elif antwort_nummer == 2:
            return self.antwort_2
        elif antwort_nummer == 3:
            return self.antwort_3
        elif antwort_nummer == 4:
            return self.antwort_4
        else:
            raise ValueError(f"Ungültige Antwortnummer: {antwort_nummer}")


def lade_quiz_fragen(dateiname: str = None) -> List[QuizFrage]:
    """Lade Quiz-Fragen aus einer Textdatei.

    Erwartetes Format:
        Question1: What is the primary material used to craft a crafting table?
        Answer 1: Stone
        Answer 2: Iron
        Answer 3: Wood
        Answer 4: Diamond
        Correct Answer: 3

        Question2: How many obsidian blocks are needed...

    Argumente:
        dateiname: Pfad zur questions.txt Datei. Wenn None, wird die Datei
                   im gleichen Verzeichnis wie dieses Modul gesucht.

    Rückgabe:
        Liste von QuizFrage-Objekten.

    Löst aus:
        FileNotFoundError: Wenn die Datei nicht existiert.
        ValueError: Wenn das Dateiformat ungültig ist.
    """
    # Verwende Standardpfad, wenn kein Dateiname angegeben
    if dateiname is None:
        dateiname = os.path.join(os.path.dirname(__file__), 'questions.txt')

    fragen = []

    try:
        with open(dateiname, 'r', encoding='utf-8') as f:
            inhalt = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Quiz-Fragen-Datei nicht gefunden: {dateiname}")

    # Trenne bei doppelten Zeilenumbrüchen, um Fragen zu separieren
    fragen_bloecke = [block.strip() for block in inhalt.split('\n\n') if block.strip()]

    for i, block in enumerate(fragen_bloecke, start=1):
        zeilen = [zeile.strip() for zeile in block.split('\n') if zeile.strip()]

        if len(zeilen) < 6:
            raise ValueError(
                f"Frage {i} hat unzureichende Zeilen (erwartet 6, erhalten {len(zeilen)})"
            )

        try:
            # Parse Fragetext (entferne "QuestionN: " Präfix)
            frage_text = zeilen[0].split(':', 1)[1].strip()

            # Parse Antworten (entferne "Answer N: " Präfix)
            antwort_1 = zeilen[1].split(':', 1)[1].strip()
            antwort_2 = zeilen[2].split(':', 1)[1].strip()
            antwort_3 = zeilen[3].split(':', 1)[1].strip()
            antwort_4 = zeilen[4].split(':', 1)[1].strip()

            # Parse korrekte Antwort (entferne "Correct Answer: " Präfix)
            korrekte_antwort_str = zeilen[5].split(':', 1)[1].strip()
            korrekte_antwort = int(korrekte_antwort_str)

            if korrekte_antwort not in [1, 2, 3, 4]:
                raise ValueError(
                    f"Frage {i} hat ungültige korrekte Antwort: {korrekte_antwort}"
                )

            fragen.append(QuizFrage(
                frage_text=frage_text,
                antwort_1=antwort_1,
                antwort_2=antwort_2,
                antwort_3=antwort_3,
                antwort_4=antwort_4,
                korrekte_antwort=korrekte_antwort
            ))

        except (IndexError, ValueError) as e:
            raise ValueError(f"Fehler beim Parsen von Frage {i}: {str(e)}")

    if not fragen:
        raise ValueError("Keine Fragen in Datei gefunden")

    return fragen
