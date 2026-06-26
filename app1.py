import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Értékesítési Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #EAF7E6 0%, #F7FBF4 45%, #DFF3DC 100%);
}
[data-testid="stHeader"] { background: transparent; }
.main { background: transparent; }
.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1500px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12372A 0%, #1B4332 100%);
}
[data-testid="stSidebar"] * {
    color: #F0FFF4 !important;
}
h1 {
    color: #12372A;
    font-weight: 800;
}
h2, h3 {
    color: #1B4332;
    font-weight: 700;
}
.hero-card {
    background: rgba(255,255,255,0.88);
    border-radius: 26px;
    padding: 26px 30px;
    border: 1px solid rgba(215,230,212,0.9);
    box-shadow: 0 18px 45px rgba(27,67,50,0.14);
    margin-bottom: 22px;
}
.hero-title {
    font-size: 36px;
    font-weight: 850;
    color: #12372A;
}
.hero-subtitle {
    font-size: 16px;
    color: #4B6358;
}
.hero-badge {
    display: inline-block;
    background: #DFF5DF;
    color: #1B4332;
    padding: 7px 13px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 12px;
    border: 1px solid #B8DDB2;
}
.kpi-card {
    background: rgba(255,255,255,0.94);
    padding: 19px;
    border-radius: 24px;
    box-shadow: 0 16px 34px rgba(27,67,50,0.12);
    border: 1px solid rgba(215,230,212,0.95);
    min-height: 142px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    height: 6px;
    width: 100%;
    background: var(--accent);
}
.kpi-icon {
    width: 36px;
    height: 36px;
    border-radius: 13px;
    background: var(--soft);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    margin-bottom: 10px;
}
.kpi-label {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 6px;
    font-weight: 700;
    text-transform: uppercase;
}
.kpi-value {
    font-size: 29px;
    font-weight: 850;
    color: var(--accent);
}
.kpi-note {
    font-size: 13px;
    color: #52715F;
    margin-top: 9px;
    font-weight: 600;
}
.sales-card { --accent: #2563EB; --soft: #DBEAFE; }
.profit-card { --accent: #16A34A; --soft: #DCFCE7; }
.orders-card { --accent: #F97316; --soft: #FFEDD5; }
.quantity-card { --accent: #7C3AED; --soft: #EDE9FE; }
.margin-card { --accent: #0891B2; --soft: #CFFAFE; }
.discount-card { --accent: #DC2626; --soft: #FEE2E2; }

div[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,0.94);
    border-radius: 24px;
    padding: 16px;
    box-shadow: 0 16px 34px rgba(27,67,50,0.12);
    border: 1px solid rgba(215,230,212,0.95);
}
.insight-box {
    background: rgba(255,255,255,0.96);
    padding: 24px 26px;
    border-radius: 24px;
    border-left: 9px solid #2E7D32;
    box-shadow: 0 16px 34px rgba(27,67,50,0.12);
    color: #1B4332;
    font-size: 16px;
    line-height: 1.7;
}
details {
    background: rgba(255,255,255,0.94);
    border-radius: 22px;
    padding: 13px;
    border: 1px solid rgba(215,230,212,0.95);
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_excel("sales_minta.xlsx")

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])

    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Year"] = df["Order Date"].dt.year

    df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

    if "Shipping Time Range" not in df.columns:
        df["Shipping Time Range"] = pd.cut(
            df["Shipping Days"],
            bins=[-1, 2, 5, 10, 999],
            labels=["0-2 nap", "3-5 nap", "6-10 nap", "10+ nap"]
        )

    if "Shipping Cost per Unit" not in df.columns:
        if "Shipping Cost" in df.columns:
            df["Shipping Cost per Unit"] = df["Shipping Cost"] / df["Quantity"]
        else:
            df["Shipping Cost per Unit"] = df["Sales"] / df["Quantity"]

    return df


df = load_data()

st.sidebar.title("📊 Értékesítési irányítópult")
st.sidebar.caption("Szűrhető vezetői dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Szűrők")

min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

selected_date_range = st.sidebar.date_input(
    "Rendelési dátum",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

years = sorted(df["Year"].dropna().unique())
regions = sorted(df["Region"].dropna().unique())
categories = sorted(df["Category"].dropna().unique())
segments = sorted(df["Segment"].dropna().unique())

selected_years = st.sidebar.multiselect("Év", years, default=years)
selected_regions = st.sidebar.multiselect("Régió", regions, default=regions)
selected_categories = st.sidebar.multiselect("Kategória", categories, default=categories)

subcategory_base = df[df["Category"].isin(selected_categories)]
subcategories = sorted(subcategory_base["Sub-Category"].dropna().unique())

selected_subcategories = st.sidebar.multiselect(
    "Alkategória",
    subcategories,
    default=subcategories
)

selected_segments = st.sidebar.multiselect("Vevőszegmens", segments, default=segments)

if "Ship Mode" in df.columns:
    ship_modes = sorted(df["Ship Mode"].dropna().unique())
    selected_ship_modes = st.sidebar.multiselect(
        "Szállítási mód",
        ship_modes,
        default=ship_modes
    )
else:
    selected_ship_modes = []

if "Product Name" in df.columns:
    product_search = st.sidebar.text_input(
        "Termék keresése",
        placeholder="Írj be terméknevet..."
    )
else:
    product_search = ""

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Szűrők visszaállítása"):
    st.rerun()

if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date = pd.to_datetime(selected_date_range[0])
    end_date = pd.to_datetime(selected_date_range[1])
else:
    start_date = pd.to_datetime(min_date)
    end_date = pd.to_datetime(max_date)

filtered = df[
    (df["Order Date"] >= start_date) &
    (df["Order Date"] <= end_date) &
    (df["Year"].isin(selected_years)) &
    (df["Region"].isin(selected_regions)) &
    (df["Category"].isin(selected_categories)) &
    (df["Sub-Category"].isin(selected_subcategories)) &
    (df["Segment"].isin(selected_segments))
]

if "Ship Mode" in df.columns and selected_ship_modes:
    filtered = filtered[filtered["Ship Mode"].isin(selected_ship_modes)]

if "Product Name" in df.columns and product_search.strip():
    filtered = filtered[
        filtered["Product Name"].str.contains(product_search, case=False, na=False)
    ]

if filtered.empty:
    st.warning("Nincs adat a kiválasztott szűrőkkel.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
orders = filtered["Order ID"].nunique()
quantity = filtered["Quantity"].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales != 0 else 0
avg_discount = filtered["Discount"].mean() * 100

st.markdown("""
<div class="hero-card">
    <div class="hero-badge">📈 Vezetői összefoglaló</div>
    <div class="hero-title">Értékesítési teljesítmény dashboard</div>
    <div class="hero-subtitle">
        Árbevétel, profit, rendelések, kedvezmények, szállítás és üzleti megállapítások egy helyen.
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Vezetői dashboard",
    "📈 Árbevétel és profit elemzés",
    "📦 Kategória és alkategória mennyiség",
    "🚚 Szállítási dashboard",
    "📋 Részletes adatok"
])

with tab1:
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        st.markdown(f"""
        <div class="kpi-card sales-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Összes árbevétel</div>
            <div class="kpi-value">${total_sales:,.0f}</div>
            <div class="kpi-note">Teljes értékesítés</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card profit-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-label">Összes profit</div>
            <div class="kpi-value">${total_profit:,.0f}</div>
            <div class="kpi-note">Teljes nyereség</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card orders-card">
            <div class="kpi-icon">🧾</div>
            <div class="kpi-label">Rendelések száma</div>
            <div class="kpi-value">{orders:,.0f}</div>
            <div class="kpi-note">Egyedi rendelések</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card quantity-card">
            <div class="kpi-icon">📦</div>
            <div class="kpi-label">Eladott mennyiség</div>
            <div class="kpi-value">{quantity:,.0f}</div>
            <div class="kpi-note">Összes darabszám</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="kpi-card margin-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">Profitráta</div>
            <div class="kpi-value">{profit_margin:.1f}%</div>
            <div class="kpi-note">Profit / Árbevétel</div>
        </div>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown(f"""
        <div class="kpi-card discount-card">
            <div class="kpi-icon">🏷️</div>
            <div class="kpi-label">Átlagos kedvezmény</div>
            <div class="kpi-value">{avg_discount:.1f}%</div>
            <div class="kpi-note">Átlagos engedmény</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    monthly = filtered.groupby("Month", as_index=False).agg({"Sales": "sum", "Profit": "sum"})

    left, right = st.columns(2)

    with left:
        st.markdown("### Árbevétel alakulása")
        fig_sales = px.line(
            monthly,
            x="Month",
            y="Sales",
            markers=True,
            color_discrete_sequence=["#2563EB"]
        )
        fig_sales.update_traces(line=dict(width=4), marker=dict(size=8))
        fig_sales.update_layout(
            height=370,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Hónap",
            yaxis_title="Árbevétel",
            font=dict(color="#1B4332"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_sales, use_container_width=True)

    with right:
        st.markdown("### Profit alakulása")
        fig_profit = px.line(
            monthly,
            x="Month",
            y="Profit",
            markers=True,
            color_discrete_sequence=["#16A34A"]
        )
        fig_profit.update_traces(line=dict(width=4), marker=dict(size=8))
        fig_profit.update_layout(
            height=370,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Hónap",
            yaxis_title="Profit",
            font=dict(color="#1B4332"),
            hovermode="x unified"
        )
        st.plotly_chart(fig_profit, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    category_sales = filtered.groupby("Category", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    region_sales = filtered.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=True)
    segment_sales = filtered.groupby("Segment", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)

    with col1:
        st.markdown("### Árbevétel kategóriánként")
        fig_cat = px.pie(
            category_sales,
            names="Category",
            values="Sales",
            hole=0.58,
            color_discrete_sequence=["#2563EB", "#16A34A", "#F97316", "#7C3AED"]
        )
        fig_cat.update_layout(
            height=355,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(color="#1B4332")
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.markdown("### Árbevétel régiónként")
        fig_region = px.bar(
            region_sales,
            x="Sales",
            y="Region",
            orientation="h",
            text_auto=".2s",
            color_discrete_sequence=["#2E7D32"]
        )
        fig_region.update_layout(
            height=355,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Árbevétel",
            yaxis_title="",
            font=dict(color="#1B4332")
        )
        st.plotly_chart(fig_region, use_container_width=True)

    with col3:
        st.markdown("### Árbevétel vevőszegmensenként")
        fig_seg = px.pie(
            segment_sales,
            names="Segment",
            values="Sales",
            hole=0.58,
            color_discrete_sequence=["#0891B2", "#7C3AED", "#F97316"]
        )
        fig_seg.update_layout(
            height=355,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(color="#1B4332")
        )
        st.plotly_chart(fig_seg, use_container_width=True)

with tab2:
    st.markdown("## Árbevétel és profit részletes elemzése")

    monthly_analysis = (
        filtered
        .groupby("Month", as_index=False)
        .agg({
            "Sales": "sum",
            "Profit": "sum",
            "Order ID": "nunique",
            "Quantity": "sum",
            "Discount": "mean"
        })
        .rename(columns={"Order ID": "Orders"})
    )

    monthly_analysis["Profitráta (%)"] = monthly_analysis["Profit"] / monthly_analysis["Sales"] * 100
    monthly_analysis["Árbevétel változás (%)"] = monthly_analysis["Sales"].pct_change() * 100
    monthly_analysis["Profit változás (%)"] = monthly_analysis["Profit"].pct_change() * 100

    best_sales_month = monthly_analysis.sort_values("Sales", ascending=False).iloc[0]
    best_profit_month = monthly_analysis.sort_values("Profit", ascending=False).iloc[0]
    worst_profit_month = monthly_analysis.sort_values("Profit", ascending=True).iloc[0]

    a1, a2, a3, a4 = st.columns(4)

    with a1:
        st.markdown(f"""
        <div class="kpi-card sales-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Legjobb árbevételű hónap</div>
            <div class="kpi-value">{best_sales_month["Month"]}</div>
            <div class="kpi-note">${best_sales_month["Sales"]:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with a2:
        st.markdown(f"""
        <div class="kpi-card profit-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-label">Legjobb profitú hónap</div>
            <div class="kpi-value">{best_profit_month["Month"]}</div>
            <div class="kpi-note">${best_profit_month["Profit"]:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with a3:
        st.markdown(f"""
        <div class="kpi-card discount-card">
            <div class="kpi-icon">⚠️</div>
            <div class="kpi-label">Leggyengébb profitú hónap</div>
            <div class="kpi-value">{worst_profit_month["Month"]}</div>
            <div class="kpi-note">${worst_profit_month["Profit"]:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with a4:
        st.markdown(f"""
        <div class="kpi-card margin-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">Átlagos profitráta</div>
            <div class="kpi-value">{profit_margin:.1f}%</div>
            <div class="kpi-note">Teljes időszak alapján</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Árbevétel és profit összehasonlítása")

    comparison = monthly_analysis.melt(
        id_vars="Month",
        value_vars=["Sales", "Profit"],
        var_name="Mutató",
        value_name="Érték"
    )

    comparison["Mutató"] = comparison["Mutató"].replace({
        "Sales": "Árbevétel",
        "Profit": "Profit"
    })

    fig_compare = px.line(
        comparison,
        x="Month",
        y="Érték",
        color="Mutató",
        markers=True,
        color_discrete_map={
            "Árbevétel": "#2563EB",
            "Profit": "#16A34A"
        }
    )

    fig_compare.update_traces(line=dict(width=4), marker=dict(size=8))
    fig_compare.update_layout(
        height=430,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Hónap",
        yaxis_title="Érték",
        hovermode="x unified",
        font=dict(color="#1B4332"),
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig_compare, use_container_width=True)

    left2, right2 = st.columns(2)

    with left2:
        st.markdown("### Profitráta alakulása")
        fig_margin = px.bar(
            monthly_analysis,
            x="Month",
            y="Profitráta (%)",
            color="Profitráta (%)",
            color_continuous_scale="Greens"
        )
        fig_margin.update_layout(
            height=380,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Hónap",
            yaxis_title="Profitráta (%)",
            font=dict(color="#1B4332"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    with right2:
        st.markdown("### Havi profitváltozás")
        fig_profit_change = px.bar(
            monthly_analysis,
            x="Month",
            y="Profit változás (%)",
            color="Profit változás (%)",
            color_continuous_scale="RdYlGn"
        )
        fig_profit_change.update_layout(
            height=380,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Hónap",
            yaxis_title="Profit változás (%)",
            font=dict(color="#1B4332"),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_profit_change, use_container_width=True)

    st.markdown("### Automatikus elemzés")

    st.markdown(f"""
    <div class="insight-box">
        <p>💰 A legmagasabb árbevételű hónap: <b>{best_sales_month["Month"]}</b>, értéke <b>${best_sales_month["Sales"]:,.0f}</b>.</p>
        <p>📈 A legmagasabb profitú hónap: <b>{best_profit_month["Month"]}</b>, értéke <b>${best_profit_month["Profit"]:,.0f}</b>.</p>
        <p>⚠️ A leggyengébb profitú hónap: <b>{worst_profit_month["Month"]}</b>, értéke <b>${worst_profit_month["Profit"]:,.0f}</b>.</p>
        <p>🎯 A teljes időszak profitrátája <b>{profit_margin:.1f}%</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Havi árbevétel és profit elemző tábla"):
        st.dataframe(monthly_analysis, use_container_width=True)

with tab3:
    st.markdown("## Termékkategóriák és alkategóriák eladott mennyisége")

    category_quantity = (
        filtered
        .groupby("Category", as_index=False)
        .agg({
            "Quantity": "sum",
            "Sales": "sum",
            "Profit": "sum",
            "Order ID": "nunique"
        })
        .rename(columns={"Order ID": "Rendelések száma"})
        .sort_values("Quantity", ascending=False)
    )

    subcategory_quantity = (
        filtered
        .groupby(["Category", "Sub-Category"], as_index=False)
        .agg({
            "Quantity": "sum",
            "Sales": "sum",
            "Profit": "sum",
            "Order ID": "nunique"
        })
        .rename(columns={"Order ID": "Rendelések száma"})
        .sort_values("Quantity", ascending=False)
    )

    top_category = category_quantity.iloc[0]
    top_subcategory = subcategory_quantity.iloc[0]
    weakest_subcategory = subcategory_quantity.sort_values("Quantity", ascending=True).iloc[0]

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        st.markdown(f"""
        <div class="kpi-card quantity-card">
            <div class="kpi-icon">📦</div>
            <div class="kpi-label">Összes eladott mennyiség</div>
            <div class="kpi-value">{filtered["Quantity"].sum():,.0f}</div>
            <div class="kpi-note">Darabszám összesen</div>
        </div>
        """, unsafe_allow_html=True)

    with q2:
        st.markdown(f"""
        <div class="kpi-card sales-card">
            <div class="kpi-icon">🏆</div>
            <div class="kpi-label">Legerősebb kategória</div>
            <div class="kpi-value">{top_category["Category"]}</div>
            <div class="kpi-note">{top_category["Quantity"]:,.0f} db</div>
        </div>
        """, unsafe_allow_html=True)

    with q3:
        st.markdown(f"""
        <div class="kpi-card profit-card">
            <div class="kpi-icon">⭐</div>
            <div class="kpi-label">Top alkategória</div>
            <div class="kpi-value">{top_subcategory["Sub-Category"]}</div>
            <div class="kpi-note">{top_subcategory["Quantity"]:,.0f} db</div>
        </div>
        """, unsafe_allow_html=True)

    with q4:
        st.markdown(f"""
        <div class="kpi-card discount-card">
            <div class="kpi-icon">🔎</div>
            <div class="kpi-label">Legalacsonyabb mennyiség</div>
            <div class="kpi-value">{weakest_subcategory["Sub-Category"]}</div>
            <div class="kpi-note">{weakest_subcategory["Quantity"]:,.0f} db</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Eladott mennyiség kategóriánként")

    fig_category_qty = px.bar(
        category_quantity,
        x="Category",
        y="Quantity",
        text_auto=".2s",
        color="Category",
        color_discrete_sequence=["#2563EB", "#16A34A", "#F97316", "#7C3AED"]
    )

    fig_category_qty.update_layout(
        height=420,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Kategória",
        yaxis_title="Eladott mennyiség",
        font=dict(color="#1B4332"),
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False
    )

    st.plotly_chart(fig_category_qty, use_container_width=True)

    left3, right3 = st.columns(2)

    with left3:
        st.markdown("### Eladott mennyiség alkategóriánként")

        fig_subcategory_qty = px.bar(
            subcategory_quantity,
            x="Quantity",
            y="Sub-Category",
            color="Category",
            orientation="h",
            text_auto=".2s",
            color_discrete_sequence=["#2563EB", "#16A34A", "#F97316", "#7C3AED"]
        )

        fig_subcategory_qty.update_layout(
            height=560,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Eladott mennyiség",
            yaxis_title="Alkategória",
            font=dict(color="#1B4332"),
            margin=dict(l=20, r=20, t=20, b=20),
            yaxis=dict(categoryorder="total ascending")
        )

        st.plotly_chart(fig_subcategory_qty, use_container_width=True)

    with right3:
        st.markdown("### Kategória és alkategória hierarchia")

        fig_treemap = px.treemap(
            subcategory_quantity,
            path=["Category", "Sub-Category"],
            values="Quantity",
            color="Quantity",
            color_continuous_scale="Greens",
            hover_data={
                "Sales": ":,.0f",
                "Profit": ":,.0f",
                "Rendelések száma": True
            }
        )

        fig_treemap.update_layout(
            height=560,
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(color="#1B4332")
        )

        st.plotly_chart(fig_treemap, use_container_width=True)

    st.markdown("### Automatikus termékmennyiség-elemzés")

    category_share = top_category["Quantity"] / filtered["Quantity"].sum() * 100
    subcategory_share = top_subcategory["Quantity"] / filtered["Quantity"].sum() * 100

    st.markdown(f"""
    <div class="insight-box">
        <p>📦 A legtöbb eladott darabszámot a <b>{top_category["Category"]}</b> kategória adja, összesen <b>{top_category["Quantity"]:,.0f}</b> darabbal.</p>
        <p>🏆 Ez a kategória az összes eladott mennyiség <b>{category_share:.1f}%</b>-át képviseli.</p>
        <p>⭐ A legerősebb alkategória mennyiség alapján: <b>{top_subcategory["Sub-Category"]}</b>, összesen <b>{top_subcategory["Quantity"]:,.0f}</b> darabbal.</p>
        <p>📊 Ez az alkategória az összes eladott mennyiség <b>{subcategory_share:.1f}%</b>-át adja.</p>
        <p>🔎 A legalacsonyabb eladott mennyiséggel rendelkező alkategória: <b>{weakest_subcategory["Sub-Category"]}</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Kategória szerinti mennyiségi tábla"):
        st.dataframe(category_quantity, use_container_width=True)

    with st.expander("Alkategória szerinti mennyiségi tábla"):
        st.dataframe(subcategory_quantity, use_container_width=True)

with tab4:
    st.markdown("## Szállítási dashboard")

    avg_shipping_days = filtered["Shipping Days"].mean()
    fastest_shipping = filtered["Shipping Days"].min()
    slowest_shipping = filtered["Shipping Days"].max()
    most_used_ship_mode = filtered["Ship Mode"].mode()[0] if "Ship Mode" in filtered.columns else "Nincs adat"

    s1, s2, s3, s4 = st.columns(4)

    with s1:
        st.markdown(f"""
        <div class="kpi-card quantity-card">
            <div class="kpi-icon">🚚</div>
            <div class="kpi-label">Átlagos szállítási idő</div>
            <div class="kpi-value">{avg_shipping_days:.1f} nap</div>
            <div class="kpi-note">Ship Date - Order Date</div>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown(f"""
        <div class="kpi-card profit-card">
            <div class="kpi-icon">⚡</div>
            <div class="kpi-label">Leggyorsabb szállítás</div>
            <div class="kpi-value">{fastest_shipping:.0f} nap</div>
            <div class="kpi-note">Minimum szállítási idő</div>
        </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown(f"""
        <div class="kpi-card discount-card">
            <div class="kpi-icon">🐢</div>
            <div class="kpi-label">Leghosszabb szállítás</div>
            <div class="kpi-value">{slowest_shipping:.0f} nap</div>
            <div class="kpi-note">Maximum szállítási idő</div>
        </div>
        """, unsafe_allow_html=True)

    with s4:
        st.markdown(f"""
        <div class="kpi-card sales-card">
            <div class="kpi-icon">📦</div>
            <div class="kpi-label">Leggyakoribb mód</div>
            <div class="kpi-value">{most_used_ship_mode}</div>
            <div class="kpi-note">Ship Mode alapján</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    ship_mode_summary = (
        filtered
        .groupby("Ship Mode", as_index=False)
        .agg({
            "Order ID": "nunique",
            "Sales": "sum",
            "Profit": "sum",
            "Shipping Days": "mean",
            "Shipping Cost per Unit": "mean"
        })
        .rename(columns={"Order ID": "Rendelések száma"})
    )

    left4, right4 = st.columns(2)

    with left4:
        st.markdown("### Szállítási mód megoszlása")

        fig_ship_mode = px.pie(
            ship_mode_summary,
            names="Ship Mode",
            values="Rendelések száma",
            hole=0.55,
            color_discrete_sequence=["#2563EB", "#16A34A", "#F97316", "#7C3AED"]
        )

        fig_ship_mode.update_layout(
            height=390,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(color="#1B4332")
        )

        st.plotly_chart(fig_ship_mode, use_container_width=True)

    with right4:
        st.markdown("### Átlagos szállítási idő szállítási mód szerint")

        fig_ship_days = px.bar(
            ship_mode_summary.sort_values("Shipping Days", ascending=True),
            x="Shipping Days",
            y="Ship Mode",
            orientation="h",
            text_auto=".2f",
            color="Shipping Days",
            color_continuous_scale="Greens"
        )

        fig_ship_days.update_layout(
            height=390,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Átlagos szállítási idő / nap",
            yaxis_title="Szállítási mód",
            font=dict(color="#1B4332"),
            margin=dict(l=20, r=20, t=20, b=20)
        )

        st.plotly_chart(fig_ship_days, use_container_width=True)

    left5, right5 = st.columns(2)

    with left5:
        st.markdown("### Shipping Time vs Profit")

        fig_time_profit = px.scatter(
            filtered,
            x="Shipping Days",
            y="Profit",
            size="Sales",
            color="Ship Mode",
            hover_data=["Order ID", "Category", "Sub-Category", "Sales"],
            color_discrete_sequence=["#2563EB", "#16A34A", "#F97316", "#7C3AED"]
        )

        fig_time_profit.update_layout(
            height=430,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Szállítási idő / nap",
            yaxis_title="Profit",
            font=dict(color="#1B4332"),
            margin=dict(l=20, r=20, t=20, b=20)
        )

        st.plotly_chart(fig_time_profit, use_container_width=True)

    with right5:
        st.markdown("### Shipping Cost per Unit vs Sales")

        fig_cost_sales = px.scatter(
            filtered,
            x="Shipping Cost per Unit",
            y="Sales",
            size="Quantity",
            color="Ship Mode",
            hover_data=["Order ID", "Category", "Sub-Category", "Profit"],
            color_discrete_sequence=["#0891B2", "#7C3AED", "#F97316", "#16A34A"]
        )

        fig_cost_sales.update_layout(
            height=430,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Szállítási költség / egység",
            yaxis_title="Árbevétel",
            font=dict(color="#1B4332"),
            margin=dict(l=20, r=20, t=20, b=20)
        )

        st.plotly_chart(fig_cost_sales, use_container_width=True)

    st.markdown("### Shipping Time Range elemzés")

    ship_range_summary = (
        filtered
        .groupby("Shipping Time Range", as_index=False)
        .agg({
            "Order ID": "nunique",
            "Sales": "sum",
            "Profit": "sum",
            "Shipping Days": "mean"
        })
        .rename(columns={"Order ID": "Rendelések száma"})
        .sort_values("Shipping Days", ascending=True)
    )

    fig_ship_range = px.bar(
        ship_range_summary,
        x="Shipping Time Range",
        y="Rendelések száma",
        color="Profit",
        text_auto=".2s",
        color_continuous_scale="Greens"
    )

    fig_ship_range.update_layout(
        height=400,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Szállítási idő kategória",
        yaxis_title="Rendelések száma",
        font=dict(color="#1B4332"),
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig_ship_range, use_container_width=True)

    st.markdown("### Automatikus szállítási megállapítások")

    most_profitable_ship = ship_mode_summary.sort_values("Profit", ascending=False).iloc[0]
    fastest_ship_mode = ship_mode_summary.sort_values("Shipping Days", ascending=True).iloc[0]
    slowest_ship_mode = ship_mode_summary.sort_values("Shipping Days", ascending=False).iloc[0]

    st.markdown(f"""
    <div class="insight-box">
        <p>🚚 Az átlagos szállítási idő <b>{avg_shipping_days:.1f} nap</b>.</p>
        <p>📦 A leggyakrabban használt szállítási mód: <b>{most_used_ship_mode}</b>.</p>
        <p>⚡ A leggyorsabb átlagos szállítási mód: <b>{fastest_ship_mode["Ship Mode"]}</b>, átlagosan <b>{fastest_ship_mode["Shipping Days"]:.1f} nap</b>.</p>
        <p>🐢 A leglassabb átlagos szállítási mód: <b>{slowest_ship_mode["Ship Mode"]}</b>, átlagosan <b>{slowest_ship_mode["Shipping Days"]:.1f} nap</b>.</p>
        <p>💰 A legtöbb profitot hozó szállítási mód: <b>{most_profitable_ship["Ship Mode"]}</b>, összesen <b>${most_profitable_ship["Profit"]:,.0f}</b> profittal.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Szállítási mód szerinti összesítő tábla"):
        st.dataframe(ship_mode_summary, use_container_width=True)

    with st.expander("Szállítási idő kategória szerinti összesítő tábla"):
        st.dataframe(ship_range_summary, use_container_width=True)

with tab5:
    st.markdown("## Részletes adatok")
    st.dataframe(filtered, use_container_width=True)