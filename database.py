"""
GYM-APP | database.py  (v2 – Plan-basiert)
==========================================
Schema:
  training_plans   → Push / Pull / Beine / Arme
  plan_exercises   → Übungen je Plan (Reihenfolge + Satz-Typen)
  workout_logs     → Jeder gespeicherte Satz (Datum, Typ, Gewicht, Reps)
  weight_logs      → Körpergewicht-Verlauf
"""

import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "gym_app.db"

# ---------------------------------------------------------------------------
# Christians Trainingsplan – wird beim ersten Start einmalig eingetragen
# ---------------------------------------------------------------------------
# Format: (exercise_name, warmup_sets, working_sets)

PLAN_SEED = {
    "Push 💪": [
        ("Schrägbank Maschine",           1, 3),
        ("Flachbank Kurzhantel",           1, 3),
        ("Butterfly",                      1, 3),
        ("Schultern Seitheben Kurzhantel", 1, 2),
        ("Schultern Seitheben Maschine",   0, 3),
        ("Trizeps Multipresse",            1, 3),
        ("Trizeps Kabel",                  0, 3),
    ],
    "Pull 🔙": [
        ("High Row mit Griff",             1, 3),
        ("Lat Ziehen breit",               1, 3),
        ("Enges Rudern",                   1, 3),
        ("Überzüge",                       1, 3),
        ("Hintere Schulter Kreuz Kabel",   1, 3),
        ("Bizeps am Kabel",                1, 3),
        ("Hammer Curls Kurzhantel",        1, 3),
    ],
    "Beine 🦵": [
        ("Bein Beuger sitzend",            1, 3),
        ("Bein Strecker",                  1, 3),
        ("Beinpresse",                     1, 3),
        ("Waden Beinpresse",               0, 2),
        ("Waden sitzend",                  1, 3),
        ("Beinheben (Bauch)",              0, 3),
        ("Planks",                         0, 3),
    ],
    "Arme 💪": [
        ("Bizeps Curls",                   1, 3),
        ("Preacher Curls Kurzhantel",      0, 3),
        ("Hammer Curls an der Bank",       1, 3),
        ("Trizeps über Kopf",              1, 3),
        ("Trizeps Kreuz Kabel",            1, 3),
        ("Trizeps drücken Kabel",          1, 3),
        ("Butterfly Reverse",              1, 3),
    ],
}

PLAN_ORDER = ["Push 💪", "Pull 🔙", "Beine 🦵", "Arme 💪"]


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Erstellt alle Tabellen und füllt den Trainingsplan beim ersten Start."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS training_plans (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL UNIQUE,
                sort_order INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS plan_exercises (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id      INTEGER NOT NULL REFERENCES training_plans(id),
                exercise_name TEXT NOT NULL,
                sort_order   INTEGER NOT NULL DEFAULT 0,
                warmup_sets  INTEGER NOT NULL DEFAULT 0,
                working_sets INTEGER NOT NULL DEFAULT 3
            );

            -- Jeder gespeicherte Satz landet hier
            -- set_type: 'warmup' | 'working'
            CREATE TABLE IF NOT EXISTS workout_logs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_name TEXT NOT NULL,
                set_type      TEXT NOT NULL CHECK(set_type IN ('warmup','working')),
                set_number    INTEGER NOT NULL,
                weight_kg     REAL    NOT NULL CHECK(weight_kg >= 0),
                reps          INTEGER NOT NULL CHECK(reps >= 0),
                log_date      TEXT NOT NULL DEFAULT (date('now')),
                logged_at     TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_wl_exercise_date
                ON workout_logs(exercise_name, log_date);

            CREATE TABLE IF NOT EXISTS weight_logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                weight_kg  REAL NOT NULL CHECK(weight_kg > 0),
                log_date   TEXT NOT NULL UNIQUE,
                logged_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_weight_date
                ON weight_logs(log_date);
        """)

        # Pläne einmalig seeden
        for sort_i, plan_name in enumerate(PLAN_ORDER):
            conn.execute(
                "INSERT OR IGNORE INTO training_plans (name, sort_order) VALUES (?,?)",
                (plan_name, sort_i)
            )
            plan_id = conn.execute(
                "SELECT id FROM training_plans WHERE name=?", (plan_name,)
            ).fetchone()["id"]

            # Nur seeden wenn noch keine Übungen vorhanden
            existing = conn.execute(
                "SELECT COUNT(*) AS c FROM plan_exercises WHERE plan_id=?", (plan_id,)
            ).fetchone()["c"]

            if existing == 0:
                exercises = PLAN_SEED[plan_name]
                conn.executemany(
                    """INSERT INTO plan_exercises
                       (plan_id, exercise_name, sort_order, warmup_sets, working_sets)
                       VALUES (?,?,?,?,?)""",
                    [(plan_id, name, idx, wu, ws)
                     for idx, (name, wu, ws) in enumerate(exercises)]
                )


# ---------------------------------------------------------------------------
# Pläne & Übungen lesen
# ---------------------------------------------------------------------------

def get_all_plans() -> list[str]:
    """Gibt alle Plannamen in der definierten Reihenfolge zurück."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name FROM training_plans ORDER BY sort_order ASC"
        ).fetchall()
    return [r["name"] for r in rows]


def get_plan_exercises(plan_name: str) -> list[dict]:
    """
    Gibt alle Übungen eines Plans zurück.
    Return: [{ exercise_name, warmup_sets, working_sets, sort_order }, ...]
    """
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT pe.exercise_name, pe.warmup_sets, pe.working_sets, pe.sort_order
            FROM plan_exercises pe
            JOIN training_plans tp ON tp.id = pe.plan_id
            WHERE tp.name = ?
            ORDER BY pe.sort_order ASC
            """,
            (plan_name,)
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Workout loggen
# ---------------------------------------------------------------------------

def log_exercise_sets(exercise_name: str, sets: list[tuple]) -> None:
    """
    Speichert alle Sätze einer Übung für heute.
    Löscht vorher alle heutigen Einträge für diese Übung (Überschreiben).

    Args:
        exercise_name: Name der Übung
        sets: Liste von (set_type, set_number, weight_kg, reps)
    """
    today = date.today().isoformat()
    now   = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:
        # Heutige Einträge für diese Übung löschen (ermöglicht Korrekturen)
        conn.execute(
            "DELETE FROM workout_logs WHERE exercise_name=? AND log_date=?",
            (exercise_name, today)
        )
        conn.executemany(
            """INSERT INTO workout_logs
               (exercise_name, set_type, set_number, weight_kg, reps, log_date, logged_at)
               VALUES (?,?,?,?,?,?,?)""",
            [(exercise_name, st, sn, wkg, r, today, now) for st, sn, wkg, r in sets]
        )


def get_today_exercise_sets(exercise_name: str) -> list[dict]:
    """Gibt alle heute gespeicherten Sätze für eine Übung zurück."""
    today = date.today().isoformat()
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT set_type, set_number, weight_kg, reps
               FROM workout_logs
               WHERE exercise_name=? AND log_date=?
               ORDER BY set_type DESC, set_number ASC""",
            (exercise_name, today)
        ).fetchall()
    return [dict(r) for r in rows]


def get_last_session_sets(exercise_name: str) -> dict:
    """
    Gibt die Sätze der letzten (nicht heute) Trainingseinheit zurück.
    Nützlich zum Vorbelegen der Eingabefelder.

    Returns:
        { ('warmup'|'working', set_number): {'weight_kg': x, 'reps': y} }
    """
    today = date.today().isoformat()
    with get_connection() as conn:
        # Letztes Datum dieser Übung (vor heute)
        row = conn.execute(
            """SELECT MAX(log_date) AS last_date
               FROM workout_logs
               WHERE exercise_name=? AND log_date < ?""",
            (exercise_name, today)
        ).fetchone()

        if not row or not row["last_date"]:
            return {}

        last_date = row["last_date"]
        sets = conn.execute(
            """SELECT set_type, set_number, weight_kg, reps
               FROM workout_logs
               WHERE exercise_name=? AND log_date=?
               ORDER BY set_type DESC, set_number ASC""",
            (exercise_name, last_date)
        ).fetchall()

    return {
        (r["set_type"], r["set_number"]): {"weight_kg": r["weight_kg"], "reps": r["reps"]}
        for r in sets
    }


def is_exercise_done_today(exercise_name: str) -> bool:
    """Gibt True zurück wenn für diese Übung heute schon Sätze gespeichert wurden."""
    today = date.today().isoformat()
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) AS c FROM workout_logs WHERE exercise_name=? AND log_date=?",
            (exercise_name, today)
        ).fetchone()["c"]
    return count > 0


# ---------------------------------------------------------------------------
# Progress / History
# ---------------------------------------------------------------------------

def get_exercise_history(exercise_name: str, weeks: int = 4) -> list[dict]:
    """
    Gibt die Trainingshistory der letzten N Wochen zurück.
    Pro Trainingstag: max Gewicht, Gesamtvolumen, Arbeitssätze.

    Returns:
        [{ log_date, max_weight, total_volume, working_sets_count, avg_reps }]
    """
    since = (date.today() - timedelta(weeks=weeks)).isoformat()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                log_date,
                MAX(CASE WHEN set_type='working' THEN weight_kg ELSE 0 END) AS max_weight,
                ROUND(SUM(weight_kg * reps), 0)                              AS total_volume,
                SUM(CASE WHEN set_type='working' THEN 1 ELSE 0 END)         AS working_sets_count,
                ROUND(AVG(CASE WHEN set_type='working' THEN reps END), 1)   AS avg_reps
            FROM workout_logs
            WHERE exercise_name=? AND log_date >= ?
            GROUP BY log_date
            ORDER BY log_date DESC
            """,
            (exercise_name, since)
        ).fetchall()
    return [dict(r) for r in rows]


def get_all_trained_exercises(weeks: int = 4) -> list[str]:
    """Gibt alle Übungen zurück, die in den letzten N Wochen trainiert wurden."""
    since = (date.today() - timedelta(weeks=weeks)).isoformat()
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT DISTINCT exercise_name
               FROM workout_logs
               WHERE log_date >= ?
               ORDER BY exercise_name ASC""",
            (since,)
        ).fetchall()
    return [r["exercise_name"] for r in rows]


def get_max_weight_for_exercise(exercise_name: str) -> float | None:
    """Gibt das höchste jemals gehobene Gewicht für eine Übung zurück."""
    with get_connection() as conn:
        row = conn.execute(
            """SELECT MAX(weight_kg) AS max_w
               FROM workout_logs
               WHERE exercise_name=? AND set_type='working'""",
            (exercise_name,)
        ).fetchone()
    return row["max_w"] if row else None


def get_training_streak() -> dict:
    """Berechnet den aktuellen Trainings-Streak (aufeinanderfolgende Trainingstage)."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT log_date FROM workout_logs ORDER BY log_date DESC"
        ).fetchall()

    if not rows:
        return {"current_streak": 0, "longest_streak": 0, "last_training_date": None}

    training_dates = [date.fromisoformat(r["log_date"]) for r in rows]
    today = date.today()

    # Aktuelle Streak
    current_streak = 0
    check_date = today
    for d in training_dates:
        if d == check_date or d == check_date - timedelta(days=1):
            current_streak += 1
            check_date = d - timedelta(days=1) if d != check_date else check_date - timedelta(days=1)
        elif d < check_date - timedelta(days=1):
            break

    # Längste Streak
    sorted_dates = sorted(training_dates)
    longest_streak = temp = 1
    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] - sorted_dates[i - 1] == timedelta(days=1):
            temp += 1
            longest_streak = max(longest_streak, temp)
        else:
            temp = 1

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "last_training_date": training_dates[0].isoformat() if training_dates else None,
    }


# ---------------------------------------------------------------------------
# Körpergewicht (unverändert)
# ---------------------------------------------------------------------------

def log_body_weight(weight_kg: float, log_date: str | None = None) -> None:
    if log_date is None:
        log_date = date.today().isoformat()
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO weight_logs (weight_kg, log_date, logged_at) VALUES (?,?,?)
               ON CONFLICT(log_date) DO UPDATE SET weight_kg=excluded.weight_kg,
                                                    logged_at=excluded.logged_at""",
            (weight_kg, log_date, now)
        )


def get_weight_history(weeks: int = 16) -> list[dict]:
    since = (date.today() - timedelta(weeks=weeks)).isoformat()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT log_date, weight_kg FROM weight_logs WHERE log_date>=? ORDER BY log_date ASC",
            (since,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_last_two_weights() -> tuple:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT log_date, weight_kg FROM weight_logs ORDER BY log_date DESC LIMIT 2"
        ).fetchall()
    entries = [dict(r) for r in rows]
    return (entries[0] if entries else None, entries[1] if len(entries) > 1 else None)
