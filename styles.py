"""
GYM-APP | styles.py
===================
Custom-CSS Dark-Design für Streamlit.
Einbinden via: st.markdown(get_css(), unsafe_allow_html=True)

Design-Sprache:
  - Tiefes Anthrazit / Near-Black als Basis
  - Neon-Grün (#39FF14) als primäre Akzentfarbe (Erfolg, PRs, CTAs)
  - Cyberpunk-Rot (#FF2D55) für Warnungen & kritische Aktionen
  - Elektro-Blau (#00D4FF) für sekundäre Highlights & Charts
  - Schrift: System-UI Stack (schnell, nativ auf iOS/Android)
"""


# ---------------------------------------------------------------------------
# Farb-Palette (auch für Plotly-Charts nutzbar)
# ---------------------------------------------------------------------------

COLORS = {
    "bg_primary":    "#0D0D0D",   # Tiefes Schwarz – App-Hintergrund
    "bg_secondary":  "#1A1A1A",   # Anthrazit – Cards, Sidebar
    "bg_tertiary":   "#242424",   # Mittleres Grau – Inputs, Tabellen
    "bg_hover":      "#2E2E2E",   # Leichtes Heben bei Hover

    "accent_green":  "#39FF14",   # Neon-Grün  – PRs, Erfolge, CTA
    "accent_red":    "#FF2D55",   # Cyberpunk-Rot – Verlust, Lösch-Aktionen
    "accent_blue":   "#00D4FF",   # Elektro-Blau – Sekundär-Info, Charts
    "accent_orange": "#FF9500",   # Energie-Orange – Streak, Badges

    "text_primary":  "#F0F0F0",   # Fast-Weiß – Haupttext
    "text_secondary":"#8A8A8A",   # Grau – Labels, Hints
    "text_muted":    "#555555",   # Sehr gedämpft – Divider-Text

    "border":        "#2A2A2A",   # Subtile Card-Borders
    "success":       "#39FF14",
    "danger":        "#FF2D55",
    "info":          "#00D4FF",
}


def get_css() -> str:
    """
    Gibt den vollständigen CSS-String zurück, der per st.markdown()
    in die Streamlit-App injiziert wird.
    """
    c = COLORS
    return f"""
<style>
/* =====================================================================
   1. GLOBAL RESET & BASE
   ===================================================================== */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                 Roboto, Helvetica, Arial, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* App-Hintergrund */
.stApp {{
    background-color: {c['bg_primary']} !important;
    color: {c['text_primary']} !important;
}}

/* Streamlit-Main-Block */
.block-container {{
    padding: 1rem 1rem 4rem 1rem !important;  /* Bottom-Padding für mobile Nav */
    max-width: 480px !important;               /* Mobile-Breite fixieren */
    margin: 0 auto !important;
}}

/* =====================================================================
   2. HEADER & TITEL
   ===================================================================== */

h1, h2, h3, h4 {{
    color: {c['text_primary']} !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}}

h1 {{
    font-size: 1.8rem !important;
    background: linear-gradient(135deg, {c['accent_green']}, {c['accent_blue']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem !important;
}}

h2 {{
    font-size: 1.2rem !important;
    color: {c['text_secondary']} !important;
    font-weight: 600 !important;
}}

h3 {{
    font-size: 1.05rem !important;
    margin-top: 1.2rem !important;
}}

/* =====================================================================
   3. TABS – SAUBER & TOUCH-FREUNDLICH
   ===================================================================== */

.stTabs [data-baseweb="tab-list"] {{
    background: {c['bg_secondary']} !important;
    border-radius: 16px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid {c['border']} !important;
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    border-radius: 12px !important;
    color: {c['text_secondary']} !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 10px 16px !important;
    border: none !important;
    transition: all 0.2s ease !important;
    flex: 1 !important;
    text-align: center !important;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {c['accent_green']}22, {c['accent_blue']}22) !important;
    color: {c['accent_green']} !important;
    border: 1px solid {c['accent_green']}44 !important;
}}

.stTabs [data-baseweb="tab-highlight"] {{
    display: none !important;
}}

.stTabs [data-baseweb="tab-border"] {{
    display: none !important;
}}

/* =====================================================================
   4. BUTTONS – GROSSE TOUCH-TARGETS
   ===================================================================== */

/* Primärer CTA-Button */
.stButton > button {{
    background: linear-gradient(135deg, {c['accent_green']}, #2BC40F) !important;
    color: #000000 !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 14px 24px !important;
    width: 100% !important;
    min-height: 52px !important;         /* Großes Touch-Target */
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 4px 20px {c['accent_green']}33 !important;
    -webkit-tap-highlight-color: transparent !important;
}}

.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px {c['accent_green']}55 !important;
    background: linear-gradient(135deg, #45FF20, {c['accent_green']}) !important;
}}

.stButton > button:active {{
    transform: translateY(0px) scale(0.98) !important;
    box-shadow: 0 2px 10px {c['accent_green']}33 !important;
}}

/* Sekundärer Button (type="secondary") */
.stButton > button[kind="secondary"] {{
    background: {c['bg_tertiary']} !important;
    color: {c['text_primary']} !important;
    border: 1px solid {c['border']} !important;
    box-shadow: none !important;
}}

/* =====================================================================
   5. INPUTS & SELECTS
   ===================================================================== */

/* Selectbox & Number Input */
.stSelectbox > div > div,
.stNumberInput > div > div > input,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    background-color: {c['bg_tertiary']} !important;
    color: {c['text_primary']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    padding: 12px 16px !important;
    min-height: 48px !important;
    transition: border-color 0.2s ease !important;
}}

.stSelectbox > div > div:focus-within,
.stNumberInput > div > div:focus-within,
.stTextInput > div > div:focus-within {{
    border-color: {c['accent_green']} !important;
    box-shadow: 0 0 0 2px {c['accent_green']}22 !important;
}}

/* Label-Texte */
.stSelectbox label,
.stNumberInput label,
.stTextInput label,
.stTextArea label,
.stSlider label {{
    color: {c['text_secondary']} !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    margin-bottom: 4px !important;
}}

/* Dropdown-Liste */
[data-baseweb="popover"] {{
    background: {c['bg_secondary']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 12px !important;
}}

[data-baseweb="menu"] li {{
    background: transparent !important;
    color: {c['text_primary']} !important;
}}

[data-baseweb="menu"] li:hover {{
    background: {c['bg_hover']} !important;
}}

/* =====================================================================
   6. METRIC WIDGETS (für Weight-Progress)
   ===================================================================== */

[data-testid="metric-container"] {{
    background: {c['bg_secondary']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 16px !important;
    padding: 16px !important;
}}

[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: {c['text_primary']} !important;
}}

[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    font-size: 0.95rem !important;
    font-weight: 700 !important;
}}

[data-testid="metric-container"] [data-testid="stMetricLabel"] {{
    color: {c['text_secondary']} !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}}

/* =====================================================================
   7. DATAFRAME / TABELLEN
   ===================================================================== */

.stDataFrame, [data-testid="stDataFrame"] {{
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid {c['border']} !important;
}}

.stDataFrame thead tr th {{
    background: {c['bg_secondary']} !important;
    color: {c['text_secondary']} !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    border-bottom: 1px solid {c['border']} !important;
}}

.stDataFrame tbody tr {{
    background: {c['bg_primary']} !important;
    border-bottom: 1px solid {c['border']} !important;
}}

.stDataFrame tbody tr:nth-child(even) {{
    background: {c['bg_secondary']} !important;
}}

/* =====================================================================
   8. SUCCESS / ERROR / INFO NOTIFICATIONS
   ===================================================================== */

.stSuccess {{
    background: {c['accent_green']}15 !important;
    border: 1px solid {c['accent_green']}55 !important;
    border-radius: 12px !important;
    color: {c['accent_green']} !important;
}}

.stError {{
    background: {c['accent_red']}15 !important;
    border: 1px solid {c['accent_red']}55 !important;
    border-radius: 12px !important;
    color: {c['accent_red']} !important;
}}

.stInfo {{
    background: {c['accent_blue']}15 !important;
    border: 1px solid {c['accent_blue']}55 !important;
    border-radius: 12px !important;
    color: {c['accent_blue']} !important;
}}

.stWarning {{
    background: {c['accent_orange']}15 !important;
    border: 1px solid {c['accent_orange']}55 !important;
    border-radius: 12px !important;
    color: {c['accent_orange']} !important;
}}

/* =====================================================================
   9. CUSTOM CARD-KOMPONENTE (via st.markdown)
   ===================================================================== */

/* Nutzung: st.markdown('<div class="gym-card">...</div>', unsafe_allow_html=True) */
.gym-card {{
    background: {c['bg_secondary']};
    border: 1px solid {c['border']};
    border-radius: 16px;
    padding: 16px;
    margin: 8px 0;
}}

.gym-card-accent {{
    background: linear-gradient(135deg, {c['accent_green']}10, {c['bg_secondary']});
    border: 1px solid {c['accent_green']}33;
    border-radius: 16px;
    padding: 16px;
    margin: 8px 0;
}}

/* PR-Badge */
.pr-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, {c['accent_green']}, {c['accent_blue']});
    color: #000;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin: 4px 0;
}}

/* Streak-Badge */
.streak-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, {c['accent_orange']}22, {c['bg_secondary']});
    border: 1px solid {c['accent_orange']}55;
    color: {c['accent_orange']};
    font-size: 1rem;
    font-weight: 700;
    padding: 10px 16px;
    border-radius: 14px;
    width: 100%;
}}

.streak-number {{
    font-size: 1.8rem;
    font-weight: 800;
    color: {c['accent_orange']};
    line-height: 1;
}}

/* Set-Row in der heutigen Trainingsübersicht */
.set-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    background: {c['bg_tertiary']};
    border-radius: 10px;
    margin: 4px 0;
    border-left: 3px solid {c['accent_green']}55;
}}

.set-row-number {{
    color: {c['text_secondary']};
    font-size: 0.8rem;
    font-weight: 700;
    min-width: 28px;
}}

.set-row-weight {{
    color: {c['text_primary']};
    font-size: 1.05rem;
    font-weight: 700;
}}

.set-row-reps {{
    color: {c['accent_green']};
    font-size: 0.9rem;
    font-weight: 600;
}}

/* Divider */
.gym-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {c['border']}, transparent);
    margin: 16px 0;
}}

/* =====================================================================
   10. STREAMLIT VERSTECKTE ELEMENTE (Cleaner Look)
   ===================================================================== */

/* Footer + Hamburger Menu ausblenden */
#MainMenu,
footer,
header[data-testid="stHeader"] {{
    display: none !important;
}}

/* Deploy-Button ausblenden */
.stDeployButton {{
    display: none !important;
}}

/* Sidebar ausblenden (wir nutzen Tabs statt Sidebar) */
[data-testid="stSidebar"] {{
    display: none !important;
}}

/* Scrollbar-Styling */
::-webkit-scrollbar {{
    width: 4px;
    height: 4px;
}}

::-webkit-scrollbar-track {{
    background: {c['bg_primary']};
}}

::-webkit-scrollbar-thumb {{
    background: {c['border']};
    border-radius: 2px;
}}

/* =====================================================================
   11. PLOTLY CHART INTEGRATION
   ===================================================================== */

.stPlotlyChart {{
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid {c['border']} !important;
}}

/* =====================================================================
   12. ANIMATIONS
   ===================================================================== */

@keyframes pulse-green {{
    0%   {{ box-shadow: 0 0 0 0 {c['accent_green']}66; }}
    70%  {{ box-shadow: 0 0 0 12px {c['accent_green']}00; }}
    100% {{ box-shadow: 0 0 0 0 {c['accent_green']}00; }}
}}

@keyframes slide-in {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.animate-slide-in {{
    animation: slide-in 0.3s ease forwards;
}}

.animate-pulse-green {{
    animation: pulse-green 1.5s ease infinite;
}}

</style>
"""


# ---------------------------------------------------------------------------
# Hilfsfunktionen für Inline-HTML-Komponenten
# ---------------------------------------------------------------------------

def pr_banner_html(exercise: str, pr_type: str) -> str:
    """
    Erzeugt ein animiertes PR-Banner als HTML-String.

    Args:
        exercise: Name der Übung
        pr_type:  Art des PRs – "weight", "volume" oder "reps"
    """
    icons   = {"weight": "🏋️", "volume": "📈", "reps": "🔁"}
    labels  = {"weight": "NEUES MAX-GEWICHT", "volume": "NEUES REKORD-VOLUMEN", "reps": "NEUER WIEDERHOLUNGS-REKORD"}
    icon    = icons.get(pr_type, "🏆")
    label   = labels.get(pr_type, "PERSONAL RECORD")

    return f"""
    <div class="animate-slide-in" style="
        background: linear-gradient(135deg, {COLORS['accent_green']}22, {COLORS['accent_blue']}11);
        border: 2px solid {COLORS['accent_green']};
        border-radius: 18px;
        padding: 18px 16px;
        margin: 12px 0;
        text-align: center;
        animation: slide-in 0.4s ease, pulse-green 2s ease 0.5s;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 4px;">{icon}</div>
        <div style="
            color: {COLORS['accent_green']};
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        ">{label}</div>
        <div style="
            color: {COLORS['text_primary']};
            font-size: 1.1rem;
            font-weight: 700;
            margin-top: 4px;
        ">{exercise}</div>
        <div class="pr-badge" style="margin: 8px auto; width: fit-content;">
            ⚡ Personal Record
        </div>
    </div>
    """


def set_row_html(set_number: int, weight_kg: float, reps: int, is_pr: bool = False) -> str:
    """Rendert eine einzelne Satz-Zeile in der Tagesübersicht."""
    border_color = COLORS['accent_green'] if is_pr else COLORS['accent_green'] + "55"
    pr_tag       = ' <span class="pr-badge" style="font-size:0.6rem;padding:2px 8px;">PR</span>' if is_pr else ""

    return f"""
    <div class="set-row" style="border-left-color: {border_color};">
        <span class="set-row-number">#{set_number}</span>
        <span class="set-row-weight">{weight_kg} kg{pr_tag}</span>
        <span class="set-row-reps">{reps} Reps</span>
    </div>
    """


def streak_card_html(current: int, longest: int) -> str:
    """Rendert die Streak-Karte mit aktuellem und bestem Wert."""
    flame = "🔥" * min(current, 5) if current > 0 else "💤"

    return f"""
    <div class="gym-card" style="text-align: center;">
        <div style="color: {COLORS['text_secondary']}; font-size: 0.75rem; font-weight: 700;
                    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
            Trainings-Streak
        </div>
        <div style="font-size: 3rem; line-height: 1;">{flame}</div>
        <div class="streak-number" style="margin: 6px 0;">{current}</div>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.85rem;">
            {"Tag" if current == 1 else "Tage"} in Folge
        </div>
        <div style="color: {COLORS['text_muted']}; font-size: 0.75rem; margin-top: 8px;">
            Bestleistung: {longest} {"Tag" if longest == 1 else "Tage"}
        </div>
    </div>
    """
