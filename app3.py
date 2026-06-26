import pandas as pd
import streamlit as st
import plotly.express as px
import streamlit.components.v1 as components
from pathlib import Path
from html import escape
from urllib.parse import quote

# ------------------------------------------------------------
# Vizuális téma
# ------------------------------------------------------------
COLOR_PRIMARY = "#38bdf8"
COLOR_SECONDARY = "#2dd4bf"
COLOR_ACCENT = "#fb923c"
COLOR_PURPLE = "#a78bfa"
COLOR_PINK = "#f472b6"
COLOR_BG = "#111827"
COLOR_PANEL = "#172033"
COLOR_TEXT = "#e5e7eb"
COLOR_MUTED = "#94a3b8"
PLOTLY_COLORS = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT, COLOR_PURPLE, COLOR_PINK, "#60a5fa"]


# ============================================================
# Streamlit dashboard váz - Call Center adatok
# Bemenet: callcenter_gzs01.xlsx
# ============================================================

st.set_page_config(
    page_title="Call Center dashboard",
    page_icon="☎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# CSS - dashboard kinézet
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', Arial, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(56, 189, 248, 0.20), transparent 30%),
            radial-gradient(circle at top right, rgba(45, 212, 191, 0.16), transparent 32%),
            radial-gradient(circle at bottom right, rgba(167, 139, 250, 0.14), transparent 35%),
            linear-gradient(135deg, #0b1120 0%, #111827 45%, #1f2937 100%);
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0b1220 58%, #111827 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.22);
        box-shadow: 12px 0 30px rgba(0, 0, 0, 0.22);
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stCaptionContainer {
        color: #e5e7eb !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] *,
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        color: #0f172a !important;
    }

    section[data-testid="stSidebar"] [data-testid="stDateInput"] input {
        color: #0f172a !important;
        background-color: #f8fafc !important;
    }

    .dashboard-hero {
        background:
            linear-gradient(135deg, rgba(14, 165, 233, 0.92) 0%, rgba(15, 118, 110, 0.92) 52%, rgba(15, 23, 42, 0.96) 100%);
        border-radius: 28px;
        padding: 28px 32px;
        color: white;
        box-shadow: 0 24px 55px rgba(0, 0, 0, 0.36);
        margin-bottom: 22px;
        border: 1px solid rgba(125, 211, 252, 0.28);
    }

    .dashboard-title {
        font-size: 39px;
        font-weight: 800;
        margin-bottom: 7px;
        color: #ffffff;
        letter-spacing: -0.03em;
    }

    .dashboard-subtitle {
        font-size: 15px;
        color: rgba(255,255,255,0.84);
        margin-bottom: 0px;
    }

    .kpi-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.96), rgba(15, 23, 42, 0.96));
        backdrop-filter: blur(12px);
        padding: 21px 22px;
        border-radius: 22px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        box-shadow: 0 18px 42px rgba(0, 0, 0, 0.28);
        min-height: 132px;
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #38bdf8, #2dd4bf, #fb923c, #a78bfa);
    }

    .kpi-label {
        font-size: 13px;
        color: #94a3b8;
        margin-bottom: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .kpi-value {
        font-size: 33px;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.05;
    }

    .kpi-note {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 10px;
    }

    .section-title {
        color: #e5e7eb;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-top: 8px;
    }

    div[data-testid="stPlotlyChart"] {
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.92), rgba(15, 23, 42, 0.92));
        border: 1px solid rgba(148, 163, 184, 0.26);
        border-radius: 22px;
        padding: 12px;
        box-shadow: 0 18px 42px rgba(0, 0, 0, 0.26);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.90);
        color: #e5e7eb;
        border-radius: 14px 14px 0 0;
        padding: 10px 16px;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.22), rgba(45, 212, 191, 0.18));
        color: #ffffff !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.25);
        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.24);
        background: rgba(15, 23, 42, 0.92);
    }

    h1, h2, h3, h4, h5, h6, p, .stMarkdown {
        color: #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Segédfüggvények
# ------------------------------------------------------------
@st.cache_data
def load_data(excel_path: str) -> pd.DataFrame:
    df1 = pd.read_excel(excel_path)

    # Biztonsági átnevezés arra az esetre, ha az Excelben elgépelve szerepelne az oszlopnév.
    if "Satisfaction rating" not in df1.columns and "Staisfaction rating" in df1.columns:
        df1 = df1.rename(columns={"Staisfaction rating": "Satisfaction rating"})

    df1["Date"] = pd.to_datetime(df1["Date"], errors="coerce")
    df1["Satisfaction rating"] = pd.to_numeric(df1["Satisfaction rating"], errors="coerce")
    df1["Speed of answer in seconds"] = pd.to_numeric(
        df1["Speed of answer in seconds"], errors="coerce"
    )

    # AvgTalkDuration átalakítása másodpercre.
    duration_td = pd.to_timedelta(df1["AvgTalkDuration"].astype(str), errors="coerce")
    df1["TalkDurationSeconds"] = duration_td.dt.total_seconds()
    df1["TalkDurationMinutes"] = df1["TalkDurationSeconds"] / 60

    # Idősávok beszélgetési hossz alapján.
    bins = [0, 60, 180, 300, float("inf")]
    labels = ["0-1 perc", "1-3 perc", "3-5 perc", "5+ perc"]
    df1["TalkDurationSlot"] = pd.cut(
        df1["TalkDurationSeconds"], bins=bins, labels=labels, include_lowest=True
    )

    # Idődimenziók.
    df1["Nap"] = df1["Date"].dt.date
    df1["Het"] = df1["Date"].dt.to_period("W").astype(str)
    df1["Honap"] = df1["Date"].dt.to_period("M").astype(str)

    # Naptári napok magyar megnevezéssel.
    day_map = {
        0: "Hétfő",
        1: "Kedd",
        2: "Szerda",
        3: "Csütörtök",
        4: "Péntek",
        5: "Szombat",
        6: "Vasárnap",
    }
    df1["HetNapSzama"] = df1["Date"].dt.weekday
    df1["NaptariNap"] = df1["HetNapSzama"].map(day_map)

    return df1


def format_seconds_to_mmss(seconds: float) -> str:
    if pd.isna(seconds):
        return "-"
    minutes = int(seconds // 60)
    sec = int(round(seconds % 60))
    return f"{minutes:02d}:{sec:02d}"


def yes_rate(series: pd.Series) -> float:
    if len(series) == 0:
        return 0.0
    return (series.astype(str).str.upper().str.strip() == "Y").mean() * 100


def render_kpi(label: str, value: str, note: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_agent_photo_url(agent_name: str) -> str:
    """Stabil, internetes avatar URL agent név alapján.

    A seed miatt ugyanahhoz az agenthez mindig ugyanaz az ikon jelenik meg.
    Ha valódi fotókat szeretnél, ezt a függvényt később könnyen lecserélheted
    saját képfájlokra vagy saját URL-ekre.
    """
    seed = quote(str(agent_name))
    return f"https://api.dicebear.com/8.x/personas/svg?seed={seed}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf"


def render_agent_photos(agent_names):
    """Agent fotó/ikon sáv megjelenítése a dashboard felső részén.

    A korábbi verzióban bizonyos Streamlit környezetben a HTML-kód
    szövegként jelent meg. Ezért itt components.html-t használunk,
    ami biztosan HTML-ként rendereli az agent kártyákat.
    """
    cards = []
    for agent in agent_names:
        safe_agent = escape(str(agent))
        photo_url = get_agent_photo_url(str(agent))
        cards.append(
            f"""
            <div class="agent-card">
                <img src="{photo_url}" alt="{safe_agent}">
                <div class="agent-card-name" title="{safe_agent}">{safe_agent}</div>
            </div>
            """
        )

    cards_html = "".join(cards)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: transparent;
            }}
            .agent-photo-strip {{
                background: linear-gradient(135deg, rgba(30,41,59,0.96), rgba(15,23,42,0.96));
                padding: 18px 20px;
                border-radius: 22px;
                border: 1px solid rgba(148,163,184,0.28);
                box-shadow: 0 18px 42px rgba(0, 0, 0, 0.28);
                margin-bottom: 8px;
            }}
            .agent-photo-title {{
                font-size: 15px;
                color: #cbd5e1;
                font-weight: 700;
                margin-bottom: 12px;
            }}
            .agent-photo-grid {{
                display: flex;
                gap: 16px;
                flex-wrap: wrap;
                align-items: center;
            }}
            .agent-card {{
                width: 116px;
                text-align: center;
                padding: 10px 8px;
                border-radius: 16px;
                background: linear-gradient(180deg, #1e293b, #0f172a);
                border: 1px solid rgba(125, 211, 252, 0.28);
                box-sizing: border-box;
            }}
            .agent-card img {{
                width: 72px;
                height: 72px;
                border-radius: 50%;
                object-fit: cover;
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.16);
                background: #e2e8f0;
            }}
            .agent-card-name {{
                margin-top: 8px;
                font-size: 13px;
                color: #f8fafc;
                font-weight: 700;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
        </style>
    </head>
    <body>
        <div class="agent-photo-strip">
            <div class="agent-photo-title">Agent fotók / ikonok</div>
            <div class="agent-photo-grid">
                {cards_html}
            </div>
        </div>
    </body>
    </html>
    """

    # Dinamikus magasság: 1 sor kb. 150 px, több sor esetén növeljük.
    row_count = max(1, (len(agent_names) + 5) // 6)
    height = 155 + (row_count - 1) * 135
    components.html(html, height=height, scrolling=False)

# ------------------------------------------------------------
# Adatbetöltés
# ------------------------------------------------------------
DEFAULT_FILE = "callcenter_gzs01.xlsx"
excel_path = Path(DEFAULT_FILE)

if not excel_path.exists():
    uploaded_file = st.sidebar.file_uploader(
        "Excel fájl feltöltése", type=["xlsx", "xls"]
    )
    if uploaded_file is None:
        st.info(
            "Tedd a callcenter_gzs01.xlsx fájlt az app.py mellé, vagy töltsd fel itt az oldalsávban."
        )
        st.stop()
    df1 = load_data(uploaded_file)
else:
    df1 = load_data(str(excel_path))

# ------------------------------------------------------------
# Oldalsáv - widgetek
# ------------------------------------------------------------
st.sidebar.title("Szűrők")
st.sidebar.caption("A bal oldali panel vezérli a teljes dashboardot.")

agents = sorted(df1["Agent"].dropna().unique())
selected_agents = st.sidebar.multiselect("Agent", agents, default=agents)

topics = sorted(df1["Topic"].dropna().unique())
selected_topics = st.sidebar.multiselect("Topic", topics, default=topics)

min_date = df1["Date"].min().date()
max_date = df1["Date"].max().date()

st.sidebar.markdown("**Dátumtartomány**")
start_date = st.sidebar.date_input(
    "Kezdő nap",
    value=min_date,
    min_value=min_date,
    max_value=max_date,
)
end_date = st.sidebar.date_input(
    "Utolsó nap",
    value=max_date,
    min_value=min_date,
    max_value=max_date,
)

if start_date > end_date:
    st.sidebar.error("A kezdő nap nem lehet későbbi, mint az utolsó nap.")

time_grain = st.sidebar.radio(
    "Dátum bontás",
    ["Nap", "Hét", "Hónap"],
    horizontal=False,
)

weekday_order = ["Hétfő", "Kedd", "Szerda", "Csütörtök", "Péntek", "Szombat", "Vasárnap"]
available_weekdays = [day for day in weekday_order if day in df1["NaptariNap"].dropna().unique()]
selected_weekdays = st.sidebar.multiselect(
    "Naptári napok",
    available_weekdays,
    default=available_weekdays,
    help="Itt konkrét hétköznapokra tudsz szűrni, például csak Hétfőre vagy csak Keddre.",
)

duration_slots = ["0-1 perc", "1-3 perc", "3-5 perc", "5+ perc"]
selected_duration_slots = st.sidebar.multiselect(
    "Beszélgetési hossz",
    duration_slots,
    default=duration_slots,
)

# Elégedettség szűrő Satisfaction rating alapján.
satisfaction_values = df1["Satisfaction rating"].dropna()
if satisfaction_values.empty:
    min_satisfaction = 0.0
    max_satisfaction = 5.0
else:
    min_satisfaction = float(satisfaction_values.min())
    max_satisfaction = float(satisfaction_values.max())

selected_satisfaction_range = st.sidebar.slider(
    "Elégedettség",
    min_value=min_satisfaction,
    max_value=max_satisfaction,
    value=(min_satisfaction, max_satisfaction),
    step=0.5,
    help="Satisfaction rating szerinti szűrés. Például 4 és 5 közötti értékelések.",
)

st.sidebar.divider()
st.sidebar.caption("Opcionális státusz szűrők")
answered_filter = st.sidebar.selectbox("Answered", ["Mind", "Y", "N"])
resolved_filter = st.sidebar.selectbox("Resolved", ["Mind", "Y", "N"])

# ------------------------------------------------------------
# Szűrés
# ------------------------------------------------------------
filtered_df = df1.copy()

filtered_df = filtered_df[filtered_df["Agent"].isin(selected_agents)]
filtered_df = filtered_df[filtered_df["Topic"].isin(selected_topics)]
filtered_df = filtered_df[
    filtered_df["TalkDurationSlot"].astype(str).isin(selected_duration_slots)
]

satisfaction_min, satisfaction_max = selected_satisfaction_range
filtered_df = filtered_df[
    filtered_df["Satisfaction rating"].between(satisfaction_min, satisfaction_max, inclusive="both")
]

if start_date <= end_date:
    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date)
        & (filtered_df["Date"].dt.date <= end_date)
    ]
else:
    filtered_df = filtered_df.iloc[0:0]

filtered_df = filtered_df[filtered_df["NaptariNap"].isin(selected_weekdays)]

if answered_filter != "Mind":
    filtered_df = filtered_df[filtered_df["Answered (Y/N)"] == answered_filter]

if resolved_filter != "Mind":
    filtered_df = filtered_df[filtered_df["Resolved"] == resolved_filter]

# ------------------------------------------------------------
# Fejlkezelés üres szűrés esetén
# ------------------------------------------------------------
if filtered_df.empty:
    st.warning("A kiválasztott szűrőkkel nincs megjeleníthető adat.")
    st.stop()

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.markdown(
    '''
    <div class="dashboard-hero">
        <div class="dashboard-title">Call Center dashboard</div>
        <div class="dashboard-subtitle">Hívásminőség, válaszidő, elégedettség és megoldási ráta áttekintése</div>
    </div>
    ''',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Felső agent fotó/ikon sáv
# ------------------------------------------------------------
# Fontos: a sáv a bal oldali Agent szűrő alapján változik.
# Ha minden agent ki van választva, minden ikon látszik.
# Ha egy agentre szűrsz, csak az adott agent ikonja marad meg.
visible_agents = sorted(filtered_df["Agent"].dropna().unique())
render_agent_photos(visible_agents)

# ------------------------------------------------------------
# KPI sor
# ------------------------------------------------------------
avg_talk_seconds = filtered_df["TalkDurationSeconds"].mean()
avg_satisfaction = filtered_df["Satisfaction rating"].mean()
avg_speed = filtered_df["Speed of answer in seconds"].mean()
resolved_rate = yes_rate(filtered_df["Resolved"])
answered_rate = yes_rate(filtered_df["Answered (Y/N)"])

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    render_kpi(
        "Átlagos beszélgetési idő",
        format_seconds_to_mmss(avg_talk_seconds),
        "AvgTalkDuration alapján, perc:másodperc",
    )
with kpi2:
    render_kpi(
        "Átlagos elégedettség",
        f"{avg_satisfaction:.2f} / 5",
        "Satisfaction rating átlaga",
    )
with kpi3:
    render_kpi(
        "Átlagos válaszidő",
        f"{avg_speed:.1f} mp",
        "Speed of answer in seconds átlaga",
    )
with kpi4:
    render_kpi(
        "Megoldási ráta",
        f"{resolved_rate:.1f}%",
        "Resolved = Y aránya",
    )

st.write("")

# ------------------------------------------------------------
# Fő grafikonok
# ------------------------------------------------------------
left_chart, right_chart = st.columns([1.25, 1])

with left_chart:
    st.markdown('<h3 class="section-title">Hívások száma időben</h3>', unsafe_allow_html=True)
    period_col = {"Nap": "Nap", "Hét": "Het", "Hónap": "Honap"}[time_grain]
    time_df = (
        filtered_df.groupby(period_col, observed=True)
        .agg(Hivasok=("Call Id", "count"))
        .reset_index()
        .rename(columns={period_col: "Időszak"})
    )
    fig_time = px.line(
        time_df,
        x="Időszak",
        y="Hivasok",
        markers=True,
        title=None,
    )
    fig_time.update_layout(
        height=360,
        template="plotly_dark",
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis_title="Hívások száma",
        xaxis_title="",
        plot_bgcolor="rgba(15,23,42,0)",
        paper_bgcolor="rgba(15,23,42,0)",
        font=dict(color="#cbd5e1"),
    )
    fig_time.update_traces(line=dict(width=4, color=COLOR_PRIMARY), marker=dict(size=8, color=COLOR_SECONDARY, line=dict(width=1, color="#0f172a")))
    st.plotly_chart(fig_time, use_container_width=True)

with right_chart:
    st.markdown('<h3 class="section-title">Topic szerinti eloszlás</h3>', unsafe_allow_html=True)

    # Topic szintű összesítés: hívásszám + átlagos ügyfélelégedettség.
    # Az elégedettségi érték nem külön táblázatban jelenik meg,
    # hanem közvetlenül a sávdiagramon, a sávok végétől jobbra eltolva.
    topic_df = (
        filtered_df.groupby("Topic", observed=True)
        .agg(
            Hivasok=("Call Id", "count"),
            Atlagos_elegedettseg=("Satisfaction rating", "mean"),
        )
        .reset_index()
        .sort_values("Hivasok", ascending=True)
    )
    topic_df["ElegedettsegFelirat"] = topic_df["Atlagos_elegedettseg"].apply(
        lambda x: "Elégedettség: -" if pd.isna(x) else f"Elégedettség: {x:.2f} / 5"
    )

    max_hivas = topic_df["Hivasok"].max() if not topic_df.empty else 1
    x_range_max = max_hivas * 1.38

    fig_topic = px.bar(
        topic_df,
        x="Hivasok",
        y="Topic",
        orientation="h",
        text="ElegedettsegFelirat",
        title=None,
        hover_data={
            "Hivasok": True,
            "Atlagos_elegedettseg": ":.2f",
            "ElegedettsegFelirat": False,
        },
    )
    fig_topic.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
    )
    fig_topic.update_layout(
        height=360,
        template="plotly_dark",
        margin=dict(l=10, r=120, t=20, b=10),
        xaxis_title="Hívások száma",
        yaxis_title="",
        xaxis=dict(range=[0, x_range_max]),
        plot_bgcolor="rgba(15,23,42,0)",
        paper_bgcolor="rgba(15,23,42,0)",
        font=dict(color="#cbd5e1"),
    )
    fig_topic.update_traces(marker_color=COLOR_SECONDARY, marker_line_color="rgba(248,250,252,0.85)", marker_line_width=1.5)
    st.plotly_chart(fig_topic, use_container_width=True)

# ------------------------------------------------------------
# Második elemző sor
# ------------------------------------------------------------
agent_col, scatter_col = st.columns([1.05, 1])

with agent_col:
    st.markdown('<h3 class="section-title">Agent teljesítmény</h3>', unsafe_allow_html=True)
    agent_df = (
        filtered_df.groupby("Agent", observed=True)
        .agg(
            Hivasok=("Call Id", "count"),
            Atlagos_elegedettseg=("Satisfaction rating", "mean"),
            Atlagos_valaszido=("Speed of answer in seconds", "mean"),
            Atlagos_beszedido_mp=("TalkDurationSeconds", "mean"),
            Megoldasi_rata=("Resolved", yes_rate),
        )
        .reset_index()
        .sort_values("Megoldasi_rata", ascending=False)
    )
    fig_agent = px.bar(
        agent_df,
        x="Agent",
        y="Megoldasi_rata",
        text=agent_df["Megoldasi_rata"].round(1).astype(str) + "%",
        title=None,
    )
    fig_agent.update_layout(
        height=340,
        template="plotly_dark",
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis_title="Megoldási ráta (%)",
        xaxis_title="",
        plot_bgcolor="rgba(15,23,42,0)",
        paper_bgcolor="rgba(15,23,42,0)",
        font=dict(color="#cbd5e1"),
    )
    fig_agent.update_traces(marker_color=COLOR_PRIMARY, marker_line_color="rgba(248,250,252,0.85)", marker_line_width=1.5)
    st.plotly_chart(fig_agent, use_container_width=True)

with scatter_col:
    st.markdown('<h3 class="section-title">Válaszidő és elégedettség kapcsolata</h3>', unsafe_allow_html=True)
    scatter_df = (
        filtered_df.groupby("Agent", observed=True)
        .agg(
            Atlagos_valaszido=("Speed of answer in seconds", "mean"),
            Atlagos_elegedettseg=("Satisfaction rating", "mean"),
            Hivasok=("Call Id", "count"),
            Megoldasi_rata=("Resolved", yes_rate),
        )
        .reset_index()
    )
    fig_scatter = px.scatter(
        scatter_df,
        x="Atlagos_valaszido",
        y="Atlagos_elegedettseg",
        size="Hivasok",
        hover_name="Agent",
        title=None,
    )
    fig_scatter.update_layout(
        height=340,
        template="plotly_dark",
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_title="Átlagos válaszidő (mp)",
        yaxis_title="Átlagos elégedettség",
        plot_bgcolor="rgba(15,23,42,0)",
        paper_bgcolor="rgba(15,23,42,0)",
        font=dict(color="#cbd5e1"),
    )
    fig_scatter.update_traces(marker=dict(line=dict(width=1, color="#e5e7eb"), opacity=0.88))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------------------------
# Alsó rész - táblázatok
# ------------------------------------------------------------
st.markdown('<h2 class="section-title">Táblázatok</h2>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Agent összesítő", "Topic összesítő", "Részletes híváslista"])

with tab1:
    table_agent = agent_df.copy()
    table_agent["Atlagos_elegedettseg"] = table_agent["Atlagos_elegedettseg"].round(2)
    table_agent["Atlagos_valaszido"] = table_agent["Atlagos_valaszido"].round(1)
    table_agent["Atlagos_beszedido_mp"] = table_agent["Atlagos_beszedido_mp"].round(1)
    table_agent["Megoldasi_rata"] = table_agent["Megoldasi_rata"].round(1)
    st.dataframe(table_agent, use_container_width=True, hide_index=True)

with tab2:
    table_topic = (
        filtered_df.groupby("Topic", observed=True)
        .agg(
            Hivasok=("Call Id", "count"),
            Atlagos_elegedettseg=("Satisfaction rating", "mean"),
            Atlagos_valaszido=("Speed of answer in seconds", "mean"),
            Atlagos_beszedido_mp=("TalkDurationSeconds", "mean"),
            Megoldasi_rata=("Resolved", yes_rate),
        )
        .reset_index()
        .sort_values("Hivasok", ascending=False)
    )
    for col in ["Atlagos_elegedettseg", "Atlagos_valaszido", "Atlagos_beszedido_mp", "Megoldasi_rata"]:
        table_topic[col] = table_topic[col].round(1)
    st.dataframe(table_topic, use_container_width=True, hide_index=True)

with tab3:
    detail_cols = [
        "Call Id",
        "Agent",
        "Date",
        "Time",
        "Topic",
        "Answered (Y/N)",
        "Resolved",
        "Speed of answer in seconds",
        "AvgTalkDuration",
        "Satisfaction rating",
    ]
    st.dataframe(
        filtered_df[detail_cols].sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
