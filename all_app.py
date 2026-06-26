import runpy
from pathlib import Path

import streamlit as st

# ============================================================
# Dashboard Hub - közös indító a 3 streamlit apphoz
# Nyitóképernyő: 3 csempe (app1, app2, app3).
# Csempére kattintva a megfelelő dashboard jelenik meg.
# ============================================================

st.set_page_config(
    page_title="Dashboard Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent

# Az egyes appok metaadatai
APPS = {
    "app1": {
        "file": "app1.py",
        "title": "Értékesítési Dashboard",
        "desc": "Sales adatok, bevétel és szállítási elemzések.",
        "icon": "�📈",
        "color": "#1B4332",
    },
    "app2": {
        "file": "app2.py",
        "title": "Netflix Content Strategy",
        "desc": "Tartalomstratégiai és nézettségi mutatók.",
        "icon": "🎬🍿",
        "color": "#E50914",
    },
    "app3": {
        "file": "app3.py",
        "title": "Call Center Dashboard",
        "desc": "Hívásforgalom, agentek és témák elemzése.",
        "icon": "🎧☎️",
        "color": "#38bdf8",
    },
}


# ------------------------------------------------------------
# Landing page (csempék)
# ------------------------------------------------------------
def render_landing():
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0b1120 100%);
        }
        .hub-title {
            text-align: center;
            color: #f8fafc;
            font-size: 44px;
            font-weight: 850;
            margin-bottom: 4px;
        }
        .hub-subtitle {
            text-align: center;
            color: #94a3b8;
            font-size: 17px;
            margin-bottom: 36px;
        }
        .tile-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(148,163,184,0.25);
            border-radius: 22px;
            padding: 28px 24px 18px 24px;
            text-align: center;
            box-shadow: 0 18px 45px rgba(0,0,0,0.35);
            min-height: 210px;
        }
        .tile-icon { font-size: 56px; }
        .tile-name {
            color: #f1f5f9;
            font-size: 23px;
            font-weight: 800;
            margin-top: 10px;
        }
        .tile-desc {
            color: #cbd5e1;
            font-size: 15px;
            margin-top: 8px;
            min-height: 48px;
        }
        div[data-testid="stButton"] > button {
            width: 100%;
            border-radius: 14px;
            font-weight: 700;
            font-size: 16px;
            padding: 10px 0;
            border: none;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: #ffffff;
        }
        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hub-title">🚀 Dashboard Hub</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hub-subtitle">Válassz egy dashboardot a megnyitáshoz</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(APPS), gap="large")
    for col, (key, meta) in zip(cols, APPS.items()):
        with col:
            st.markdown(
                f"""
                <div class="tile-card">
                    <div class="tile-icon">{meta['icon']}</div>
                    <div class="tile-name">{meta['title']}</div>
                    <div class="tile-desc">{meta['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Megnyitás · {key}", key=f"open_{key}", use_container_width=True):
                st.query_params["app"] = key
                st.rerun()


# ------------------------------------------------------------
# Kiválasztott app futtatása
# ------------------------------------------------------------
def run_app(key):
    meta = APPS[key]
    app_path = BASE_DIR / meta["file"]

    # Vissza-gomb az oldalsávban - fix piros háttér, fehér felirat
    st.markdown(
        """
        <style>
        div.st-key-back_sidebar button {
            background-color: #d00000 !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
        }
        div.st-key-back_sidebar button:hover {
            background-color: #b00000 !important;
            color: #ffffff !important;
        }
        div.st-key-back_sidebar button p {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        if st.button("⬅ Vissza a kezdőképernyőre", key="back_sidebar", use_container_width=True):
            st.query_params.clear()
            st.rerun()
        st.markdown("---")

    if not app_path.exists():
        st.error(f"A fájl nem található: {app_path.name}")
        return

    # A set_page_config-ot csak egyszer lehet hívni futásonként,
    # ezért a betöltött app set_page_config hívását semlegesítjük.
    original_set_page_config = st.set_page_config
    st.set_page_config = lambda *args, **kwargs: None
    try:
        runpy.run_path(str(app_path), run_name="__main__")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Hiba a(z) {meta['file']} futtatása közben: {exc}")
        st.exception(exc)
    finally:
        st.set_page_config = original_set_page_config


# ------------------------------------------------------------
# Router
# ------------------------------------------------------------
selected = st.query_params.get("app")

if selected in APPS:
    run_app(selected)
else:
    render_landing()
