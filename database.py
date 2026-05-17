"""
GYM-APP | database.py  (v3 – Supabase / PostgreSQL)
=====================================================
Schema:
  training_plans   → Push / Pull / Beine / Arme
  plan_exercises   → Übungen je Plan (Reihenfolge + Satz-Typen)
  workout_logs     → Jeder gespeicherte Satz (Datum, Typ, Gewicht, Reps)
  weight_logs      → Körpergewicht-Verlauf
"""

import psycopg2
import psycopg2.extras
import streamlit as st
from contextlib import contextmanager
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------------------
# Christians Trainingsplan – wird beim ersten Start einmalig eingetragen
# ---------------------------------------------------------------------------
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

def _get_db_url() -> str:
    """Liest die Datenbank-URL aus den Streamlit Secrets."""
    return st.secrets["DATABASE_URL"]


@st.cache_resource
def _get_pool():
    """Erstellt einen wiederverwendbaren Connection-Pool (einmalig pro Session)."""
    from psycopg2 import pool as pg_pool
    return pg_pool.ThreadedConnectionPool(1, 5, _get_db_url())


@contextmanager
def get_connection():
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


# ---------------------------------------------------------------------------
# Query-Helpers (ersetzen sqlite3.Row durch echte Dicts)
# ---------------------------------------------------------------------------

def _fetchall(conn, query: str, params=None) -> list[dict]:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query, params or ())
        return [dict(r) for r in cur.fetchall()]


def _fetchone(conn, query: str, params=None) -> dict | None:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query, params or ())
        row = cur.fetchone()
        return dict(row) if row else None


def _execute(conn, query: str, params=None) -> None:
    with conn.cursor() as cur:
        cur.execute(query, params or ())


def _executemany(conn, query: str, params_list: list) -> None:
    with conn.cursor() as cur:
        cur.executemany(query, params_list)


def _to_date_str(val) -> str | None:
    """Konvertiert date/datetime-Objekte zu ISO-String (für einheitliche Rückgabewerte)."""
    if val is None:
        return None
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    return str(val)


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Erstellt alle Tabellen und füllt den Trainingsplan beim ersten Start."""
    with get_connection() as conn:

        _execute(conn, """
            CREATE TABLE IF NOT EXISTS training_plans (
                id         SERIAL PRIMARY KEY,
                name       TEXT NOT NULL UNIQUE,
                sort_order INTEGER NOT NULL DEFAULT 0
            )
        """)

        _execute(conn, """
            CREATE TABLE IF NOT EXISTS plan_exercises (
                id            SERIAL PRIMARY KEY,
                plan_id       INTEGER NOT NULL REFERENCES training_plans(id),
                exercise_name TEXT NOT NULL,
                sort_order    INTEGER NOT NULL DEFAULT 0,
                warmup_sets   INTEGER NOT NULL DEFAULT 0,
                working_sets  INTEGER NOT NULL DEFAULT 3
            )
        """)

        _execute(conn, """
            CREATE TABLE IF NOT EXISTS workout_logs (
                id            SERIAL PRIMARY KEY,
                exercise_name TEXT NOT NULL,
                set_type      TEXT NOT NULL CHECK(set_type IN ('warmup','working')),
                set_number    INTEGER NOT NULL,
                weight_kg     REAL    NOT NULL CHECK(weight_kg >= 0),
                reps          INTEGER NOT NULL CHECK(reps >= 0),
                log_date      DATE    NOT NULL DEFAULT CURRENT_DATE,
                logged_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        _execute(conn, """
            CREATE INDEX IF NOT EXISTS idx_wl_exercise_date
                ON workout_logs(exercise_name, log_date)
        """)

        _execute(conn, """
            CREATE TABLE IF NOT EXISTS weight_logs (
                id        SERIAL PRIMARY KEY,
                weight_kg REAL NOT NULL CHECK(weight_kg > 0),
                log_date  DATE NOT NULL UNIQUE,
                logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        _execute(conn, """
            CREATE INDEX IF NOT EXISTS idx_weight_date
                ON weight_logs(log_date)
        """)

        _execute(conn, """
            CREATE TABLE IF NOT EXISTS app_settings (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Pläne einmalig seeden
        for sort_i, plan_name in enumerate(PLAN_ORDER):
            _execute(conn,
                "INSERT INTO training_plans (name, sort_order) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING",
                (plan_name, sort_i)
            )
            row = _fetchone(conn, "SELECT id FROM training_plans WHERE name=%s", (plan_name,))
            plan_id = row["id"]

            count_row = _fetchone(conn,
                "SELECT COUNT(*) AS c FROM plan_exercises WHERE plan_id=%s", (plan_id,))

            if count_row["c"] == 0:
                exercises = PLAN_SEED[plan_name]
                _executemany(conn,
                    """INSERT INTO plan_exercises
                       (plan_id, exercise_name, sort_order, warmup_sets, working_sets)
                       VALUES (%s, %s, %s, %s, %s)""",
                    [(plan_id, name, idx, wu, ws)
                     for idx, (name, wu, ws) in enumerate(exercises)]
                )


# ---------------------------------------------------------------------------
# Pläne & Übungen lesen
# ---------------------------------------------------------------------------

@st.cache_data(ttl=600)
def get_all_plans() -> list[str]:
    with get_connection() as conn:
        rows = _fetchall(conn,
            "SELECT name FROM training_plans ORDER BY sort_order ASC")
    return [r["name"] for r in rows]


@st.cache_data(ttl=600)
def get_plan_exercises(plan_name: str) -> list[dict]:
    with get_connection() as conn:
        rows = _fetchall(conn, """
            SELECT pe.exercise_name, pe.warmup_sets, pe.working_sets, pe.sort_order
            FROM plan_exercises pe
            JOIN training_plans tp ON tp.id = pe.plan_id
            WHERE tp.name = %s
            ORDER BY pe.sort_order ASC
        """, (plan_name,))
    return rows


# ---------------------------------------------------------------------------
# Workout loggen
# ---------------------------------------------------------------------------

def log_exercise_sets(exercise_name: str, sets: list[tuple]) -> None:
    today = date.today()
    now   = datetime.now()

    with get_connection() as conn:
        _execute(conn,
            "DELETE FROM workout_logs WHERE exercise_name=%s AND log_date=%s",
            (exercise_name, today)
        )
        _executemany(conn,
            """INSERT INTO workout_logs
               (exercise_name, set_type, set_number, weight_kg, reps, log_date, logged_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            [(exercise_name, stype, sn, wkg, r, today, now) for stype, sn, wkg, r in sets]
        )
    # Cache nach Schreibvorgang leeren
    get_today_exercise_sets.clear()
    is_exercise_done_today.clear()
    get_training_streak.clear()
    get_max_weight_for_exercise.clear()
    get_exercise_history.clear()
    get_all_trained_exercises.clear()


@st.cache_data(ttl=20)
def get_today_exercise_sets(exercise_name: str) -> list[dict]:
    today = date.today()
    with get_connection() as conn:
        rows = _fetchall(conn, """
            SELECT set_type, set_number, weight_kg, reps
            FROM workout_logs
            WHERE exercise_name=%s AND log_date=%s
            ORDER BY set_type DESC, set_number ASC
        """, (exercise_name, today))
    return rows


@st.cache_data(ttl=120)
def get_last_session_sets(exercise_name: str) -> dict:
    today = date.today()
    with get_connection() as conn:
        row = _fetchone(conn, """
            SELECT MAX(log_date) AS last_date
            FROM workout_logs
            WHERE exercise_name=%s AND log_date < %s
        """, (exercise_name, today))

        if not row or not row["last_date"]:
            return {}

        last_date = row["last_date"]
        sets = _fetchall(conn, """
            SELECT set_type, set_number, weight_kg, reps
            FROM workout_logs
            WHERE exercise_name=%s AND log_date=%s
            ORDER BY set_type DESC, set_number ASC
        """, (exercise_name, last_date))

    return {
        (r["set_type"], r["set_number"]): {"weight_kg": r["weight_kg"], "reps": r["reps"]}
        for r in sets
    }


@st.cache_data(ttl=20)
def is_exercise_done_today(exercise_name: str) -> bool:
    today = date.today()
    with get_connection() as conn:
        row = _fetchone(conn,
            "SELECT COUNT(*) AS c FROM workout_logs WHERE exercise_name=%s AND log_date=%s",
            (exercise_name, today))
    return row["c"] > 0


# ---------------------------------------------------------------------------
# Progress / History
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60)
def get_exercise_history(exercise_name: str, weeks: int = 4) -> list[dict]:
    since = date.today() - timedelta(weeks=weeks)
    with get_connection() as conn:
        rows = _fetchall(conn, """
            SELECT
                log_date::text                                                          AS log_date,
                MAX(CASE WHEN set_type='working' THEN weight_kg ELSE 0 END)            AS max_weight,
                ROUND(CAST(SUM(weight_kg * reps) AS numeric), 0)                       AS total_volume,
                SUM(CASE WHEN set_type='working' THEN 1 ELSE 0 END)                    AS working_sets_count,
                ROUND(CAST(AVG(CASE WHEN set_type='working' THEN reps END) AS numeric), 1) AS avg_reps
            FROM workout_logs
            WHERE exercise_name=%s AND log_date >= %s
            GROUP BY log_date
            ORDER BY log_date DESC
        """, (exercise_name, since))
    return rows


@st.cache_data(ttl=60)
def get_all_trained_exercises(weeks: int = 4) -> list[str]:
    since = date.today() - timedelta(weeks=weeks)
    with get_connection() as conn:
        rows = _fetchall(conn, """
            SELECT DISTINCT exercise_name
            FROM workout_logs
            WHERE log_date >= %s
            ORDER BY exercise_name ASC
        """, (since,))
    return [r["exercise_name"] for r in rows]


@st.cache_data(ttl=60)
def get_max_weight_for_exercise(exercise_name: str) -> float | None:
    with get_connection() as conn:
        row = _fetchone(conn, """
            SELECT MAX(weight_kg) AS max_w
            FROM workout_logs
            WHERE exercise_name=%s AND set_type='working'
        """, (exercise_name,))
    return row["max_w"] if row else None


@st.cache_data(ttl=30)
def get_training_streak() -> dict:
    with get_connection() as conn:
        rows = _fetchall(conn,
            "SELECT DISTINCT log_date::text AS log_date FROM workout_logs ORDER BY log_date DESC")

    empty = {
        "sessions_this_week": 0,
        "sessions_last_week": 0,
        "weekly_streak": 0,
        "longest_weekly_streak": 0,
        "last_training_date": None,
    }
    if not rows:
        return empty

    training_dates = [date.fromisoformat(r["log_date"]) for r in rows]
    today = date.today()

    # Montag dieser und letzter Woche
    this_monday = today - timedelta(days=today.weekday())
    last_monday = this_monday - timedelta(weeks=1)

    sessions_this_week = sum(1 for d in training_dates if d >= this_monday)
    sessions_last_week = sum(1 for d in training_dates if last_monday <= d < this_monday)

    # Wochen-Streak: wie viele Wochen in Folge (inkl. akt. Woche) mindestens 1 Training
    trained_weeks = set(d.strftime("%G-%V") for d in training_dates)  # ISO-Woche

    weekly_streak = 0
    check = today
    while True:
        week_key = check.strftime("%G-%V")
        if week_key in trained_weeks:
            weekly_streak += 1
            check -= timedelta(weeks=1)
        else:
            break

    # Längste Wochen-Streak
    sorted_weeks = sorted(trained_weeks)
    longest_weekly_streak = temp = 1 if sorted_weeks else 0
    for i in range(1, len(sorted_weeks)):
        # Prüfe ob aufeinanderfolgende ISO-Wochen
        y1, w1 = map(int, sorted_weeks[i - 1].split("-"))
        y2, w2 = map(int, sorted_weeks[i].split("-"))
        total1 = y1 * 53 + w1
        total2 = y2 * 53 + w2
        if total2 - total1 == 1:
            temp += 1
            longest_weekly_streak = max(longest_weekly_streak, temp)
        else:
            temp = 1

    return {
        "sessions_this_week": sessions_this_week,
        "sessions_last_week": sessions_last_week,
        "weekly_streak": weekly_streak,
        "longest_weekly_streak": longest_weekly_streak,
        "last_training_date": training_dates[0].isoformat() if training_dates else None,
    }


# ---------------------------------------------------------------------------
# Körpergewicht
# ---------------------------------------------------------------------------

def log_body_weight(weight_kg: float, log_date: str | None = None) -> None:
    if log_date is None:
        log_date = date.today()
    else:
        log_date = date.fromisoformat(log_date)
    now = datetime.now()

    with get_connection() as conn:
        _execute(conn, """
            INSERT INTO weight_logs (weight_kg, log_date, logged_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (log_date) DO UPDATE
                SET weight_kg = EXCLUDED.weight_kg,
                    logged_at = EXCLUDED.logged_at
        """, (weight_kg, log_date, now))
    # Cache nach Schreibvorgang leeren
    get_weight_history.clear()
    get_last_two_weights.clear()


def get_setting(key: str) -> str | None:
    """Liest einen App-Einstellungswert aus der Datenbank."""
    with get_connection() as conn:
        row = _fetchone(conn, "SELECT value FROM app_settings WHERE key=%s", (key,))
    return row["value"] if row else None


def set_setting(key: str, value: str) -> None:
    """Speichert einen App-Einstellungswert dauerhaft."""
    with get_connection() as conn:
        _execute(conn, """
            INSERT INTO app_settings (key, value) VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """, (key, value))


@st.cache_data(ttl=60)
def get_weight_history(weeks: int = 16) -> list[dict]:
    since = date.today() - timedelta(weeks=weeks)
    with get_connection() as conn:
        rows = _fetchall(conn, """
            SELECT log_date::text AS log_date, weight_kg
            FROM weight_logs
            WHERE log_date >= %s
            ORDER BY log_date ASC
        """, (since,))
    return rows


@st.cache_data(ttl=60)
def get_last_two_weights() -> tuple:
    with get_connection() as conn:
        rows = _fetchall(conn, """
            SELECT log_date::text AS log_date, weight_kg
            FROM weight_logs
            ORDER BY log_date DESC
            LIMIT 2
        """)
    return (rows[0] if rows else None, rows[1] if len(rows) > 1 else None)
