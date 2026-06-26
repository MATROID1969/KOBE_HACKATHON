"""
Streamlit dashboard a salaries.xlsx adataihoz

Futtatás:
1) Tedd ezt a fájlt ugyanabba a mappába, mint a salaries.xlsx fájlt.
2) Telepítés: pip install streamlit pandas plotly openpyxl numpy
3) Indítás: streamlit run salaries_dashboard_app.py

A dashboard tartalma:
- Executive KPI-k
- Oldalsáv szűrők
- Fizetés trend, eloszlás, top munkakörök, országok, térkép
- Company size / employment type megoszlások
- Experience vs salary, heatmap, treemap, scatter
- Hackathon bónuszok: Salary Score, What-if emelés, Top N, feltételes színezés,
  gazdag tooltip/pontadatok, több nézetes navigáció
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Salary Intelligence Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)




REQUIRED_COLUMNS = {
    "Job Title",
    "Employment Type",
    "Experience Level",
    "Expertise Level",
    "Salary",
    "Salary Currency",
    "Company Location",
    "Salary in USD",
    "Employee Residence",
    "Company Size",
    "Year",
}

EXPERIENCE_ORDER = ["Entry", "Mid", "Senior", "Executive"]
COMPANY_SIZE_ORDER = ["Small", "Medium", "Large"]


# KÖBE arculati hangulat: zöld dominancia, piros akcentus, fehér felületek
KOBE_GREEN = "#2f8f2f"
KOBE_DARK_GREEN = "#176b34"
KOBE_LIGHT_GREEN = "#eaf6e8"
KOBE_RED = "#ef3b2d"
KOBE_DARK_TEXT = "#233323"

px.defaults.color_discrete_sequence = [
    KOBE_GREEN,
    KOBE_RED,
    "#63b35d",
    "#0f6b3d",
    "#f36c5d",
    "#8fcf86",
]
px.defaults.template = "plotly_white"

st.markdown(f"""
<style>
:root {{
    --kobe-green: {KOBE_GREEN};
    --kobe-dark-green: {KOBE_DARK_GREEN};
    --kobe-light-green: {KOBE_LIGHT_GREEN};
    --kobe-red: {KOBE_RED};
    --kobe-text: {KOBE_DARK_TEXT};
}}

.stApp {{
    background:
        radial-gradient(circle at top right, rgba(239, 59, 45, 0.10), transparent 28%),
        linear-gradient(135deg, #ffffff 0%, var(--kobe-light-green) 45%, #d7efd2 100%);
    color: var(--kobe-text);
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--kobe-dark-green) 0%, var(--kobe-green) 100%);
    border-right: 5px solid var(--kobe-red);
}}

section[data-testid="stSidebar"] * {{
    color: white !important;
}}

h1, h2, h3 {{
    color: var(--kobe-dark-green);
}}

div[data-testid="stMetric"] {{
    background: rgba(255, 255, 255, 0.96);
    border-left: 7px solid var(--kobe-green);
    border-top: 2px solid rgba(239, 59, 45, 0.45);
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 4px 18px rgba(23, 107, 52, 0.12);
}}

div[data-testid="stMetricLabel"] p {{
    color: var(--kobe-dark-green) !important;
    font-weight: 700;
}}

div[data-testid="stMetricValue"] {{
    color: var(--kobe-dark-green);
}}

.stButton > button,
.stDownloadButton > button {{
    background-color: var(--kobe-red);
    color: white;
    border: 0;
    border-radius: 8px;
    font-weight: 700;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    background-color: var(--kobe-dark-green);
    color: white;
    border: 0;
}}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {{
    border-color: var(--kobe-green);
}}

[data-testid="stCaptionContainer"] {{
    color: var(--kobe-dark-green);
}}
</style>
""", unsafe_allow_html=True)



@st.cache_data(show_spinner=False)
def load_data(uploaded_file=None) -> pd.DataFrame:
    """Betölti és előkészíti az adatokat."""
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
    else:
        default_path = Path(__file__).with_name("salaries.xlsx")
        if not default_path.exists():
            default_path = Path("salaries.xlsx")
        df = pd.read_excel(default_path)

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Hiányzó oszlopok: {', '.join(sorted(missing))}")

    df = df.copy()
    df["Salary in USD"] = pd.to_numeric(df["Salary in USD"], errors="coerce")
    df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["Salary in USD", "Year"])

    job_avg = df.groupby("Job Title")["Salary in USD"].transform("mean")
    df["Salary Score"] = df["Salary in USD"] / job_avg
    df["Market Position"] = np.select(
        [df["Salary Score"] >= 1.15, df["Salary Score"] <= 0.85],
        ["Above Market", "Below Market"],
        default="Average",
    )

    return df


def multi_filter(label: str, values, default_all=True):
    options = sorted(pd.Series(values).dropna().unique().tolist())
    return st.sidebar.multiselect(label, options, default=options if default_all else [])


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("🔎 Szűrők")
    year_range = st.sidebar.slider(
        "Év",
        int(df["Year"].min()),
        int(df["Year"].max()),
        (int(df["Year"].min()), int(df["Year"].max())),
    )
    selected_locations = multi_filter("Company Location", df["Company Location"])
    selected_residences = multi_filter("Employee Residence", df["Employee Residence"])
    selected_company_sizes = multi_filter("Company Size", df["Company Size"])
    selected_employment = multi_filter("Employment Type", df["Employment Type"])
    selected_experience = multi_filter("Experience Level", df["Experience Level"])
    selected_expertise = multi_filter("Expertise Level", df["Expertise Level"])

    top_job_options = sorted(df["Job Title"].dropna().unique().tolist())


    selected_jobs = st.sidebar.multiselect(
    "Job Title",
    top_job_options,
    default=top_job_options)

    filtered = df[
        (df["Year"].between(year_range[0], year_range[1]))
        & (df["Company Location"].isin(selected_locations))
        & (df["Employee Residence"].isin(selected_residences))
        & (df["Company Size"].isin(selected_company_sizes))
        & (df["Employment Type"].isin(selected_employment))
        & (df["Experience Level"].isin(selected_experience))
        & (df["Expertise Level"].isin(selected_expertise))
        & (df["Job Title"].isin(selected_jobs))
    ].copy()

    return filtered


def money(value) -> str:
    if pd.isna(value):
        return "—"
    return f"${value:,.0f}"


def kpi_cards(df: pd.DataFrame):
    """Fő KPI mutatók megjelenítése rövid magyarázatokkal."""
    avg_salary = df["Salary in USD"].mean()
    median_salary = df["Salary in USD"].median()
    senior_ratio = (df["Experience Level"].eq("Senior").mean() * 100) if len(df) else np.nan
    most_common_size = df["Company Size"].mode().iloc[0] if not df.empty else "—"
    highest_salary = df["Salary in USD"].max() if not df.empty else np.nan
    most_common_job = df["Job Title"].mode().iloc[0] if not df.empty else "—"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "📊 Rekordok",
        f"{len(df):,}",
        help="A szűrők után megmaradt sorok száma. Ez mutatja, mekkora adatminta alapján készülnek a további elemzések.",
    )
    c1.caption("Elemzett adatsorok száma.")
    c2.metric(
        "📈 Átlagfizetés",
        money(avg_salary),
        help="A szűrt adatokban szereplő fizetések számtani átlaga USD-ben. Érzékeny lehet a nagyon magas vagy nagyon alacsony értékekre.",
    )
    c2.caption("Átlagos bérszint USD-ben.")
    c3.metric(
        "💰 Medián fizetés",
        money(median_salary),
        help="A középső fizetési érték USD-ben: a rekordok fele ez alatt, fele e felett található. Stabilabb képet ad, ha vannak kiugró értékek.",
    )
    c3.caption("Tipikusabb fizetési szint.")
    c4.metric(
        "🌍 Országok",
        f"{df['Company Location'].nunique():,}",
        help="Az egyedi céges lokációk száma a szűrt adatokban. A földrajzi lefedettséget jelzi.",
    )
    c4.caption("Lefedett céges országok.")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric(
        "👨‍💻 Munkakörök",
        f"{df['Job Title'].nunique():,}",
        help="Az egyedi munkakörök száma a szűrt adatokban. Minél magasabb, annál változatosabb a pozíciómix.",
    )
    c5.caption("Egyedi pozíciók száma.")
    c6.metric(
        "⭐ Senior arány",
        "—" if pd.isna(senior_ratio) else f"{senior_ratio:.1f}%",
        help="A Senior tapasztalati szintű rekordok aránya a szűrt mintán belül. Segít megérteni, mennyire tapasztalt a vizsgált csoport.",
    )
    c6.caption("Senior rekordok százaléka.")
    c7.metric(
        "🏭 Leggyakoribb cégméret",
        most_common_size,
        help="A szűrt adatokban leggyakrabban előforduló vállalatméret-kategória. A minta domináns cégtípusát mutatja.",
    )
    c7.caption("Domináns vállalatméret.")
    c8.metric(
        "🏆 Legmagasabb fizetés",
        money(highest_salary),
        help="A szűrt adatokban található legnagyobb Salary in USD érték. Kiugró érték is lehet, ezért érdemes az eloszlással együtt értelmezni.",
    )
    c8.caption("Maximum fizetési érték.")

    st.info(
        "**Hogyan olvasd a KPI-ket?** Az átlagfizetés gyors összképet ad, a medián a tipikusabb bérszintet mutatja, "
        "a rekordok és országok száma pedig azt jelzi, mennyire erős és széles az elemzési minta."
    )
    st.caption(f"Leggyakoribb munkakör: **{most_common_job}** — ez a pozíció fordul elő legtöbbször a jelenlegi szűrés mellett.")

def executive_view(df: pd.DataFrame):
    st.subheader("Executive overview")
    kpi_cards(df)

    if df.empty:
        st.warning("A szűrők alapján nincs megjeleníthető adat.")
        return

    left, right = st.columns((1.1, 1))

    with left:
        yearly = (
            df.groupby("Year", as_index=False)["Salary in USD"]
            .mean()
            .sort_values("Year")
        )
        fig = px.line(
            yearly,
            x="Year",
            y="Salary in USD",
            markers=True,
            title="Átlagfizetés trend évek szerint",
            labels={"Salary in USD": "Átlagfizetés USD", "Year": "Év"},
        )
        fig.update_traces(hovertemplate="Év: %{x}<br>Átlag: $%{y:,.0f}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        size_counts = df["Company Size"].value_counts().reset_index()
        size_counts.columns = ["Company Size", "Count"]
        fig = px.pie(
            size_counts,
            names="Company Size",
            values="Count",
            hole=0.48,
            title="Company Size megoszlás",
        )
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(
            df,
            x="Salary in USD",
            nbins=45,
            title="Fizetések eloszlása",
            labels={"Salary in USD": "Fizetés USD"},
        )
        fig.update_traces(hovertemplate="Fizetési sáv: %{x}<br>Darab: %{y}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        exp_avg = (
            df.groupby("Experience Level", as_index=False)["Salary in USD"]
            .mean()
        )
        exp_avg["Experience Level"] = pd.Categorical(
            exp_avg["Experience Level"], EXPERIENCE_ORDER, ordered=True
        )
        exp_avg = exp_avg.sort_values("Experience Level")
        fig = px.bar(
            exp_avg,
            x="Experience Level",
            y="Salary in USD",
            title="Experience Level vs átlagfizetés",
            labels={"Salary in USD": "Átlagfizetés USD"},
            text_auto=".2s",
        )
        st.plotly_chart(fig, use_container_width=True)


def salary_deep_dive(df: pd.DataFrame):
    st.subheader("Salary analytics")
    if df.empty:
        st.warning("A szűrők alapján nincs megjeleníthető adat.")
        return

    top_n = st.slider("Dinamikus Top N", 5, 30, 10)
    min_records = st.slider("Minimum rekord munkakörönként", 1, 50, 5)

    job_stats = (
        df.groupby("Job Title")
        .agg(avg_salary=("Salary in USD", "mean"), median_salary=("Salary in USD", "median"), count=("Salary in USD", "size"))
        .reset_index()
    )
    job_stats = job_stats[job_stats["count"] >= min_records].sort_values("avg_salary", ascending=False).head(top_n)

    fig = px.bar(
        job_stats.sort_values("avg_salary"),
        x="avg_salary",
        y="Job Title",
        orientation="h",
        title=f"Top {top_n} munkakör átlagfizetés szerint",
        labels={"avg_salary": "Átlagfizetés USD", "Job Title": "Munkakör"},
        hover_data={"median_salary": ":,.0f", "count": True},
        text="avg_salary",
    )
    fig.update_traces(texttemplate="$%{text:,.0f}", hovertemplate="%{y}<br>Átlag: $%{x:,.0f}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(
            df,
            x="Experience Level",
            y="Salary in USD",
            category_orders={"Experience Level": EXPERIENCE_ORDER},
            points="outliers",
            title="Box plot: fizetés tapasztalati szint szerint",
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(
            df,
            x="Salary Score",
            y="Salary in USD",
            size="Salary in USD",
            color="Employment Type",
            hover_name="Job Title",
            hover_data=["Experience Level", "Company Size", "Company Location", "Market Position"],
            title="Salary Score vs fizetés — piaci pozíció elemzés",
        )
        fig.add_vline(x=1.0, line_dash="dash", annotation_text="Piaci átlag")
        st.plotly_chart(fig, use_container_width=True)


def geography_view(df: pd.DataFrame):
    st.subheader("Geographical analytics")
    if df.empty:
        st.warning("A szűrők alapján nincs megjeleníthető adat.")
        return

    country = (
        df.groupby("Company Location")
        .agg(avg_salary=("Salary in USD", "mean"), employees=("Salary in USD", "size"), median_salary=("Salary in USD", "median"))
        .reset_index()
        .sort_values("avg_salary", ascending=False)
    )

    c1, c2 = st.columns((1.1, 1))
    with c1:
        top_countries = country.head(15).sort_values("avg_salary")
        fig = px.bar(
            top_countries,
            x="avg_salary",
            y="Company Location",
            orientation="h",
            title="Top 15 ország átlagfizetés szerint",
            labels={"avg_salary": "Átlagfizetés USD", "Company Location": "Ország"},
            hover_data={"employees": True, "median_salary": ":,.0f"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.choropleth(
            country,
            locations="Company Location",
            locationmode="country names",
            color="avg_salary",
            hover_name="Company Location",
            hover_data={"employees": True, "avg_salary": ":,.0f", "median_salary": ":,.0f"},
            title="Térkép: átlagfizetés országonként",
            labels={"avg_salary": "Átlagfizetés USD"},
        )
        st.plotly_chart(fig, use_container_width=True)


def hr_segments_view(df: pd.DataFrame):
    st.subheader("HR segmentáció")
    if df.empty:
        st.warning("A szűrők alapján nincs megjeleníthető adat.")
        return

    c1, c2 = st.columns(2)
    with c1:
        emp_counts = df["Employment Type"].value_counts().reset_index()
        emp_counts.columns = ["Employment Type", "Count"]
        fig = px.pie(emp_counts, names="Employment Type", values="Count", title="Employment Type megoszlás")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        heat = pd.pivot_table(
            df,
            index="Experience Level",
            columns="Company Size",
            values="Salary in USD",
            aggfunc="mean",
        )
        heat = heat.reindex(index=[x for x in EXPERIENCE_ORDER if x in heat.index])
        heat = heat[[x for x in COMPANY_SIZE_ORDER if x in heat.columns]]
        fig = px.imshow(
            heat,
            text_auto=".2s",
            aspect="auto",
            title="Heatmap: átlagfizetés Experience Level × Company Size",
            labels=dict(x="Company Size", y="Experience Level", color="Átlagfizetés USD"),
        )
        st.plotly_chart(fig, use_container_width=True)

    treemap_df = (
        df.groupby(["Expertise Level", "Job Title"], as_index=False)
        .agg(total_salary=("Salary in USD", "sum"), avg_salary=("Salary in USD", "mean"), count=("Salary in USD", "size"))
    )
    fig = px.treemap(
        treemap_df,
        path=["Expertise Level", "Job Title"],
        values="total_salary",
        color="avg_salary",
        hover_data={"count": True, "avg_salary": ":,.0f", "total_salary": ":,.0f"},
        title="Treemap: munkakörök dominanciája salary volume alapján",
    )
    st.plotly_chart(fig, use_container_width=True)


def bonus_view(df: pd.DataFrame):
    st.subheader("Hackathon bónusz modulok")
    if df.empty:
        st.warning("A szűrők alapján nincs megjeleníthető adat.")
        return

    raise_pct = st.slider("What-if fizetésemelés (%)", -20, 50, 10)
    df = df.copy()
    df["What-if Salary USD"] = df["Salary in USD"] * (1 + raise_pct / 100)

    current_avg = df["Salary in USD"].mean()
    whatif_avg = df["What-if Salary USD"].mean()
    change_avg = whatif_avg - current_avg

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Aktuális átlagfizetés",
        money(current_avg),
        help="A jelenlegi, szűrt adatok alapján számolt átlagfizetés USD-ben, emelés vagy csökkentés nélkül.",
    )
    c1.caption("Kiinduló átlagbér.")
    c2.metric(
        "What-if átlagfizetés",
        money(whatif_avg),
        help="A kiválasztott százalékos fizetésemelés vagy csökkentés után várható átlagfizetés USD-ben.",
    )
    c2.caption("Szimulált átlagbér.")
    c3.metric(
        "Változás",
        money(change_avg),
        help="A What-if átlagfizetés és az aktuális átlagfizetés különbsége. Pozitív érték emelést, negatív érték csökkenést jelent.",
    )
    c3.caption("Átlagos bérhatás.")

    st.info(
        "**What-if értelmezés:** ez a modul azt modellezi, hogyan változna az átlagbér, "
        "ha minden szűrt rekord fizetése a csúszkán megadott százalékkal módosulna."
    )

    whatif = (
        df.groupby("Experience Level", as_index=False)
        .agg(current=("Salary in USD", "mean"), whatif=("What-if Salary USD", "mean"))
    )
    whatif["Experience Level"] = pd.Categorical(whatif["Experience Level"], EXPERIENCE_ORDER, ordered=True)
    whatif = whatif.sort_values("Experience Level")
    fig = go.Figure()
    fig.add_bar(x=whatif["Experience Level"], y=whatif["current"], name="Aktuális")
    fig.add_bar(x=whatif["Experience Level"], y=whatif["whatif"], name="What-if")
    fig.update_layout(title="What-if emelés hatása tapasztalati szintenként", barmode="group", yaxis_title="Átlagfizetés USD")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Salary Score táblázat feltételes színezéssel")
    st.caption(
        "A Salary Score azt mutatja, hogy egy rekord fizetése hogyan viszonyul az adott munkakör átlagához. "
        "1,00 = munkaköri átlag, 1,15 felett Above Market, 0,85 alatt Below Market."
    )
    score_table = df[
        [
            "Job Title",
            "Experience Level",
            "Company Location",
            "Company Size",
            "Salary in USD",
            "Salary Score",
            "Market Position",
        ]
    ].sort_values("Salary Score", ascending=False).head(200)

    st.dataframe(
        score_table.style.format({"Salary in USD": "${:,.0f}", "Salary Score": "{:.2f}"}).background_gradient(
            subset=["Salary Score"]
        ),
        use_container_width=True,
        height=420,
    )

    csv = score_table.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Salary Score export CSV", csv, "salary_score_export.csv", "text/csv")


def raw_data_view(df: pd.DataFrame):
    st.subheader("Adattábla")
    st.dataframe(df, use_container_width=True, height=650)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Szűrt adatok exportálása CSV-be", csv, "filtered_salaries.csv", "text/csv")


def main():
    st.title("💼 Salary Intelligence Dashboard")
    st.markdown("Interaktív HR Analytics dashboard a `salaries.xlsx` adataihoz.")

    with st.sidebar:
        st.header("📁 Adatforrás")
        uploaded = st.file_uploader("Opcionális Excel feltöltés", type=["xlsx"])

    try:
        df = load_data(uploaded)
    except Exception as exc:
        st.error(f"Nem sikerült betölteni az adatokat: {exc}")
        st.stop()

    filtered = apply_filters(df)

    st.sidebar.header("🧭 Nézet")
    page = st.sidebar.radio(
        "Dashboard oldal",
        [
            "Executive overview",
            "Salary analytics",
            "Geographical analytics",
            "HR segmentáció",
            "Hackathon bónuszok",
            "Adattábla",
        ],
    )

    if page == "Executive overview":
        executive_view(filtered)
    elif page == "Salary analytics":
        salary_deep_dive(filtered)
    elif page == "Geographical analytics":
        geography_view(filtered)
    elif page == "HR segmentáció":
        hr_segments_view(filtered)
    elif page == "Hackathon bónuszok":
        bonus_view(filtered)
    else:
        raw_data_view(filtered)

    st.sidebar.divider()
    st.sidebar.caption("Tipp: hackathon demónál kezdd az Executive overview oldallal, majd mutasd meg a Salary Score és What-if részt.")


if __name__ == "__main__":
    main()
