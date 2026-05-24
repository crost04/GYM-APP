"""
GYM-APP | app.py  (v2 – Plan-geführtes Workout)
================================================
Starten:  streamlit run app.py

Tabs:
  🏋️  Training  → Plan wählen, Sätze eintragen, PR-Erkennung
  📊  Verlauf   → 4-Wochen-History pro Übung + Plotly-Charts
  ⚖️  Gewicht   → Körpergewicht tracken
"""

import streamlit as st

st.set_page_config(
    page_title="GYM-APP 💪",
    page_icon="🏋️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

import random
from datetime import date

import database as db
from styles import get_css, streak_card_html, COLORS

# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

if "db_initialized" not in st.session_state:
    db.init_db()
    db.run_migrations()
    st.session_state.db_initialized = True
st.markdown(get_css(), unsafe_allow_html=True)

# Zusätzliches CSS speziell für v2
st.markdown(f"""
<style>
/* Plan-Buttons – große quadratische Touch-Targets */
div[data-testid="column"] .stButton > button {{
    height: 80px !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    border-radius: 18px !important;
    flex-direction: column !important;
}}

/* Grüner "erledigt"-Button */
.done-btn > button {{
    background: {COLORS['bg_tertiary']} !important;
    color: {COLORS['accent_green']} !important;
    border: 2px solid {COLORS['accent_green']}55 !important;
    box-shadow: none !important;
}}

/* Satz-Header-Labels */
.set-header {{
    display: flex;
    gap: 8px;
    align-items: center;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: {COLORS['text_muted']};
    margin-bottom: 4px;
    padding: 0 4px;
}}

/* Übungs-Karte */
.exercise-card {{
    background: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 18px;
    padding: 16px 14px 12px 14px;
    margin-bottom: 12px;
}}

.exercise-card.done {{
    border-color: {COLORS['accent_green']}55;
    background: linear-gradient(135deg, {COLORS['accent_green']}08, {COLORS['bg_secondary']});
}}

/* Aufwärm-Row */
.warmup-tag {{
    display: inline-block;
    background: {COLORS['accent_orange']}22;
    color: {COLORS['accent_orange']};
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 2px 8px;
    border-radius: 6px;
    margin-bottom: 6px;
}}

.working-tag {{
    display: inline-block;
    background: {COLORS['accent_green']}22;
    color: {COLORS['accent_green']};
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 2px 8px;
    border-radius: 6px;
    margin-bottom: 6px;
}}

/* Number-Input kleiner auf Mobile */
.stNumberInput input {{
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    text-align: center !important;
}}

/* History-Tabelle */
.history-row {{
    display: grid;
    grid-template-columns: 1.2fr 1fr 1.2fr 0.8fr;
    gap: 0;
    padding: 10px 14px;
    font-size: 0.85rem;
    border-top: 1px solid {COLORS['border']};
    align-items: center;
}}

.history-header {{
    background: {COLORS['bg_secondary']};
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {COLORS['text_muted']};
    border-radius: 12px 12px 0 0;
    padding: 10px 14px;
}}

/* Fortschrittsbalken für Workout */
.progress-bar-wrap {{
    background: {COLORS['bg_tertiary']};
    border-radius: 6px;
    height: 6px;
    margin: 8px 0 16px 0;
    overflow: hidden;
}}

.progress-bar-fill {{
    background: linear-gradient(90deg, {COLORS['accent_green']}, {COLORS['accent_blue']});
    height: 100%;
    border-radius: 6px;
    transition: width 0.4s ease;
}}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def motivational_message() -> str:
    messages = [
        "Satz zerstört! Weiter so! 🔥",
        "Direkt gesichert. Nächster! 💪",
        "Sauber! Du bist im Flow! ⚡",
        "Locked in. Fokus halten! 🎯",
        "Boom! Ins Log eingetragen! 💥",
        "Stark! Kein Stop! 🚀",
        "Gespeichert. Du machst das! 🔥",
    ]
    return random.choice(messages)


def pr_message(exercise: str, new_w: float, old_w: float | None) -> str:
    return f"🏆 NEUER REKORD bei {exercise}! {new_w} kg – vorher {old_w or 0} kg. BEAST MODE! ⚡"


# ---------------------------------------------------------------------------
# App-Header
# ---------------------------------------------------------------------------

st.markdown(f"""
<div style="padding: 8px 0 4px 0;">
    <h1 style="margin:0;padding:0;">GYM-APP 💪</h1>
    <p style="color:{COLORS['text_secondary']};font-size:0.85rem;margin:2px 0 10px 0;">
        Track hard. Progress harder.
    </p>
</div>
""", unsafe_allow_html=True)

# Streak
streak = db.get_training_streak()
st.markdown(streak_card_html(
    sessions_this_week   = streak["sessions_this_week"],
    sessions_last_week   = streak["sessions_last_week"],
    weekly_streak        = streak["weekly_streak"],
    longest_weekly_streak= streak["longest_weekly_streak"],
), unsafe_allow_html=True)
st.markdown(f'<div style="height:1px;background:linear-gradient(90deg,transparent,{COLORS["border"]},transparent);margin:14px 0;"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_train, tab_verlauf, tab_gewicht, tab_plaene = st.tabs(["🏋️  Training", "📊  Verlauf", "⚖️  Gewicht", "⚙️  Pläne"])


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 1 – TRAINING                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab_train:

    # --- Plan-Auswahl (große Buttons) ---
    if "selected_plan" not in st.session_state:
        # Fallback: letzten Plan aus DB laden (überlebt st.rerun() auf Cloud)
        saved_plan = db.get_setting("active_plan")
        st.session_state["selected_plan"] = saved_plan if saved_plan else None

    plans = db.get_all_plans()

    # Wenn noch kein Plan gewählt: Plan-Auswahl zeigen
    if st.session_state["selected_plan"] is None:

        st.markdown(
            f'<div style="color:{COLORS["text_secondary"]};font-size:0.8rem;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;">'
            f'Welchen Workout machst du heute?</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        for i, plan in enumerate(plans):
            col = col1 if i % 2 == 0 else col2
            with col:
                if st.button(plan, key=f"plan_btn_{plan}", use_container_width=True):
                    st.session_state["selected_plan"] = plan
                    db.set_setting("active_plan", plan)  # in DB sichern
                    st.rerun()

    else:
        # --- Workout läuft ---
        selected_plan = st.session_state["selected_plan"]
        exercises     = db.get_plan_exercises(selected_plan)

        # Fortschrittsbalken
        done_count = sum(1 for ex in exercises
                         if db.is_exercise_done_today(ex["exercise_name"]))
        total_count = len(exercises)
        pct = int(done_count / total_count * 100) if total_count > 0 else 0

        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
            f'<span style="font-size:1rem;font-weight:800;color:{COLORS["text_primary"]};">{selected_plan}</span>'
            f'<span style="font-size:0.8rem;font-weight:700;color:{COLORS["accent_green"]};">{done_count}/{total_count} ✓</span>'
            f'</div>'
            f'<div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:{pct}%;"></div></div>',
            unsafe_allow_html=True,
        )

        # Plan wechseln
        if st.button("← Plan wechseln", key="change_plan_btn"):
            st.session_state["selected_plan"] = None
            db.set_setting("active_plan", "")  # in DB zurücksetzen
            st.rerun()

        # Zeitbasierte Übungen – "Reps" wird durch "Sekunden" ersetzt
        TIMED_EXERCISES = {"Planks"}

        # --- Übungskarten ---
        for ex in exercises:
            ex_name      = ex["exercise_name"]
            warmup_sets  = ex["warmup_sets"]
            working_sets = ex["working_sets"]
            already_done = db.is_exercise_done_today(ex_name)

            # Letzte Session zum Vorbelegen
            last_session = db.get_last_session_sets(ex_name)

            # Heutige Sätze (falls schon erledigt)
            today_sets   = db.get_today_exercise_sets(ex_name) if already_done else []

            # Card-Stil je nach Status
            card_class = "exercise-card done" if already_done else "exercise-card"
            done_icon  = f'<span style="color:{COLORS["accent_green"]};font-size:1rem;">✓</span>' if already_done else ""

            # Wenn heute schon erledigt: komplette Karte als ein HTML-Block
            if already_done and today_sets:
                rows_html = ""
                is_timed = ex_name in TIMED_EXERCISES
                for s in today_sets:
                    tag   = "🔸 Aufwärm" if s["set_type"] == "warmup" else f"Satz {s['set_number']}"
                    color = COLORS["accent_orange"] if s["set_type"] == "warmup" else COLORS["accent_green"]
                    val_str = (f'{s["reps"]} Sek.' if is_timed
                               else f'{s["weight_kg"]} kg × {s["reps"]} Reps')
                    rows_html += (
                        f'<div style="display:flex;justify-content:space-between;'
                        f'padding:6px 0;border-bottom:1px solid {COLORS["border"]};">'
                        f'<span style="color:{COLORS["text_muted"]};font-size:0.82rem;">{tag}</span>'
                        f'<span style="color:{color};font-weight:700;font-size:0.9rem;">'
                        f'{val_str}</span></div>'
                    )
                card_html = (
                    f'<div class="{card_class}">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
                    f'<span style="font-size:0.95rem;font-weight:800;color:{COLORS["text_primary"]};">{ex_name}</span>'
                    f'{done_icon}</div>'
                    f'{rows_html}</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

                # Fehlereintrag löschen
                if st.button(f"🗑️ Eintrag löschen", key=f"edit_{ex_name}"):
                    db.log_exercise_sets(ex_name, [])
                    st.rerun()
                continue

            # --- Eingabe-Formular (Titel direkt drin, kein externer HTML-Block) ---
            with st.form(key=f"form_{ex_name}", clear_on_submit=False):
                st.markdown(
                    f'<div style="font-size:0.95rem;font-weight:800;'
                    f'color:{COLORS["text_primary"]};margin-bottom:6px;">'
                    f'{ex_name}</div>',
                    unsafe_allow_html=True,
                )

                # ── "Letztes Mal"-Referenz ────────────────────────────────
                if last_session:
                    working_refs = []
                    for sn in range(1, working_sets + 1):
                        prev_s = last_session.get(("working", sn))
                        if prev_s:
                            wkg = prev_s["weight_kg"]
                            rps = prev_s["reps"]
                            w_str = f"{wkg:.0f}" if wkg == int(wkg) else f"{wkg:.1f}"
                            working_refs.append(
                                f'<b style="color:{COLORS["text_secondary"]};">'
                                f'#{sn}:</b> {w_str}kg × {rps}'
                            )
                    if working_refs:
                        st.markdown(
                            f'<div style="background:{COLORS["bg_tertiary"]};'
                            f'border-left:3px solid {COLORS["accent_blue"]}66;'
                            f'border-radius:0 8px 8px 0;padding:5px 10px;'
                            f'margin-bottom:10px;font-size:0.72rem;'
                            f'color:{COLORS["text_muted"]};">'
                            f'💾 Letztes Mal: ' + '  ·  '.join(working_refs) + '</div>',
                            unsafe_allow_html=True,
                        )

                all_set_inputs = []

                # Aufwärm-Sätze
                if warmup_sets > 0:
                    st.markdown(f'<span class="warmup-tag">🔸 Aufwärmsatz{"" if warmup_sets == 1 else "s"}</span>',
                                unsafe_allow_html=True)
                    for i in range(1, warmup_sets + 1):
                        prev = last_session.get(("warmup", i), {})
                        default_w = prev.get("weight_kg", 0.0)
                        default_r = prev.get("reps", 12)

                        col_w, col_r = st.columns([3, 2])
                        with col_w:
                            w = st.number_input(
                                f"Gewicht (kg)",
                                min_value=0.0, max_value=500.0,
                                value=float(default_w), step=0.25, format="%.2f",
                                key=f"{ex_name}_wu{i}_w",
                                label_visibility="collapsed" if i > 1 else "visible",
                            )
                        with col_r:
                            r = st.number_input(
                                f"Reps",
                                min_value=0, max_value=200,
                                value=int(default_r), step=1,
                                key=f"{ex_name}_wu{i}_r",
                                label_visibility="collapsed" if i > 1 else "visible",
                            )
                        all_set_inputs.append(("warmup", i, w, r))

                # Arbeitssätze
                is_timed = ex_name in TIMED_EXERCISES
                if working_sets > 0:
                    st.markdown(f'<span class="working-tag">💪 Arbeitssatz{"" if working_sets == 1 else "e"} ({working_sets}×)</span>',
                                unsafe_allow_html=True)
                    for i in range(1, working_sets + 1):
                        prev = last_session.get(("working", i), {})
                        if not prev and last_session:
                            prev = last_session.get(("working", 1), {})
                        default_w = prev.get("weight_kg", 0.0)
                        default_r = prev.get("reps", 60 if is_timed else 10)

                        if is_timed:
                            # Zeitbasiert: nur Sekunden, kein Gewicht
                            col_label, col_r = st.columns([1, 5])
                            with col_label:
                                st.markdown(
                                    f'<div style="padding-top:32px;color:{COLORS["text_muted"]};'
                                    f'font-size:0.78rem;font-weight:700;">#{i}</div>',
                                    unsafe_allow_html=True,
                                )
                            with col_r:
                                r = st.number_input(
                                    "⏱ Sekunden",
                                    min_value=0, max_value=600,
                                    value=int(default_r), step=5,
                                    key=f"{ex_name}_ws{i}_r",
                                )
                            w = 0.0  # kein Gewicht bei Zeitübungen
                        else:
                            col_label, col_w, col_r = st.columns([1, 3, 2])
                            with col_label:
                                st.markdown(
                                    f'<div style="padding-top:32px;color:{COLORS["text_muted"]};'
                                    f'font-size:0.78rem;font-weight:700;">#{i}</div>',
                                    unsafe_allow_html=True,
                                )
                            with col_w:
                                w = st.number_input(
                                    "kg",
                                    min_value=0.0, max_value=500.0,
                                    value=float(default_w), step=0.25, format="%.2f",
                                    key=f"{ex_name}_ws{i}_w",
                                )
                            with col_r:
                                r = st.number_input(
                                    "Reps",
                                    min_value=0, max_value=200,
                                    value=int(default_r), step=1,
                                    key=f"{ex_name}_ws{i}_r",
                                )
                        all_set_inputs.append(("working", i, w, r))

                # Letzten Rekord anzeigen
                prev_max = db.get_max_weight_for_exercise(ex_name)
                if prev_max:
                    st.markdown(
                        f'<div style="color:{COLORS["text_muted"]};font-size:0.72rem;margin:6px 0 4px 0;">'
                        f'Bisheriger Rekord: <span style="color:{COLORS["accent_blue"]};font-weight:700;">'
                        f'{prev_max} kg</span></div>',
                        unsafe_allow_html=True,
                    )

                submitted = st.form_submit_button(
                    f"✅ {ex_name} speichern",
                    use_container_width=True,
                )

                if submitted:
                    # Nur Sätze mit Gewicht > 0 speichern
                    valid_sets = [(st_type, sn, wkg, rp)
                                  for st_type, sn, wkg, rp in all_set_inputs
                                  if wkg > 0 or rp > 0]
                    if valid_sets:
                        db.log_exercise_sets(ex_name, valid_sets)

                        # PR-Check
                        new_max = max((wkg for st_type, _, wkg, _ in valid_sets
                                       if st_type == "working"), default=0)
                        if prev_max is not None and new_max > prev_max:
                            st.success(pr_message(ex_name, new_max, prev_max))
                            st.balloons()
                        else:
                            st.success(motivational_message())
                        st.rerun()
                    else:
                        st.warning("Bitte mindestens einen Wert eingeben.")

            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

        # Workout abgeschlossen?
        if done_count == total_count and total_count > 0:
            st.markdown(
                f'<div style="background:linear-gradient(135deg,{COLORS["accent_green"]}22,{COLORS["accent_blue"]}11);'
                f'border:2px solid {COLORS["accent_green"]};border-radius:18px;'
                f'padding:24px 16px;text-align:center;margin-top:16px;">'
                f'<div style="font-size:2.5rem;">🏆</div>'
                f'<div style="color:{COLORS["accent_green"]};font-size:1.2rem;font-weight:800;margin-top:8px;">'
                f'WORKOUT ABGESCHLOSSEN!</div>'
                f'<div style="color:{COLORS["text_secondary"]};font-size:0.9rem;margin-top:6px;">'
                f'{selected_plan} – alle {total_count} Übungen erledigt. Absolute Bestie! 🔥</div></div>',
                unsafe_allow_html=True,
            )


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 2 – VERLAUF                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab_verlauf:

    st.markdown(
        f'<div style="color:{COLORS["text_secondary"]};font-size:0.8rem;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">Letzte 4 Wochen</div>',
        unsafe_allow_html=True,
    )

    trained_exercises = db.get_all_trained_exercises(weeks=4)

    if not trained_exercises:
        st.markdown(
            f'<div class="gym-card" style="text-align:center;padding:32px 16px;">'
            f'<div style="font-size:2rem;">📊</div>'
            f'<div style="color:{COLORS["text_secondary"]};font-size:0.9rem;margin-top:10px;">'
            f'Noch keine Daten. Starte dein erstes Training!</div></div>',
            unsafe_allow_html=True,
        )
    else:
        selected_ex = st.selectbox(
            "ÜBUNG",
            options=trained_exercises,
            key="verlauf_exercise",
        )

        if selected_ex:
            history = db.get_exercise_history(selected_ex, weeks=4)

            if history:
                import plotly.graph_objects as go

                # ── Metrik-Auswahl ─────────────────────────────────────────
                chart_metric = st.radio(
                    "METRIK",
                    options=["💪 Max-Gewicht", "📦 Gesamtvolumen", "⚡ 1RM (Epley)"],
                    horizontal=True,
                    key="verlauf_metric",
                )

                dates_asc = [h["log_date"]  for h in reversed(history)]

                # Werte je nach Metrik berechnen
                if chart_metric == "💪 Max-Gewicht":
                    y_vals    = [h["max_weight"] for h in reversed(history)]
                    y_suffix  = " kg"
                    line_col  = COLORS["accent_green"]
                    fill_col  = "rgba(57, 255, 20, 0.08)"
                    chart_lbl = f"🏋️ {selected_ex} – Max-Gewicht"
                    hover_fmt = "<b>%{y:.1f} kg</b><br>%{x}<extra></extra>"

                elif chart_metric == "📦 Gesamtvolumen":
                    y_vals    = [float(h["total_volume"]) for h in reversed(history)]
                    y_suffix  = " kg"
                    line_col  = COLORS["accent_blue"]
                    fill_col  = "rgba(0, 212, 255, 0.08)"
                    chart_lbl = f"📦 {selected_ex} – Gesamtvolumen"
                    hover_fmt = "<b>%{y:,.0f} kg</b><br>%{x}<extra></extra>"

                else:  # 1RM Epley: weight * (1 + reps / 30)
                    y_vals = []
                    for h in reversed(history):
                        avg_r = h["avg_reps"] if h["avg_reps"] else 1
                        orm   = round(float(h["max_weight"]) * (1 + float(avg_r) / 30), 1)
                        y_vals.append(orm)
                    y_suffix  = " kg"
                    line_col  = COLORS["accent_orange"]
                    fill_col  = "rgba(255, 149, 0, 0.08)"
                    chart_lbl = f"⚡ {selected_ex} – Geschätztes 1RM"
                    hover_fmt = "<b>~%{y:.1f} kg 1RM</b><br>%{x}<extra></extra>"

                # ── Chart ──────────────────────────────────────────────────
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates_asc, y=y_vals,
                    mode="lines+markers",
                    name=chart_metric,
                    line=dict(color=line_col, width=2.5, shape="spline"),
                    marker=dict(size=8, color=line_col,
                                line=dict(width=2, color=COLORS["bg_secondary"])),
                    fill="tozeroy",
                    fillcolor=fill_col,
                ))
                fig.update_traces(hovertemplate=hover_fmt)
                fig.update_layout(
                    title=dict(text=chart_lbl,
                               font=dict(size=13, color=COLORS["text_primary"]),
                               x=0, xanchor="left"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor=COLORS["bg_secondary"],
                    font=dict(color=COLORS["text_secondary"], family="Inter", size=11),
                    margin=dict(l=8, r=8, t=44, b=8),
                    xaxis=dict(type="date", gridcolor=COLORS["border"],
                               linecolor=COLORS["border"], tickfont=dict(size=9),
                               tickformat="%d.%m."),
                    yaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"],
                               ticksuffix=y_suffix, tickfont=dict(size=9)),
                    showlegend=False,
                    hovermode="x unified",
                    height=230,
                )
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": False})

                # ── Tabelle ────────────────────────────────────────────────
                st.markdown(
                    f'<div style="border-radius:14px;overflow:hidden;'
                    f'border:1px solid {COLORS["border"]};margin-top:12px;">'
                    f'<div class="history-row history-header">'
                    f'<span>Datum</span><span>Max-Gew.</span>'
                    f'<span>Volumen</span><span>1RM~</span></div>',
                    unsafe_allow_html=True,
                )

                for i, h in enumerate(history):
                    bg    = COLORS["bg_secondary"] if i % 2 == 0 else COLORS["bg_primary"]
                    avg_r = h["avg_reps"] if h["avg_reps"] else 1
                    orm   = round(float(h["max_weight"]) * (1 + float(avg_r) / 30), 1)
                    vol_str = f"{int(h['total_volume']):,}".replace(",", ".")
                    st.markdown(
                        f'<div class="history-row" style="background:{bg};">'
                        f'<span style="color:{COLORS["text_secondary"]};font-size:0.8rem;">{h["log_date"]}</span>'
                        f'<span style="color:{COLORS["accent_green"]};font-weight:800;">{h["max_weight"]} kg</span>'
                        f'<span style="color:{COLORS["accent_blue"]};font-weight:700;">{vol_str} kg</span>'
                        f'<span style="color:{COLORS["accent_orange"]};font-weight:700;">~{orm} kg</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

                # ── Trend-Berechnung ───────────────────────────────────────
                if len(history) >= 2:
                    first_w = history[-1]["max_weight"]
                    last_w  = history[0]["max_weight"]
                    diff    = round(float(last_w) - float(first_w), 1)
                    if diff > 0:
                        trend_msg = f"⬆️ +{diff} kg Max-Gewicht in 4 Wochen – du wirst stärker! 💪"
                        trend_col = COLORS["accent_green"]
                    elif diff < 0:
                        trend_msg = f"⬇️ {diff} kg – dran bleiben, es kommt zurück! 🔥"
                        trend_col = COLORS["accent_orange"]
                    else:
                        trend_msg = "➡️ Stabiles Niveau – steiger die Reps! 💡"
                        trend_col = COLORS["accent_blue"]

                    st.markdown(
                        f'<div style="background:{COLORS["bg_secondary"]};'
                        f'border:1px solid {COLORS["border"]};border-radius:12px;'
                        f'padding:12px 14px;margin-top:10px;'
                        f'color:{trend_col};font-size:0.88rem;font-weight:700;">'
                        f'{trend_msg}</div>',
                        unsafe_allow_html=True,
                    )


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 3 – GEWICHT                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab_gewicht:
    import pandas as _pd
    from datetime import timedelta as _td
    from datetime import date as _date

    # ── SECTION 1: Eingabe-Formular ────────────────────────────────────────
    latest, previous = db.get_last_two_weights()
    default_weight   = latest["weight_kg"] if latest else 80.0
    saved_goal       = db.get_setting("goal_weight")
    default_goal     = float(saved_goal) if saved_goal else 75.0
    saved_start      = db.get_setting("start_weight")
    default_start    = float(saved_start) if saved_start else default_weight

    # ── Wöchentlicher Check-in Status ──────────────────────────────────────
    today = _date.today()
    if latest:
        last_date = _pd.to_datetime(latest["log_date"]).date()
        days_since = (today - last_date).days
        # Gleiche ISO-Kalenderwoche?
        same_week = (today.isocalendar()[:2] == last_date.isocalendar()[:2])
        if same_week:
            _badge_color = COLORS["accent_green"]
            _badge_icon  = "✅"
            _badge_text  = f"Diese Woche bereits eingetragen · vor {days_since} Tag{'en' if days_since != 1 else ''}"
        elif days_since <= 14:
            _badge_color = COLORS["accent_orange"]
            _badge_icon  = "⏰"
            _badge_text  = f"Letzte Messung vor {days_since} Tagen – Zeit für den Wochen-Check-in!"
        else:
            _badge_color = COLORS["accent_red"]
            _badge_icon  = "🔴"
            _badge_text  = f"Letzte Messung vor {days_since} Tagen – nicht vergessen!"
    else:
        _badge_color = COLORS["accent_blue"]
        _badge_icon  = "👋"
        _badge_text  = "Erste Messung eintragen und loslegen!"

    st.markdown(
        f'<div style="background:{_badge_color}18;border:1px solid {_badge_color}50;'
        f'border-radius:14px;padding:10px 14px;margin-bottom:14px;'
        f'color:{_badge_color};font-size:0.82rem;font-weight:700;">'
        f'{_badge_icon} {_badge_text}</div>',
        unsafe_allow_html=True,
    )

    with st.form("weight_form", clear_on_submit=False):
        st.markdown(
            f'<div style="color:{COLORS["text_secondary"]};font-size:0.75rem;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">'
            f'⚖️ Wöchentliches Gewicht eintragen</div>',
            unsafe_allow_html=True,
        )

        col_w, col_g = st.columns(2)
        with col_w:
            body_weight_input = st.number_input(
                "GEWICHT (KG)",
                min_value=20.0, max_value=300.0,
                value=default_weight, step=0.1, format="%.1f",
            )
        with col_g:
            goal_weight_input = st.number_input(
                "ZIELGEWICHT (KG)",
                min_value=20.0, max_value=300.0,
                value=default_goal, step=0.1, format="%.1f",
            )

        submitted = st.form_submit_button(
            "💾 ÄNDERUNGEN SPEICHERN",
            use_container_width=True,
        )

    if submitted:
        db.log_body_weight(body_weight_input)
        db.set_setting("goal_weight", str(goal_weight_input))
        st.success("Gespeichert! Weiter so! 🔥")
        st.rerun()

    # ── Einstellungen & Reset (aufgeklappt nur wenn nötig) ─────────────────
    st.markdown("---")

    # ── SECTION 2: Metriken & Fortschritt ──────────────────────────────────
    latest, previous = db.get_last_two_weights()
    saved_goal       = db.get_setting("goal_weight")
    saved_start      = db.get_setting("start_weight")

    if latest:
        current_kg = latest["weight_kg"]
        goal_kg    = float(saved_goal) if saved_goal else None
        # Startgewicht: explizit gesetzt oder Fallback auf ältesten DB-Eintrag
        start_kg_setting = float(saved_start) if saved_start else None

        # st.metric Karten
        col1, col2 = st.columns(2)
        with col1:
            # Delta nur anzeigen wenn tatsächlich eine Änderung vorhanden ist
            if start_kg_setting is not None:
                delta_vs_start = round(current_kg - start_kg_setting, 1)
                # Badge weglassen wenn 0 – kein Unterschied zu zeigen
                if delta_vs_start != 0.0:
                    delta_label = f"{delta_vs_start:+.1f} kg vs. Start"
                else:
                    delta_label = None
            elif previous:
                delta_vs_start = round(current_kg - previous["weight_kg"], 1)
                delta_label    = f"{delta_vs_start:+.1f} kg vs. letzter Messung" if delta_vs_start != 0.0 else None
            else:
                delta_vs_start = None
                delta_label    = None
            st.metric(
                label="⚖️ Aktuell",
                value=f"{current_kg:.1f} kg",
                delta=delta_label,
                delta_color="inverse",
                help="Grün = abgenommen ✅  |  Rot = zugenommen" if delta_label else "",
            )
        with col2:
            if goal_kg is not None:
                remaining = round(current_kg - goal_kg, 1)
                if remaining <= 0:
                    st.metric(label="🏆 Zum Ziel", value="ERREICHT!", delta="🎯 Glückwunsch")
                else:
                    st.metric(
                        label="🎯 Zum Ziel",
                        value=f"{remaining:.1f} kg",
                        delta=f"Ziel: {goal_kg:.1f} kg",
                        delta_color="off",
                    )

        # Fortschrittsbalken – basiert auf Startgewicht-Setting, nicht altem DB-Eintrag
        if goal_kg is not None and start_kg_setting is not None:
            start_kg     = start_kg_setting
            total_change = abs(start_kg - goal_kg)
            done_change  = abs(start_kg - current_kg)
            progress_pct = min(1.0, done_change / total_change) if total_change > 0 else 1.0

            direction_ok = (goal_kg < start_kg and current_kg <= start_kg) or \
                           (goal_kg > start_kg and current_kg >= start_kg)
            if not direction_ok:
                progress_pct = 0.0

            st.markdown(
                f'<div style="color:{COLORS["text_muted"]};font-size:0.7rem;font-weight:700;'
                f'text-transform:uppercase;letter-spacing:0.07em;margin-top:12px;margin-bottom:4px;">'
                f'Fortschritt zum Ziel '
                f'<span style="float:right;color:{COLORS["text_secondary"]};">{int(progress_pct*100)} %</span></div>',
                unsafe_allow_html=True,
            )
            st.progress(progress_pct)
        elif goal_kg is not None:
            # Kein Startgewicht gesetzt: Nutzer auffordern
            st.markdown(
                f'<div style="color:{COLORS["accent_orange"]};font-size:0.78rem;font-weight:600;'
                f'margin-top:10px;">📍 Bitte Startgewicht im Formular oben setzen, um den Fortschrittsbalken zu aktivieren.</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── SECTION 3: Chart mit Moving Average ───────────────────────────────
    weight_history = db.get_weight_history(weeks=16)

    if len(weight_history) >= 1:
        import plotly.graph_objects as go

        df = _pd.DataFrame(weight_history)
        df["log_date"] = _pd.to_datetime(df["log_date"])
        df = df.sort_values("log_date").reset_index(drop=True)
        saved_goal = db.get_setting("goal_weight")
        goal_kg    = float(saved_goal) if saved_goal else None

        # Deduplizieren auf Tagesebene (Datum ohne Uhrzeit)
        df["date_str"] = df["log_date"].dt.strftime("%d.%m.")
        df = df.drop_duplicates(subset=["date_str"]).reset_index(drop=True)

        # 4-Wochen Moving Average (sinnvoll bei wöchentlichen Messungen)
        df["ma4w"] = df["weight_kg"].rolling(window=4, min_periods=1).mean()

        dates_lbl = df["date_str"].tolist()
        weights   = df["weight_kg"].tolist()
        ma4w      = df["ma4w"].round(2).tolist()

        all_vals = weights + ([goal_kg] if goal_kg else [])
        y_min = round(min(all_vals) - 1.5, 1)
        y_max = round(max(all_vals) + 1.5, 1)

        fig = go.Figure()

        # Wöchentliche Messpunkte als Linie + Marker
        fig.add_trace(go.Scatter(
            x=dates_lbl, y=weights,
            mode="lines+markers",
            name="Wochenmessung",
            marker=dict(size=8, color=COLORS["accent_blue"],
                        line=dict(width=2, color=COLORS["bg_secondary"])),
            line=dict(color=COLORS["accent_blue"], width=2, dash="dot"),
            hovertemplate="<b>%{y:.1f} kg</b><br>%{x}<extra>Wochenmessung</extra>",
        ))

        # 4-Wochen-Trend als Hauptlinie
        if len(weights) >= 2:
            fig.add_trace(go.Scatter(
                x=dates_lbl, y=ma4w,
                mode="lines",
                name="Ø 4 Wochen",
                line=dict(color=COLORS["accent_green"], width=3, shape="spline"),
                fill="tozeroy", fillcolor="rgba(0, 212, 255, 0.06)",
                hovertemplate="<b>Ø %{y:.1f} kg</b><br>%{x}<extra>4-Wochen-Schnitt</extra>",
            ))

        # Zielgewicht-Linie
        if goal_kg is not None:
            fig.add_hline(
                y=goal_kg,
                line_dash="dash",
                line_color=COLORS["accent_green"],
                line_width=2,
                annotation_text=f"🎯 {goal_kg:.1f} kg",
                annotation_font_color=COLORS["accent_green"],
                annotation_font_size=10,
                annotation_position="top right",
            )

        fig.update_layout(
            title=dict(text="⚖️ Wöchentlicher Gewichtsverlauf & Trend",
                       font=dict(size=13, color=COLORS["text_primary"]),
                       x=0, xanchor="left"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=COLORS["bg_secondary"],
            font=dict(color=COLORS["text_secondary"], family="Inter", size=11),
            margin=dict(l=8, r=8, t=44, b=8),
            xaxis=dict(type="category", gridcolor=COLORS["border"],
                       linecolor=COLORS["border"], tickfont=dict(size=9),
                       tickmode="array",
                       tickvals=dates_lbl,
                       ticktext=dates_lbl),
            yaxis=dict(gridcolor=COLORS["border"], linecolor=COLORS["border"],
                       ticksuffix=" kg", tickfont=dict(size=9),
                       range=[y_min, y_max]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1,
                        font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
            hovermode="x unified",
            height=270,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # ── SECTION 4: Prognose ────────────────────────────────────────────────
    weight_history = db.get_weight_history(weeks=16)
    saved_goal     = db.get_setting("goal_weight")

    if saved_goal and len(weight_history) >= 2:
        goal_kg = float(saved_goal)

        # Letzten 8 Wochen (8 Messpunkte) für die Rate nutzen
        df_prog = _pd.DataFrame(weight_history)
        df_prog["log_date"] = _pd.to_datetime(df_prog["log_date"])
        df_prog = df_prog.sort_values("log_date").reset_index(drop=True)

        window_days = min(8, len(df_prog))
        df_window   = df_prog.tail(window_days)

        d_first = df_window["log_date"].iloc[0]
        d_last  = df_window["log_date"].iloc[-1]
        kg_first = df_window["weight_kg"].iloc[0]
        kg_last  = df_window["weight_kg"].iloc[-1]
        days_span = (d_last - d_first).days

        if days_span > 0:
            daily_rate = (kg_last - kg_first) / days_span

            going_right_dir = (daily_rate < 0 and goal_kg < kg_last) or \
                              (daily_rate > 0 and goal_kg > kg_last)

            if going_right_dir and abs(daily_rate) > 0.001:
                days_needed = abs(kg_last - goal_kg) / abs(daily_rate)
                target_date = d_last.date() + _td(days=int(days_needed))
                weekly_rate = round(daily_rate * 7, 2)
                trend_color = COLORS["accent_green"] if daily_rate < 0 else COLORS["accent_blue"]

                # Motivationstext
                if days_needed <= 30:
                    moti = "🔥 Fast geschafft – Endspurt!"
                elif days_needed <= 90:
                    moti = "💪 Auf einem guten Weg!"
                else:
                    moti = "🎯 Konstant dran bleiben!"

                st.markdown(
                    f'<div style="background:linear-gradient(135deg,{trend_color}12,{COLORS["bg_secondary"]});'
                    f'border:1px solid {trend_color}40;border-radius:18px;padding:18px 16px;margin:4px 0 12px 0;">'
                    f'<div style="color:{trend_color};font-size:0.72rem;font-weight:800;'
                    f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;">'
                    f'🔮 Prognose · Letzten {window_days} Messungen als Basis</div>'
                    f'<div style="display:flex;justify-content:space-between;gap:6px;text-align:center;">'
                    f'<div style="flex:1;background:{COLORS["bg_primary"]}88;border-radius:12px;padding:10px 6px;">'
                    f'<div style="font-size:1.5rem;font-weight:900;color:{trend_color};line-height:1.1;">{int(days_needed)}</div>'
                    f'<div style="color:{COLORS["text_muted"]};font-size:0.68rem;margin-top:3px;">Tage noch</div></div>'
                    f'<div style="flex:1;background:{COLORS["bg_primary"]}88;border-radius:12px;padding:10px 6px;">'
                    f'<div style="font-size:1.25rem;font-weight:900;color:{COLORS["text_primary"]};line-height:1.1;">{target_date.strftime("%d.%m.%y")}</div>'
                    f'<div style="color:{COLORS["text_muted"]};font-size:0.68rem;margin-top:3px;">Zieldatum</div></div>'
                    f'<div style="flex:1;background:{COLORS["bg_primary"]}88;border-radius:12px;padding:10px 6px;">'
                    f'<div style="font-size:1.5rem;font-weight:900;color:{trend_color};line-height:1.1;">{weekly_rate:+.2f}</div>'
                    f'<div style="color:{COLORS["text_muted"]};font-size:0.68rem;margin-top:3px;">kg/Woche</div></div></div>'
                    f'<div style="text-align:center;margin-top:10px;color:{trend_color};font-size:0.82rem;font-weight:700;">'
                    f'{moti}</div></div>',
                    unsafe_allow_html=True,
                )

            elif not going_right_dir and abs(daily_rate) > 0.001:
                st.markdown(
                    f'<div style="background:{COLORS["bg_secondary"]};border:1px solid {COLORS["accent_red"]}40;'
                    f'border-radius:14px;padding:14px;margin:4px 0 12px 0;'
                    f'color:{COLORS["accent_orange"]};font-size:0.88rem;font-weight:700;text-align:center;">'
                    f'⚠️ Dein Trend geht gerade in die falsche Richtung – dran bleiben! 💪</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="background:{COLORS["bg_secondary"]};border:1px solid {COLORS["border"]};'
                    f'border-radius:14px;padding:14px;margin:4px 0 12px 0;'
                    f'color:{COLORS["text_muted"]};font-size:0.82rem;text-align:center;">'
                    f'📊 Noch zu wenig Bewegung im Gewicht für eine Prognose. Trag dich wöchentlich ein!</div>',
                    unsafe_allow_html=True,
                )
    elif not saved_goal:
        st.markdown(
            f'<div style="background:{COLORS["bg_secondary"]};border:1px solid {COLORS["border"]};'
            f'border-radius:14px;padding:14px;margin:4px 0 12px 0;'
            f'color:{COLORS["text_muted"]};font-size:0.82rem;text-align:center;">'
            f'Trag oben ein Zielgewicht ein, um deine Prognose zu sehen. 🎯</div>',
            unsafe_allow_html=True,
        )


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 4 – PLAN-EDITOR                                                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝

with tab_plaene:

    st.markdown(
        f'<div style="color:{COLORS["text_secondary"]};font-size:0.8rem;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px;">'
        f'Trainingsplan bearbeiten</div>',
        unsafe_allow_html=True,
    )

    # Plan auswählen
    all_plans = db.get_all_plans()
    selected_edit_plan = st.selectbox(
        "Plan wählen",
        options=all_plans,
        key="editor_plan_select",
    )

    if selected_edit_plan:
        exercises = db.get_plan_exercises(selected_edit_plan)

        st.markdown(
            f'<div style="color:{COLORS["text_muted"]};font-size:0.72rem;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.07em;margin:14px 0 8px 0;">'
            f'{len(exercises)} Übungen</div>',
            unsafe_allow_html=True,
        )

        # ── Bestehende Übungen ────────────────────────────────────────────
        for ex in exercises:
            ex_name = ex["exercise_name"]
            with st.container():
                st.markdown(
                    f'<div style="background:{COLORS["bg_secondary"]};border:1px solid {COLORS["border"]};'
                    f'border-radius:14px;padding:12px 14px 8px 14px;margin-bottom:8px;">'
                    f'<div style="font-size:0.92rem;font-weight:800;color:{COLORS["text_primary"]};'
                    f'margin-bottom:10px;">{ex_name}</div></div>',
                    unsafe_allow_html=True,
                )

                col_wu, col_ws, col_up, col_down, col_del = st.columns([2, 2, 1, 1, 1])

                with col_wu:
                    new_wu = st.number_input(
                        "Aufwärm",
                        min_value=0, max_value=5,
                        value=int(ex["warmup_sets"]),
                        step=1,
                        key=f"ed_wu_{selected_edit_plan}_{ex_name}",
                    )
                with col_ws:
                    new_ws = st.number_input(
                        "Arbeit",
                        min_value=1, max_value=10,
                        value=int(ex["working_sets"]),
                        step=1,
                        key=f"ed_ws_{selected_edit_plan}_{ex_name}",
                    )
                with col_up:
                    st.markdown('<div style="padding-top:24px;"></div>', unsafe_allow_html=True)
                    if st.button("↑", key=f"up_{selected_edit_plan}_{ex_name}", use_container_width=True):
                        db.move_exercise(selected_edit_plan, ex_name, "up")
                        st.rerun()
                with col_down:
                    st.markdown('<div style="padding-top:24px;"></div>', unsafe_allow_html=True)
                    if st.button("↓", key=f"dn_{selected_edit_plan}_{ex_name}", use_container_width=True):
                        db.move_exercise(selected_edit_plan, ex_name, "down")
                        st.rerun()
                with col_del:
                    st.markdown('<div style="padding-top:24px;"></div>', unsafe_allow_html=True)
                    if st.button("🗑", key=f"del_{selected_edit_plan}_{ex_name}", use_container_width=True):
                        db.remove_exercise_from_plan(selected_edit_plan, ex_name)
                        st.rerun()

                # Sätze speichern wenn geändert
                if new_wu != int(ex["warmup_sets"]) or new_ws != int(ex["working_sets"]):
                    db.update_exercise_sets(selected_edit_plan, ex_name, new_wu, new_ws)

        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="height:1px;background:{COLORS["border"]};margin:8px 0 16px 0;"></div>',
            unsafe_allow_html=True,
        )

        # ── Neue Übung hinzufügen ─────────────────────────────────────────
        st.markdown(
            f'<div style="color:{COLORS["text_secondary"]};font-size:0.78rem;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">'
            f'➕ Neue Übung</div>',
            unsafe_allow_html=True,
        )

        with st.form(key=f"add_exercise_{selected_edit_plan}", clear_on_submit=True):
            new_name = st.text_input(
                "Übungsname",
                placeholder="z.B. Bizeps Curls Maschine",
                key=f"new_ex_name_{selected_edit_plan}",
            )
            col_a, col_b = st.columns(2)
            with col_a:
                add_wu = st.number_input("Aufwärmsätze", min_value=0, max_value=5, value=1, step=1)
            with col_b:
                add_ws = st.number_input("Arbeitssätze",  min_value=1, max_value=10, value=3, step=1)

            if st.form_submit_button("➕ Hinzufügen", use_container_width=True):
                if new_name.strip():
                    db.add_exercise_to_plan(selected_edit_plan, new_name.strip(), add_wu, add_ws)
                    st.success(f"✅ '{new_name.strip()}' hinzugefügt!")
                    st.rerun()
                else:
                    st.warning("Bitte einen Namen eingeben.")
