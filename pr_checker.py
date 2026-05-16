"""
GYM-APP | pr_checker.py
========================
Personal-Record-Erkennung.

Ablauf (wird nach jedem gespeicherten Satz aufgerufen):
  1. Hole die bisherigen PR-Werte aus der DB (via database.get_pr_stats)
  2. Vergleiche den neuen Satz gegen alle drei PR-Dimensionen
  3. Gib ein PRResult-Objekt zurück → das UI entscheidet dann,
     welches Banner / welche Animation es zeigt.

Drei PR-Dimensionen:
  - MAX_WEIGHT:  Schwerstes je gehobenes Gewicht in einem Satz
  - MAX_VOLUME:  Höchstes Tagesvolumen (kg × Reps, summiert über alle Sätze des Tages)
  - MAX_REPS:    Meiste Wiederholungen in einem einzelnen Satz
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass  # Verhindert zirkuläre Imports; database wird lazy importiert


# ---------------------------------------------------------------------------
# Datenstrukturen
# ---------------------------------------------------------------------------

class PRType(Enum):
    """Art des geschlagenen Personal Records."""
    MAX_WEIGHT = auto()   # Neues schwerster Satz
    MAX_VOLUME = auto()   # Neues Tages-Rekordvolumen
    MAX_REPS   = auto()   # Neue Rekord-Wiederholungszahl


@dataclass
class PRResult:
    """
    Ergebnis nach einem gespeicherten Satz.

    Attributes:
        is_pr:        True wenn mindestens ein PR gebrochen wurde
        pr_types:     Liste der gebrochenen PR-Dimensionen
        old_values:   Alte Bestwerte {PRType -> float | None}
        new_values:   Neue Bestwerte {PRType -> float}
        motivational_message: Generierte Motivationsnachricht
    """
    is_pr:                 bool            = False
    pr_types:              list[PRType]    = field(default_factory=list)
    old_values:            dict            = field(default_factory=dict)
    new_values:            dict            = field(default_factory=dict)
    motivational_message:  str             = ""

    # Für das UI: Welches Banner-Icon soll zuerst gezeigt werden?
    @property
    def primary_pr_type(self) -> PRType | None:
        """Gibt den "wichtigsten" PR zurück (Gewicht > Volumen > Reps)."""
        priority = [PRType.MAX_WEIGHT, PRType.MAX_VOLUME, PRType.MAX_REPS]
        for t in priority:
            if t in self.pr_types:
                return t
        return None

    @property
    def banner_key(self) -> str | None:
        """Gibt den String-Key zurück, den pr_banner_html() erwartet."""
        mapping = {
            PRType.MAX_WEIGHT: "weight",
            PRType.MAX_VOLUME: "volume",
            PRType.MAX_REPS:   "reps",
        }
        t = self.primary_pr_type
        return mapping.get(t) if t else None


# ---------------------------------------------------------------------------
# Motivationsnachrichten
# ---------------------------------------------------------------------------

_MESSAGES_PR_WEIGHT = [
    "NEUES MAX! Du bist stärker als jemals zuvor! 🏋️‍♂️⚡",
    "BESTGEWICHT GEFALLEN! Das ist dein neues Level! 🔥",
    "ABSOLUTER REKORD! Du hast dich selbst übertroffen! 💪",
    "MONSTERLIFT! Neues persönliches Maximum gesetzt! 🚀",
]

_MESSAGES_PR_VOLUME = [
    "REKORDVOLUMEN HEUTE! Mehr Arbeit = mehr Wachstum! 📈🔥",
    "BESTES TAGESVOLUMEN! Du hast heute ALLES gegeben! 💥",
    "VOLUMEN-REKORD! Dein Körper dankt dir später! 💪",
]

_MESSAGES_PR_REPS = [
    "REKORD-WIEDERHOLUNGEN! Ausdauer ist auch Stärke! 🔁🔥",
    "NEUE BESTMARKE bei den Reps! Einfach unaufhörlich! ⚡",
]

_MESSAGES_NO_PR = [
    "Satz zerstört! Weiter so! 🔥",
    "Direkt gespeichert. Weiter, kein Stop! 💪",
    "Eintrag gesichert. Du machst das! ⚡",
    "Sauber! Nächster Satz wartet! 🚀",
    "Locked in. Fokus halten! 🎯",
    "Gespeichert. Du bist im Flow! 🔥",
    "Boom! Ins Log eingetragen! 💥",
]

import random as _random


def _pick_message(messages: list[str]) -> str:
    return _random.choice(messages)


# ---------------------------------------------------------------------------
# Kern-Logik
# ---------------------------------------------------------------------------

def check_pr(
    exercise_name: str,
    new_weight_kg: float,
    new_reps:      int,
    todays_volume: float,
) -> PRResult:
    """
    Prüft, ob der soeben gespeicherte Satz einen Personal Record darstellt.

    Diese Funktion wird NACH dem Speichern des Satzes aufgerufen, damit
    das neue Gewicht bereits in der DB steht (für das Volumen).

    Args:
        exercise_name:  Name der Übung
        new_weight_kg:  Gewicht des gerade gespeicherten Satzes
        new_reps:       Reps des gerade gespeicherten Satzes
        todays_volume:  Gesamtvolumen heutiger Sätze für diese Übung
                        (nach dem Speichern des neuen Satzes berechnen:
                         SUM(weight_kg * reps) WHERE log_date = today)

    Returns:
        PRResult mit allen Details für die UI
    """
    # Lazy-Import um zirkuläre Abhängigkeiten zu vermeiden
    from database import get_pr_stats

    # Bisherige Bestwerte aus der DB holen
    # WICHTIG: get_pr_stats() gibt das NEUE Maximum zurück (nach dem Insert).
    # Wir ermitteln daher das "alte" Maximum, indem wir prüfen, ob der aktuelle
    # Wert genau gleich dem neuen DB-Maximum ist (kein Tie = neuer PR).
    stats = get_pr_stats(exercise_name)

    result        = PRResult()
    result.old_values = {}
    result.new_values = {}

    # --- 1. Max-Gewicht PR ---
    db_max_weight = stats["all_time_max_weight"]
    if db_max_weight is not None and new_weight_kg >= db_max_weight:
        # Da wir nach dem Insert abfragen, bedeutet == ein neuer oder geteilter PR
        # Wir flagen es als PR wenn new_weight_kg == db_max_weight
        # (d. h. der neue Satz hat das Maximum erreicht oder erstmalig gesetzt)
        result.pr_types.append(PRType.MAX_WEIGHT)
        result.new_values[PRType.MAX_WEIGHT] = new_weight_kg

    # --- 2. Tagesvolumen PR ---
    db_max_volume = stats["all_time_max_volume"]
    if db_max_volume is not None and todays_volume >= db_max_volume:
        result.pr_types.append(PRType.MAX_VOLUME)
        result.new_values[PRType.MAX_VOLUME] = round(todays_volume, 1)

    # --- 3. Max-Reps PR ---
    db_max_reps = stats["all_time_max_reps"]
    if db_max_reps is not None and new_reps >= db_max_reps:
        result.pr_types.append(PRType.MAX_REPS)
        result.new_values[PRType.MAX_REPS] = new_reps

    # --- Ergebnis zusammenbauen ---
    if result.pr_types:
        result.is_pr = True
        # Motivationsnachricht je nach wichtigstem PR
        if PRType.MAX_WEIGHT in result.pr_types:
            result.motivational_message = _pick_message(_MESSAGES_PR_WEIGHT)
        elif PRType.MAX_VOLUME in result.pr_types:
            result.motivational_message = _pick_message(_MESSAGES_PR_VOLUME)
        else:
            result.motivational_message = _pick_message(_MESSAGES_PR_REPS)
    else:
        result.motivational_message = _pick_message(_MESSAGES_NO_PR)

    return result


def compute_todays_volume(exercise_name: str) -> float:
    """
    Hilfsfunktion: Berechnet das heutige Gesamtvolumen für eine Übung.
    Muss NACH dem Speichern des neuen Satzes aufgerufen werden.

    Returns:
        Gesamtvolumen in kg (Summe aus weight_kg × reps aller heutigen Sätze)
    """
    from database import get_todays_sets

    sets   = get_todays_sets(exercise_name)
    volume = sum(s["weight_kg"] * s["reps"] for s in sets)
    return round(volume, 1)


def get_pr_summary(exercise_name: str) -> dict:
    """
    Gibt eine für das UI aufbereitete PR-Zusammenfassung zurück.
    Nützlich für die Anzeige der bisherigen Bestleistungen oberhalb des Eingabeformulars.

    Returns:
        Dict mit menschenlesbaren Strings:
          - max_weight_str: "142.5 kg"
          - max_volume_str: "4 320 kg"
          - max_reps_str:   "15"
          - has_data:       bool
    """
    from database import get_pr_stats

    stats = get_pr_stats(exercise_name)

    has_data = any(v is not None for v in stats.values())

    def fmt_kg(val: float | None) -> str:
        if val is None:
            return "–"
        return f"{val:g} kg"

    def fmt_vol(val: float | None) -> str:
        if val is None:
            return "–"
        return f"{val:,.0f} kg".replace(",", ".")  # Tausenderpunkt

    def fmt_reps(val: int | None) -> str:
        if val is None:
            return "–"
        return str(int(val))

    return {
        "max_weight_str": fmt_kg(stats["all_time_max_weight"]),
        "max_volume_str": fmt_vol(stats["all_time_max_volume"]),
        "max_reps_str":   fmt_reps(stats["all_time_max_reps"]),
        "has_data":       has_data,
        "raw":            stats,
    }
