
import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# NETFLIX CONTENT STRATEGY DASHBOARD
# Streamlit single-file app
# File name: appcsv04.py
# ============================================================

st.set_page_config(
    page_title="Netflix Content Strategy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CSS ----------
st.markdown("""
<style>
.stApp{
    background:linear-gradient(180deg,#232730 0%,#1b1f27 45%,#15181e 100%);
    color:#FAFAFA;
}
.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}
h1,h2,h3{
    color:#FFFFFF !important;
}
p,label,span,div{
    color:#EAEAEA;
}
section[data-testid="stSidebar"]{
    background:#20252E;
    border-right:1px solid #424754;
}
div[data-testid="stMetric"]{
    background:#2B313C;
    border:1px solid #515866;
    border-left:6px solid #E50914;
    border-radius:14px;
    padding:12px;
    box-shadow:0 8px 18px rgba(0,0,0,.25);
}
div[data-testid="stMetricValue"]{
    color:#FFFFFF;
    font-size:34px;
    font-weight:800;
}
div[data-testid="stMetricLabel"]{
    color:#D9DDE4;
    font-weight:700;
}
div[data-baseweb="select"] *{
    color:#000000 !important;
}
div[data-baseweb="select"] input{
    color:#000000 !important;
}
.stDataFrame{
    background:#2B313C;
}
hr{
    border:none;
    height:2px;
    background:linear-gradient(90deg,#E50914,#D6B56D);
}
.hero-card{
    background:linear-gradient(90deg,rgba(80,20,24,.92),rgba(43,49,60,.95));
    border:1px solid #59343A;
    border-radius:16px;
    padding:22px 24px;
    margin-bottom:16px;
    box-shadow:0 10px 22px rgba(0,0,0,.28);
}
.hero-title{
    color:#FF3340;
    font-size:16px;
    font-weight:900;
    letter-spacing:.5px;
    margin-bottom:10px;
}
.hero-text{
    color:#FFFFFF;
    font-size:18px;
    line-height:1.45;
}
.kpi-panel{
    background:#2B313C;
    border:1px solid #515866;
    border-radius:16px;
    padding:16px;
    text-align:center;
    box-shadow:0 8px 18px rgba(0,0,0,.25);
}
.kpi-icon{
    font-size:30px;
    color:#D6B56D;
}
.kpi-value-red{
    font-size:34px;
    color:#E50914;
    font-weight:900;
}
.kpi-value-gold{
    font-size:34px;
    color:#D6B56D;
    font-weight:900;
}
.kpi-label{
    color:#F0F0F0;
    font-size:14px;
}
.sidebar-card{
    background:#242A35;
    border:1px solid #424754;
    border-radius:14px;
    padding:14px;
    margin-top:14px;
}
.small-muted{
    color:#C9CED7;
    font-size:13px;
}
</style>
""", unsafe_allow_html=True)


# ---------- DATA ----------
@st.cache_data
def load_data(path="netflix.xlsx"):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower()

    df = df[df["type"].isin(["Movie", "TV Show"])].copy()

    # Basic cleaning
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    df["added_year"] = df["date_added"].dt.year
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
    df["country"] = df["country"].fillna("Unknown")
    df["listed_in"] = df["listed_in"].fillna("Unknown")
    df["rating"] = df["rating"].fillna("Unrated").astype(str).str.strip()
    df["duration"] = df["duration"].fillna("Unknown").astype(str)

    # Fix rows where duration accidentally appears in rating
    duration_in_rating = df["rating"].str.contains(r"\bmin\b", case=False, na=False)
    df.loc[duration_in_rating, "duration"] = df.loc[duration_in_rating, "rating"]
    df.loc[duration_in_rating, "rating"] = "Unrated"

    valid_ratings = [
        "G", "PG", "PG-13", "R", "NC-17",
        "TV-Y", "TV-Y7", "TV-Y7-FV", "TV-G",
        "TV-PG", "TV-14", "TV-MA",
        "NR", "UR", "Unrated"
    ]
    df = df[df["rating"].isin(valid_ratings)].copy()

    df["duration_minutes"] = pd.to_numeric(
        df["duration"].str.extract(r"(\d+)")[0],
        errors="coerce"
    )
    df.loc[df["type"] != "Movie", "duration_minutes"] = pd.NA

    df["season_count"] = pd.to_numeric(
        df["duration"].str.extract(r"(\d+)")[0],
        errors="coerce"
    )
    df.loc[df["type"] != "TV Show", "season_count"] = pd.NA

    df["primary_country"] = df["country"].str.split(",").str[0].str.strip()
    df["primary_genre"] = df["listed_in"].str.split(",").str[0].str.strip()

    return df


def maturity_group(rating):
    rating = str(rating).strip()
    if rating in ["TV-MA", "R", "NC-17"]:
        return "Felnőtt"
    if rating in ["TV-14", "PG-13"]:
        return "Teen"
    if rating in ["TV-Y", "TV-Y7", "TV-Y7-FV", "TV-G", "G", "PG"]:
        return "Családi / gyerek"
    return "Besorolatlan"


df = load_data()


# ---------- SIDEBAR FILTERS ----------
st.sidebar.markdown("## SZŰRŐK")

types_all = sorted(df["type"].dropna().unique())
type_filter = st.sidebar.selectbox("Tartalom típusa", ["Minden"] + types_all, key="type_filter")

years = df["added_year"].dropna()
year_min, year_max = int(years.min()), int(years.max())
year_filter = st.sidebar.slider(
    "Megjelenés / hozzáadás éve",
    year_min,
    year_max,
    (year_min, year_max),
    key="year_filter"
)

countries = sorted(df["country"].str.split(",").explode().str.strip().dropna().unique())
country_filter = st.sidebar.selectbox("Ország", ["Minden ország"] + countries, key="country_filter")

genres = sorted(df["listed_in"].str.split(",").explode().str.strip().dropna().unique())
genre_filter = st.sidebar.selectbox("Műfaj", ["Minden műfaj"] + genres, key="genre_filter")

movie_minutes = df["duration_minutes"].dropna()
if len(movie_minutes):
    dur_min, dur_max = int(movie_minutes.min()), int(movie_minutes.max())
else:
    dur_min, dur_max = 0, 300

duration_filter = st.sidebar.slider(
    "Időtartam filmeknél (perc)",
    dur_min,
    dur_max,
    (dur_min, dur_max),
    key="duration_filter"
)

st.sidebar.markdown("### Korhatár-besorolás")
st.sidebar.caption("A kiválasztás a teljes dashboardra hat.")

ratings_order = ["TV-MA", "TV-14", "PG-13", "TV-PG", "PG", "TV-Y7", "TV-Y", "G", "R", "NC-17", "NR", "UR", "Unrated"]
available_ratings = [r for r in ratings_order if r in df["rating"].unique()]
available_ratings += [r for r in sorted(df["rating"].unique()) if r not in available_ratings]


def sync_rating_all():
    for rating_item in available_ratings:
        st.session_state[f"rating_{rating_item}"] = st.session_state["rating_all"]


if "rating_all" not in st.session_state:
    st.session_state["rating_all"] = True
for rating_item in available_ratings:
    if f"rating_{rating_item}" not in st.session_state:
        st.session_state[f"rating_{rating_item}"] = True

st.sidebar.checkbox("Összes kijelölése", key="rating_all", on_change=sync_rating_all)

rating_counts = df["rating"].value_counts()
selected_ratings = []

for rating_item in available_ratings:
    count = int(rating_counts.get(rating_item, 0))
    if st.sidebar.checkbox(f"{rating_item}  —  {count:,}", key=f"rating_{rating_item}"):
        selected_ratings.append(rating_item)

search = st.sidebar.text_input("Cím keresése", key="search_filter")

if st.sidebar.button("🔄 Szűrők törlése", use_container_width=True):
    for key in list(st.session_state.keys()):
        if key.startswith("rating_") or key in [
            "type_filter", "year_filter", "country_filter",
            "genre_filter", "duration_filter", "search_filter"
        ]:
            del st.session_state[key]
    st.rerun()


# ---------- FILTER DATA ----------
f = df.copy()

if type_filter != "Minden":
    f = f[f["type"] == type_filter]

f = f[(f["added_year"].fillna(0) >= year_filter[0]) & (f["added_year"].fillna(0) <= year_filter[1])]

if country_filter != "Minden ország":
    f = f[f["country"].str.contains(country_filter, case=False, na=False)]

if genre_filter != "Minden műfaj":
    f = f[f["listed_in"].str.contains(genre_filter, case=False, na=False)]

if selected_ratings:
    f = f[f["rating"].isin(selected_ratings)]
else:
    f = f.iloc[0:0]

# Duration filter affects only movies. TV Shows remain visible.
movie_mask = f["type"].eq("Movie")
tv_mask = f["type"].eq("TV Show")
f = f[
    tv_mask |
    (
        movie_mask &
        (f["duration_minutes"].fillna(-1) >= duration_filter[0]) &
        (f["duration_minutes"].fillna(-1) <= duration_filter[1])
    )
]

if search:
    f = f[f["title"].str.contains(search, case=False, na=False)]


# ---------- METRICS ----------
total_titles = len(f)
movies = int((f["type"] == "Movie").sum())
tv_shows = int((f["type"] == "TV Show").sum())
movie_share = movies / total_titles * 100 if total_titles else 0
countries_count = f["country"].str.split(",").explode().str.strip().nunique() if total_titles else 0

active_year = "-"
if total_titles and f["added_year"].notna().any():
    active_year = int(f["added_year"].value_counts().idxmax())

# Story values
if total_titles:
    dominant_type = f["type"].value_counts().idxmax()
    dominant_rating = f["rating"].value_counts().idxmax()
    dominant_genre = f["listed_in"].str.split(",").explode().str.strip().value_counts().idxmax()
else:
    dominant_type = "-"
    dominant_rating = "-"
    dominant_genre = "-"


# ---------- HEADER ----------
top_left, top_right = st.columns((3, 1))
with top_left:
    st.title("Netflix Content Strategy Dashboard")
with top_right:
    st.caption("Adatok frissítve: 2021. december 31.")

st.markdown("<hr>", unsafe_allow_html=True)

hero, k1, k2, k3, k4 = st.columns((2.7, 1, 1, 1, 1))

with hero:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">KIEMELT INSIGHT</div>
            <div class="hero-text">
                A Netflix katalógusa a kiválasztott szűrésben <b>{total_titles:,}</b> tartalmat mutat.
                A filmek aránya <b>{movie_share:.1f}%</b>, a domináns műfaji irány pedig
                <b>{dominant_genre}</b>. A legerősebb korhatár-besorolás jelenleg:
                <b>{dominant_rating}</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k1:
    st.markdown(f'<div class="kpi-panel"><div class="kpi-icon">🎬</div><div class="kpi-value-red">{movie_share:.1f}%</div><div class="kpi-label">Filmek aránya</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-panel"><div class="kpi-icon">🌍</div><div class="kpi-value-gold">{countries_count:,}</div><div class="kpi-label">Egyedülálló ország</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-panel"><div class="kpi-icon">📅</div><div class="kpi-value-gold">{active_year}</div><div class="kpi-label">Legaktívabb év</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-panel"><div class="kpi-icon">▶</div><div class="kpi-value-red">{total_titles:,}</div><div class="kpi-label">Összes tartalom</div></div>', unsafe_allow_html=True)


# ---------- ROW 1 ----------
left, right = st.columns((1.7, 1.2))

with left:
    yearly = f.groupby("added_year").size().reset_index(name="Tartalmak száma").dropna()
    fig = px.area(
        yearly,
        x="added_year",
        y="Tartalmak száma",
        title="Katalógus növekedése évek szerint<br><sup>A tartalmak számának alakulása hozzáadási év szerint</sup>",
        color_discrete_sequence=["#D6B56D"]
    )
    fig.update_traces(line=dict(color="#D6B56D", width=3), fillcolor="rgba(214,181,109,.35)")
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=410,
        xaxis_title="",
        yaxis_title="Tartalmak száma"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    mix = f.groupby("type").size().reset_index(name="Count")
    fig = px.pie(
        mix,
        values="Count",
        names="type",
        hole=.62,
        color="type",
        color_discrete_map={"Movie": "#E50914", "TV Show": "#D6B56D"},
        title="Tartalom típusa szerinti megoszlás<br><sup>Filmek és TV-műsorok aránya</sup>"
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=410
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------- ROW 2 ----------
rp_col, country_col, genre_col = st.columns((1.25, 1.05, 1.05))

with rp_col:
    st.markdown("### Korhatár-profil")
    st.caption("Milyen célközönségre épül a kiválasztott katalógus?")

    rating_profile = f["rating"].fillna("Unrated").astype(str).str.strip().value_counts().reset_index()
    rating_profile.columns = ["Rating", "Titles"]

    if len(rating_profile):
        rating_profile["Share"] = rating_profile["Titles"] / rating_profile["Titles"].sum()
        rating_profile["Csoport"] = rating_profile["Rating"].apply(maturity_group)
        rating_profile["Label"] = rating_profile.apply(lambda x: f"{x['Titles']:,} ({x['Share']:.1%})", axis=1)

        color_map = {
            "Felnőtt": "#E50914",
            "Teen": "#D6B56D",
            "Családi / gyerek": "#64B96A",
            "Besorolatlan": "#8A8F98"
        }

        fig = px.bar(
            rating_profile.sort_values("Titles", ascending=True),
            x="Titles",
            y="Rating",
            orientation="h",
            color="Csoport",
            color_discrete_map=color_map,
            text="Label"
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            height=390,
            margin=dict(l=15, r=70, t=25, b=35),
            xaxis_title="Tartalmak száma",
            yaxis_title="",
            legend_title_text="Korhatár-csoport"
        )
        st.plotly_chart(fig, use_container_width=True)

        dominant_rating = rating_profile.iloc[0]["Rating"]
        dominant_share = rating_profile.iloc[0]["Share"]
        top_group = rating_profile.groupby("Csoport")["Titles"].sum().sort_values(ascending=False).index[0]
        st.info(
            f"**Domináns korhatár:** {dominant_rating} · "
            f"A kiválasztott katalógus {dominant_share:.1%}-a. "
            f"A legerősebb célközönség-csoport: **{top_group}**."
        )
    else:
        st.warning("Nincs megjeleníthető korhatár-adat.")

with country_col:
    cc = f["country"].str.split(",").explode().str.strip().value_counts().head(10).reset_index()
    cc.columns = ["Country", "Titles"]
    fig = px.bar(
        cc,
        x="Titles",
        y="Country",
        orientation="h",
        color_discrete_sequence=["#E50914"],
        title="Top 10 ország<br><sup>Tartalmak száma alapján</sup>"
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=450,
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Tartalmak száma",
        yaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)

with genre_col:
    gg = f["listed_in"].str.split(",").explode().str.strip().value_counts().head(10).reset_index()
    gg.columns = ["Genre", "Titles"]
    fig = px.bar(
        gg,
        x="Titles",
        y="Genre",
        orientation="h",
        color_discrete_sequence=["#D6B56D"],
        title="Top 10 műfaj<br><sup>Tartalmak száma alapján</sup>"
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        height=450,
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Tartalmak száma",
        yaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------- TITLE EXPLORER ----------
st.subheader("Címek böngészése")
st.caption("A fenti elemzések minden esetben visszavezethetők az eredeti Netflix rekordokra.")

cols = ["title", "type", "country", "listed_in", "release_year", "rating", "duration"]
st.dataframe(
    f[cols].rename(
        columns={
            "title": "Cím",
            "type": "Típus",
            "country": "Ország",
            "listed_in": "Műfaj",
            "release_year": "Megjelenési év",
            "rating": "Korhatár",
            "duration": "Időtartam"
        }
    ),
    use_container_width=True,
    height=320
)

# ---------- SIDEBAR FOOTER ----------
st.sidebar.markdown(
    f"""
    <div class="sidebar-card">
        <div class="small-muted">Adatforrás</div>
        <b>Netflix Titles Dataset</b><br><br>
        <div class="small-muted">Katalógus mérete szűrve</div>
        <div style="font-size:30px;font-weight:900;color:white;">{total_titles:,}</div>
        <div class="small-muted">tartalom</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
st.info("A dashboard interaktív: használd a bal oldali szűrőket az országok, műfajok, időszakok és korhatár-profilok felfedezéséhez.")
