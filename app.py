# pyrefly: ignore [missing-import]
import streamlit as st 
# pyrefly: ignore [missing-import]
import yfinance as yf
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go

@st.cache_data(ttl="1h")
def load_stock_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="max")
    try:
        info = ticker.info
    except Exception:
        info = {}
    return df, info

@st.cache_data(ttl="1h")
def load_msci_data():
    try:
        msci_data = yf.Ticker("URTH")
        return msci_data.history(period="max")
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl="1h")
def load_stock_news(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        return getattr(ticker, 'news', [])
    except Exception:
        return []

def filter_data_by_period(df, period):
    if df.empty or period == "max":
        return df
    latest_date = df.index.max()
    if period == "1mo":
        start_date = latest_date - pd.DateOffset(months=1)
    elif period == "3mo":
        start_date = latest_date - pd.DateOffset(months=3)
    elif period == "6mo":
        start_date = latest_date - pd.DateOffset(months=6)
    elif period == "1y":
        start_date = latest_date - pd.DateOffset(years=1)
    elif period == "2y":
        start_date = latest_date - pd.DateOffset(years=2)
    elif period == "5y":
        start_date = latest_date - pd.DateOffset(years=5)
    else:
        start_date = df.index.min()
    return df.loc[start_date:]


if "page" not in st.session_state:
    st.session_state["page"] = "landing"

def set_selected_stock(select_key):
    st.session_state["selected_option_1"] = select_key
    st.session_state["use_custom_ticker_1"] = False
    st.session_state["page"] = "details"

def handle_landing_select():
    """Triggered when the landing-page dropdown changes."""
    val = st.session_state.get("landing_select_option")
    if val:
        st.session_state["selected_option_1"] = val
        st.session_state["use_custom_ticker_1"] = False
        st.session_state["page"] = "details"

def handle_custom_search():
    val = st.session_state.get("landing_search_input_val", "").upper().strip()
    if val:
        st.session_state["use_custom_ticker_1"] = True
        st.session_state["custom_ticker_input_1"] = val
        st.session_state["page"] = "details"

def go_home():
    st.session_state["selected_option_1"] = None
    st.session_state["use_custom_ticker_1"] = False
    st.session_state["use_landing_custom"] = False
    st.session_state["custom_ticker_input_1"] = ""
    st.session_state["landing_search_input_val"] = ""
    st.session_state["landing_select_option"] = None
    st.session_state["page"] = "landing"


# --- CONFIGURATION & ACCESSIBLE STYLING ---
st.set_page_config(
    page_title="Finanz-Dashboard für Gelegenheitsanleger",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für exzellente Tab-Usability (Kein Abschneiden, starker visueller Fokus)
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1200px; padding-top: 2rem; }
    h1 { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; font-weight: 800; color: #1e293b; letter-spacing: -0.03em; }
    h2, h3 { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; color: #334155; font-weight: 700; letter-spacing: -0.02em; }

    /* Theme-respektierende, elegante Metric-Cards (Aesthetic-Usability-Effect) */
    [data-testid="stMetric"] {
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        padding: 18px 24px !important;
        border-radius: 10px !important;
        background-color: rgba(148, 163, 184, 0.04) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05) !important;
    }
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600 !important;
    }

    /* Dynamische Farbcodierung für Metriken (eingeschränkt auf unmittelbaren Nachfolgeschnitt) */
    [data-testid="stElementContainer"]:has(.metric-value-green) + [data-testid="stElementContainer"] [data-testid="stMetricValue"],
    [data-testid="element-container"]:has(.metric-value-green) + [data-testid="element-container"] [data-testid="stMetricValue"] {
        color: #2ecc71 !important;
    }
    [data-testid="stElementContainer"]:has(.metric-value-red) + [data-testid="stElementContainer"] [data-testid="stMetricValue"],
    [data-testid="element-container"]:has(.metric-value-red) + [data-testid="element-container"] [data-testid="stMetricValue"] {
        color: #e74c3c !important;
    }

    /* Optimierte Kompakt-Styles für Details im Stärkenprofil (innerhalb von Expandern) */
    [data-testid="stExpander"] [data-testid="stMetric"] {
        padding: 6px 8px !important;
    }
    [data-testid="stExpander"] [data-testid="stMetricValue"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        white-space: normal !important;
        line-height: 1.2 !important;
    }

    /* Hauptcontainer für Tab-Liste */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; 
        overflow-x: auto !important; white-space: nowrap !important;
    }

    /* Einzelner Tab im Normalzustand (Inaktiv) - Kontraststark & Theme-sensitiv */
    .stTabs [data-baseweb="tab"] { 
        background-color: color-mix(in srgb, var(--text-color) 4%, var(--background-color)) !important; 
        color: color-mix(in srgb, var(--text-color) 65%, var(--background-color)) !important; 
        font-size: 16px !important; /* Etwas größere Schrift */
        border-radius: 6px 6px 0px 0px; 
        padding: 12px 24px !important; /* Komfortableres Padding */
        border: 1px solid rgba(128, 128, 128, 0.2) !important; 
        font-weight: 600 !important;
        display: inline-flex !important; 
        white-space: nowrap !important;
        text-overflow: unset !important; 
        overflow: visible !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-color) !important; /* Voller Textkontrast beim Hovern */
        background-color: color-mix(in srgb, var(--text-color) 10%, var(--background-color)) !important;
        border-color: rgba(128, 128, 128, 0.4) !important;
        transition: color 0.15s ease, background-color 0.15s ease, border-color 0.15s ease;
    }
    .stTabs [data-baseweb="tab"]:focus,
    .stTabs [data-baseweb="tab"]:active {
        outline: none !important;
        box-shadow: none !important;
    }

    /* Aktiver / Ausgewählter Tab - Exzellenter Kontrast über var(--primary-color) */
    .stTabs [aria-selected="true"] { 
        background-color: color-mix(in srgb, var(--primary-color) 12%, var(--background-color)) !important; 
        color: var(--primary-color) !important; 
        border: 1px solid color-mix(in srgb, var(--primary-color) 45%, var(--background-color)) !important; 
        border-bottom: 4px solid var(--primary-color) !important; 
        font-weight: 700 !important;
        font-size: 16px !important;
    }

    /* CSS for custom logo buttons inside the grid */
    .custom-logo-btn {
        display: flex;
        align-items: center;
        gap: 10px;
        width: 100%;
        height: 42px;
        padding: 0 14px;
        background-color: rgba(148, 163, 184, 0.06);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 8px;
        box-sizing: border-box;
        transition: all 0.2s ease-in-out;
        pointer-events: none; /* Let clicks pass through to the button behind */
    }

    .custom-logo-img {
        height: 24px;
        width: 24px;
        object-fit: contain;
        border-radius: 4px;
        background-color: white;
        padding: 1px;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }

    .custom-logo-text {
        font-size: 14px;
        font-weight: 600;
        color: inherit;
    }

    /* Style container and make the real streamlit button overlay the custom HTML */
    .st-key-popular-stocks-container [data-testid="column"] {
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
    }

    .st-key-popular-stocks-container [data-testid="stButton"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 42px !important;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 10 !important;
    }

    .st-key-popular-stocks-container [data-testid="stButton"] button {
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important; /* Make it completely invisible */
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer !important;
    }

    /* Hover effect for custom button when the column is hovered */
    .st-key-popular-stocks-container [data-testid="column"]:hover .custom-logo-btn {
        background-color: rgba(14, 165, 233, 0.08) !important;
        border-color: rgba(14, 165, 233, 0.4) !important;
        box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.05) !important;
    }

    /* Style for home button to look like an H1 header */
    div[class*="st-key-home-button"] button,
    div[class*="st-key-home-button"] button * {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 2.75rem !important; /* matches large st.title size */
        line-height: 1.25 !important;
        font-weight: 800 !important;
        color: inherit !important;
        letter-spacing: -0.03em !important;
        text-align: left !important;
        box-shadow: none !important;
    }

    div[class*="st-key-home-button"] button:hover,
    div[class*="st-key-home-button"] button:hover * {
        background: transparent !important;
        color: #0284c7 !important; /* Change color slightly on hover to indicate clickability */
        box-shadow: none !important;
        border: none !important;
    }

    </style>
""", unsafe_allow_html=True)

# Dynamische Titel-Definition erfolgt weiter unten im Hauptfenster


# --- SIDEBAR (SUCHE MIT LEEREM INITIALZUSTAND) ---
st.sidebar.header("⚙️ Aktien-Suche")

# Wörterbuch beliebter Aktien
STOCK_OPTIONS = {
    "Apple Inc. (AAPL)": "AAPL",
    "NVIDIA Corporation (NVDA)": "NVDA",
    "Microsoft Corporation (MSFT)": "MSFT",
    "Tesla, Inc. (TSLA)": "TSLA",
    "Amazon.com, Inc. (AMZN)": "AMZN",
    "Alphabet Inc. / Google (GOOGL)": "GOOGL",
    "Meta Platforms, Inc. (META)": "META",
    "Netflix, Inc. (NFLX)": "NFLX",
    "Advanced Micro Devices (AMD)": "AMD",
    "Intel Corporation (INTC)": "INTC",
    "SAP SE (SAP)": "SAP",
    "Siemens AG (SIE.DE)": "SIE.DE",
    "Allianz SE (ALV.DE)": "ALV.DE",
    "✨ Eigener Ticker / Freie Eingabe...": "CUSTOM"
}

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Primäraktie")

# Toggle für Eingabe-Modus der Primäraktie
use_custom_ticker_1 = st.sidebar.toggle(
    "Freie Ticker-Eingabe",
    value=st.session_state.get("use_custom_ticker_1", False),
    help="💡 Schalte um, um entweder eine beliebte Aktie aus der Liste zu wählen (AUS) oder ein beliebiges globales Ticker-Symbol (z. B. 'MSFT' oder 'SAP.DE') einzugeben (AN).",
    key="use_custom_ticker_1"
)

ticker_input_1 = None
selected_option_1 = None
custom_ticker_input_1 = ""

if use_custom_ticker_1:
    # Wenn der Nutzer gerade vom Listen-Modus umschaltet und das Textfeld noch leer ist,
    # füllen wir es mit dem aktuell ausgewählten Ticker vor – so bleibt die Detailseite sichtbar.
    _prev_list_selection = st.session_state.get("selected_option_1")
    _prefill_ticker = ""
    if not st.session_state.get("custom_ticker_input_1", "") and _prev_list_selection:
        _resolved = STOCK_OPTIONS.get(_prev_list_selection, "")
        if _resolved and _resolved != "CUSTOM":
            _prefill_ticker = _resolved

    custom_ticker_input_1 = st.sidebar.text_input(
        "✍️ Ticker-Symbol eingeben:",
        value=st.session_state.get("custom_ticker_input_1", _prefill_ticker),
        max_chars=10,
        help="Gib hier ein beliebiges Ticker-Symbol ein (z. B. 'MSFT' für Microsoft oder 'SAP.DE' für SAP).",
        key="custom_ticker_input_1"
    ).upper().strip()
    ticker_input_1 = custom_ticker_input_1 if custom_ticker_input_1 else None
else:
    selected_option_1 = st.sidebar.selectbox(
        "Top Aktien auf einen Blick:",
        options=[k for k in STOCK_OPTIONS.keys() if STOCK_OPTIONS[k] != "CUSTOM"],
        index=None,
        placeholder="Wähle eine Aktie...",
        help="Wähle ein beliebtes Unternehmen aus der Liste.",
        key="selected_option_1"
    )
    if selected_option_1:
        ticker_input_1 = STOCK_OPTIONS[selected_option_1]
    elif st.session_state.get("custom_ticker_input_1", ""):
        # Fallback: Nutzer hat gerade vom Freitext-Modus zurückgeschaltet, aber noch
        # keinen Listeneintrag gewählt → vorherigen Ticker behalten, damit die Detailseite
        # sichtbar bleibt. go_home() löscht custom_ticker_input_1, daher funktionieren
        # Home-Button und "Zurück"-Button weiterhin korrekt.
        ticker_input_1 = st.session_state.get("custom_ticker_input_1")

st.sidebar.markdown("---")

# Checkbox für Vergleich aktivieren
compare_stock = st.sidebar.checkbox("⚖️ Aktie vergleichen", value=False, help="Aktiviere diese Option, um ein zweites Unternehmen für den direkten Vergleich hinzuzufügen.")

ticker_input_2 = None
selected_option_2 = None
custom_ticker_input_2 = ""

if compare_stock:
    st.sidebar.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.sidebar.subheader("⚖️ Vergleichsaktie")

    use_custom_ticker_2 = st.sidebar.toggle(
        "Freie Ticker-Eingabe",
        value=False,
        help="💡 Schalte um, um entweder eine beliebte Vergleichsaktie aus der Liste zu wählen (AUS) oder ein beliebiges globales Ticker-Symbol (z. B. 'MSFT' oder 'SAP.DE') einzugeben (AN).",
        key="toggle_comp"
    )

    if use_custom_ticker_2:
        custom_ticker_input_2 = st.sidebar.text_input(
            "✍️ Ticker-Symbol eingeben:",
            value="",
            max_chars=10,
            help="Gib hier ein beliebiges Vergleichs-Ticker-Symbol ein (z. B. 'MSFT' oder 'SAP.DE').",
            key="custom_comp"
        ).upper().strip()
        ticker_input_2 = custom_ticker_input_2 if custom_ticker_input_2 else None
    else:
        selected_option_2 = st.sidebar.selectbox(
            "Top Aktien auf einen Blick:",
            options=[k for k in STOCK_OPTIONS.keys() if STOCK_OPTIONS[k] != "CUSTOM"],
            index=None,
            placeholder="Wähle eine Vergleichsaktie...",
            help="Wähle ein beliebtes Vergleichsunternehmen aus der Liste.",
            key="select_comp"
        )
        if selected_option_2:
            ticker_input_2 = STOCK_OPTIONS[selected_option_2]

# --- Sidebar auf der Startseite ausblenden, auf Detailseite einblenden ---
if st.session_state.get("page", "landing") == "landing":
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)


if st.session_state.get("page", "landing") == "landing":
    st.button("📊  Stockguide: Dein persönliches Aktiendashboard", key="home-button-landing", on_click=go_home)
    st.caption("Konzipiert für Gelegenheitsanleger zur intuitiven Analyse des Marktes.")

    # --- INFO-KARTE ---
    with st.expander("ℹ️ Was bietet dir Stockguide?"):
        st.markdown("""
        - **Schnelle Marktanalyse:** Komplexe Börsendaten, verständlich aufbereitet für Gelegenheitsanleger.
        - **Klarheit statt Chaos:** Ein intuitives Design mit einfach verständlichen Erklärungen zu jedem Begriff.
        - **Alles auf einen Blick:** Kursverlauf, Fundamental-Kennzahlen, Rendite-Simulation und Nachrichten-Feed.
        """)

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    # --- AKTIENAUSWAHL: Toggle-Muster identisch zur Sidebar ---
    st.markdown("### 🔍 Welche Aktie möchtest du analysieren?")

    use_landing_custom = st.toggle(
        "Freie Ticker-Eingabe",
        value=st.session_state.get("use_landing_custom", False),
        help="💡 Schalte um, um entweder ein Unternehmen aus der Liste zu wählen (AUS) oder ein beliebiges globales Ticker-Symbol (z. B. 'MSFT' oder 'SAP.DE') einzugeben (AN).",
        key="use_landing_custom"
    )

    if use_landing_custom:
        st.text_input(
            "✍️ Ticker-Symbol eingeben:",
            value="",
            placeholder="z. B. AAPL, NVDA, SAP.DE, MSFT...",
            key="landing_search_input_val",
            on_change=handle_custom_search,
            help="Gib das offizielle Börsenkürzel ein (z. B. 'MSFT' für Microsoft oder 'SAP.DE' für SAP)."
        )
    else:
        st.selectbox(
            "Top Aktien auf einen Blick:",
            options=[k for k in STOCK_OPTIONS.keys() if STOCK_OPTIONS[k] != "CUSTOM"],
            index=None,
            placeholder="Unternehmen wählen...",
            key="landing_select_option",
            on_change=handle_landing_select,
            help="Wähle ein Unternehmen aus der Liste."
        )

    st.markdown("---")

    # --- SCHNELLEINSTIEG: Beliebte Aktien als Logo-Grid ---
    st.markdown("### 🎯 Oder wähle direkt eine beliebte Aktie:")
    st.markdown("Klicke auf eines der Unternehmen, um die Analyse sofort zu starten:")
    
    # 2x4 Grid von beliebten Aktien für schnellen Klick
    popular_keys = [
        ("Apple (AAPL)", "Apple Inc. (AAPL)", "apple.com", "AAPL"),
        ("NVIDIA (NVDA)", "NVIDIA Corporation (NVDA)", "nvidia.com", "NVDA"),
        ("Microsoft (MSFT)", "Microsoft Corporation (MSFT)", "microsoft.com", "MSFT"),
        ("Tesla (TSLA)", "Tesla, Inc. (TSLA)", "tesla.com", "TSLA"),
        ("Amazon (AMZN)", "Amazon.com, Inc. (AMZN)", "amazon.com", "AMZN"),
        ("Google (GOOGL)", "Alphabet Inc. / Google (GOOGL)", "google.com", "GOOGL"),
        ("Meta (META)", "Meta Platforms, Inc. (META)", "meta.com", "META"),
        ("SAP SE (SAP)", "SAP SE (SAP)", "sap.com", "SAP")
    ]
    
    with st.container(key="popular-stocks-container"):
        cols = st.columns(4)
        for i, (label, select_key, domain, ticker) in enumerate(popular_keys):
            with cols[i % 4]:
                logo_url = f"https://logos.hunter.io/{domain}"
                fallback_url = f"https://financialmodelingprep.com/image-stock/{ticker}.png"
                
                # Der echte Streamlit Button (wird durch CSS unsichtbar gemacht und überlagert das HTML)
                st.button(
                    label, 
                    use_container_width=True, 
                    key=f"btn_{select_key}",
                    on_click=set_selected_stock,
                    args=(select_key,)
                )
                
                # Das visuelle HTML für das Logo im Button
                st.markdown(
                    f"""
                    <div class="custom-logo-btn">
                        <img src="{logo_url}" onerror="this.onerror=null; this.src='{fallback_url}';" class="custom-logo-img">
                        <span class="custom-logo-text">{label}</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

    st.markdown("---")

else:
    st.button("📊  Stockguide", key="home-button-detail", on_click=go_home)
    st.caption("Konzipiert für Gelegenheitsanleger zur intuitiven Analyse des Marktes.")
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

    if not ticker_input_1:
        st.info("👈 Bitte wähle eine Aktie in der Seitenleiste aus oder gib ein Ticker-Symbol ein, um die Analyse anzuzeigen.")
        st.stop()

    # --- DATENABRUF & VERARBEITUNG BEI AKTIVER AUSWAHL ---
    with st.spinner("🚀 Marktdaten werden aufbereitet..."):
        try:
            # 1. Hauptaktie laden
            df_1, info_1 = load_stock_data(ticker_input_1)

            # Validierung der Hauptaktie zur Fehlervermeidung (Postel's Law / Nielsen Heuristik #5)
            if df_1.empty:
                st.error(f"⚠️ **Das Ticker-Symbol '{ticker_input_1}' konnte nicht geladen werden.**\n\nBitte überprüfe die Schreibweise in der Seitenleiste (z. B. 'AAPL' für Apple, 'NVDA' für NVIDIA oder 'SAP.DE' für SAP SE) und stelle sicher, dass eine Internetverbindung besteht.")
                st.button("🏠 Zurück zur Startseite", on_click=go_home, type="primary")
                st.stop()

            # 2. Benchmark laden
            df_msci = load_msci_data()

            # Dynamische Namensauflösung für alle Reiter
            name_1 = info_1.get('longName', selected_option_1.split(" (")[0] if selected_option_1 else ticker_input_1)

            df_2 = pd.DataFrame()
            info_2 = {}
            name_2 = ""
            if ticker_input_2:
                df_2, info_2 = load_stock_data(ticker_input_2)
                # Validierung der Vergleichsaktie zur Fehlervermeidung
                if df_2.empty:
                    st.warning(f"⚠️ **Die Vergleichsaktie '{ticker_input_2}' konnte nicht geladen werden.**\n\nDer Vergleich wird übersprungen. Bitte überprüfe die Schreibweise des Symbols.")
                    ticker_input_2 = None
                    df_2 = pd.DataFrame()
                else:
                    name_2 = info_2.get('longName', selected_option_2.split(" (")[0] if selected_option_2 else ticker_input_2)

            # --- 1. PROMINENTE KPIs ---
            kpi_cols = st.columns(2 if not df_2.empty else 1)


            def rendere_saubere_kpis(df, name, info, col, ticker):
                if len(df) >= 2:
                    aktueller_kurs = df['Close'].iloc[-1]
                    vortag_kurs = df['Close'].iloc[-2]
                    differenz = aktueller_kurs - vortag_kurs
                    prozent = (differenz / vortag_kurs) * 100
                    waehrung = info.get('currency', 'USD')

                    # Echten Firmennamen und Domain ermitteln
                    website = info.get('website')
                    logo_url = None
                    if website:
                        from urllib.parse import urlparse
                        try:
                            parsed = urlparse(website)
                            domain = parsed.netloc or parsed.path
                            if domain.startswith("www."):
                                domain = domain[4:]
                            domain = domain.split("/")[0]
                            logo_url = f"https://logos.hunter.io/{domain}"
                        except:
                            pass
                    
                    clean_ticker = ticker.split(".")[0].upper()
                    if not logo_url:
                        logo_url = f"https://financialmodelingprep.com/image-stock/{clean_ticker}.png"
                    fallback_url = f"https://financialmodelingprep.com/image-stock/{clean_ticker}.png"

                    # HTML für Header mit Logo
                    col.markdown(
                        f"""
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 15px;">
                            <img src="{logo_url}" onerror="this.onerror=null; this.src='{fallback_url}'; this.onerror=function(){{this.style.display='none';}}" style="height: 38px; width: 38px; object-fit: contain; border-radius: 6px; background-color: white; padding: 3px; border: 1px solid rgba(148, 163, 184, 0.2);">
                            <h3 style="margin: 0; line-height: 1.2;">{name}</h3>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

                    col.metric(
                        label="Aktueller Schlusskurs",
                        value=f"{aktueller_kurs:.2f} {waehrung}",
                        delta=f"{differenz:+.2f} {waehrung} ({prozent:+.2f}%)"
                    )


            rendere_saubere_kpis(df_1, name_1, info_1, kpi_cols[0], ticker_input_1)
            if not df_2.empty:
                rendere_saubere_kpis(df_2, name_2, info_2, kpi_cols[1], ticker_input_2)

            st.markdown("---")

            # --- 2. TABS ---
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🔮 Anlage-Kompass",
                "📈 Kursverlauf",
                "🔬 Fundamental-Analyse",
                "💰 Rendite-Rechner",
                "📰 Nachrichten"
            ])

            report_text = f"=== ANLAGE-REPORT ===\nStand: Aktuell\n\n"

            # --- TAB 1: ANLAGE-KOMPASS ---
            with tab1:

                kompass_cols = st.columns(2 if not df_2.empty else 1)


                def rendere_kompass_refactored(name, df, info, col, color_theme):
                    global report_text
                    col.markdown(f"### Profil-Analyse:   {name}")
                    current_price = df['Close'].iloc[-1]
                    sma_30 = df['Close'].rolling(window=30).mean().iloc[-1] if len(df) >= 30 else current_price
                    rec_key = info.get('recommendationKey', 'none').lower()

                    if "buy" in rec_key or current_price > (sma_30 * 1.03):
                        col.success(
                            "📈 **Kauf-Signal** — Das Unternehmen befindet sich in einem stabilen Aufwärtstrend.")
                        signal_txt = "Kauf-Signal"
                    elif "sell" in rec_key or current_price < (sma_30 * 0.97):
                        col.error("📉 **Verkaufs-Signal / Erhöhte Vorsicht** — Der aktuelle Trend zeigt nach unten.")
                        signal_txt = "Verkaufs-Signal"
                    else:
                        col.warning("↔️ **Halte-Signal / Abwarten** — Es liegt kein klarer Trend vor.")
                        signal_txt = "Halte-Signal"

                    report_text += f"Unternehmen: {name}\nUrteil: {signal_txt}\n"

                    kgv = info.get('trailingPE')
                    kgv_score = 3 if kgv is None else (5 if kgv < 15 else (4 if kgv < 25 else (2 if kgv < 40 else 1)))
                    div = info.get('dividendYield')
                    div_score = 3 if div is None else (1 if div == 0 else (2 if div < 0.015 else (4 if div < 0.035 else 5)))
                    beta = info.get('beta')
                    beta_score = 3 if beta is None else (5 if beta < 0.75 else (4 if beta < 1.05 else (3 if beta < 1.35 else (2 if beta < 1.75 else 1))))

                    target = info.get('targetMeanPrice', current_price)
                    potential = ((target / current_price) - 1) * 100
                    pot_score = 5 if potential > 20 else (4 if potential > 8 else (3 if potential > 0 else 2))
                    trend_score = 5 if current_price > (sma_30 * 1.06) else (
                        4 if current_price > sma_30 else (3 if current_price > (sma_30 * 0.94) else 1))

                    categories = ['Bewertung (KGV)', 'Dividendenrendite', 'Stabilität (Beta)',
                                  'Kurspotenzial', 'Aktueller Trend']
                    values = [kgv_score, div_score, beta_score, pot_score, trend_score]
                    categories += [categories[0]]
                    values += [values[0]]

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values, theta=categories, fill='toself',
                        fillcolor=color_theme['fill'], line=dict(color=color_theme['line'], width=2.5), name=name
                    ))
                    fig.update_layout(
                        paper_bgcolor="rgba(15, 23, 42, 1)", # slate-900 für hervorragenden Kontrast
                        plot_bgcolor="rgba(15, 23, 42, 1)",
                        polar=dict(
                            bgcolor="rgba(30, 41, 59, 1)", # slate-800
                            radialaxis=dict(visible=True, range=[0, 5], tickvals=[1, 3, 5],
                                            ticktext=['Niedrig', 'Mittel', 'Hoch'],
                                            tickfont=dict(size=12, color="#94a3b8"),
                                            gridcolor="rgba(71, 85, 105, 0.4)",
                                            linecolor="rgba(71, 85, 105, 0.4)"),
                            angularaxis=dict(tickfont=dict(size=13, color="#e2e8f0"),
                                             gridcolor="rgba(71, 85, 105, 0.4)")
                        ),
                        dragmode=False,
                        showlegend=False, height=460, margin=dict(l=60, r=60, t=40, b=40)
                    )
                    col.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    with col.expander("ℹ️ So liest du das Diagramm"):
                        st.markdown("""
                        - 🟦 **Bewertung (KGV):** Ist die Aktie günstig bewertet? (Hoch = günstig)
                        - 🟦 **Dividendenrendite:** Schüttet das Unternehmen regelmäßig Gewinne aus? (Hoch = mehr Ausschüttung)
                        - 🟦 **Stabilität (Beta):** Schwankt der Kurs wenig im Vergleich zum Markt? (Hoch = stabil)
                        - 🟦 **Kurspotenzial:** Erwarten Analysten Kurssteigerungen? (Hoch = mehr Potenzial)
                        - 🟦 **Aktueller Trend:** Liegt der Kurs über seinem 30-Tage-Durchschnitt? (Hoch = positiver Trend)
                        """)

                    with col.expander("📝 Details zum Stärkenprofil einsehen"):
                        target_price = info.get('targetMeanPrice')
                        
                        # Farbcodierte Einbettung des gesamten Spalten-Blocks über CSS-Klassen um vertikalen Versatz zu verhindern
                        if target_price:
                            if potential >= 0:
                                st.markdown('<div class="third-metric-green">', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="third-metric-red">', unsafe_allow_html=True)
                            col_d1, col_d2, col_d3 = st.columns(3)
                        else:
                            col_d1 = st.columns(1)[0]
                        
                        with col_d1:
                            if beta is not None:
                                beta_class = "metric-value-green" if beta <= 1.0 else "metric-value-red"
                                st.markdown(f'<div class="{beta_class}">', unsafe_allow_html=True)
                            st.metric(
                                label="Schwankungsrisiko (Beta)",
                                value=f"{beta:.2f}" if beta is not None else "N/A",
                                help="Das Beta misst, wie stark die Aktie im Vergleich zum Gesamtmarkt schwankt.\n\n• Beta > 1.0: Stärkere Schwankungen (höheres Risiko)\n• Beta = 1.0: Gleiche Schwankungen wie der Markt\n• Beta < 1.0: Ruhigere Kursbewegungen (weniger Risiko)"
                            )
                            if beta is not None:
                                st.markdown('</div>', unsafe_allow_html=True)
                        if target_price:
                            currency = info.get('currency', 'USD')
                            with col_d2:
                                target_class = "metric-value-green" if target > current_price else ("metric-value-red" if target < current_price else "")
                                if target_class:
                                    st.markdown(f'<div class="{target_class}">', unsafe_allow_html=True)
                                st.metric(
                                    label="Kursziel der Experten",
                                    value=f"{target:.2f} {currency}",
                                    help="Das von professionellen Finanzanalysten geschätzte durchschnittliche Kursziel der Aktie für die nächsten 12 Monate."
                                )
                                if target_class:
                                    st.markdown('</div>', unsafe_allow_html=True)
                            with col_d3:
                                pot_class = "metric-value-green" if potential >= 0 else "metric-value-red"
                                st.markdown(f'<div class="{pot_class}">', unsafe_allow_html=True)
                                st.metric(
                                    label="Analysten-Potenzial",
                                    value=f"{potential:+.2f}%",
                                    help="Die prozentuale Differenz zwischen dem aktuellen Kurs und dem Experten-Kursziel.\n\n• Positiver Wert: Analysten erwarten Kurssteigerungen\n• Negativer Wert: Analysten erwarten Kursrückgänge"
                                )
                                st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)


                theme_blue = {'fill': 'rgba(59, 130, 246, 0.25)', 'line': '#3b82f6'}
                theme_purple = {'fill': 'rgba(147, 51, 234, 0.25)', 'line': '#9333ea'}

                rendere_kompass_refactored(name_1, df_1, info_1, kompass_cols[0], theme_blue)
                if not df_2.empty:
                    rendere_kompass_refactored(name_2, df_2, info_2, kompass_cols[1], theme_purple)

                st.markdown("---")
                st.download_button(
                    label="📥 Diese Kurzanalyse herunterladen",
                    data=report_text,
                    file_name=f"Anlage_Zusammenfassung_{name_1.replace(' ', '_')}.txt",
                    mime="text/plain"
                )


            # --- TAB 2: KURSVERLAUF & LABOR ---
            with tab2:
                st.subheader("📈 Interaktiver Kursverlauf")

                time_period_chart = st.segmented_control(
                    "Zeitraum für Kursverlauf:",
                    options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                    default="1y",
                    format_func=lambda x: {
                        "1mo": "📅 1 Monat", "3mo": "📅 3 Monate", "6mo": "📅 6 Monate",
                        "1y": "📅 1 Jahr", "2y": "📅 2 Jahre", "5y": "📅 5 Jahre", "max": "⏳ Max"
                    }[x],
                    key="time_period_chart"
                )

                df_1_filtered = filter_data_by_period(df_1, time_period_chart)
                if df_1_filtered.index.tz is not None:
                    df_1_filtered.index = df_1_filtered.index.tz_localize(None)

                df_2_filtered = filter_data_by_period(df_2, time_period_chart) if not df_2.empty else df_2
                if not df_2_filtered.empty and df_2_filtered.index.tz is not None:
                    df_2_filtered.index = df_2_filtered.index.tz_localize(None)

                df_msci_filtered = filter_data_by_period(df_msci, time_period_chart) if not df_msci.empty else df_msci
                if not df_msci_filtered.empty and df_msci_filtered.index.tz is not None:
                    df_msci_filtered.index = df_msci_filtered.index.tz_localize(None)

                if df_2_filtered.empty:
                    chart_view = st.radio(
                        "Visualisierungs-Modus wählen:",
                        options=["Liniendiagramm",
                                 "Kerzenchart / Candlestick"],
                        horizontal=True
                    )
                else:
                    chart_view = "Liniendiagramm"
                    st.info(
                        "ℹ️ Bei aktiven Vergleichen ist der Linienmodus fest vorgegeben, um eine optische Überlagerung zu verhindern.")

                if chart_view == "Liniendiagramm":
                    st.markdown("**🔍 Optionale Filter & Zusatzlinien zuschalten:**")

                    num_cols = 5 if not df_2_filtered.empty else 4
                    lab_cols = st.columns(num_cols)

                    col_idx = 0
                    normalize = False

                    # Lesen ob MSCI World aktiv ist (aus session_state, da das Checkbox-Widget erst weiter unten gerendert wird)
                    show_msci_active = st.session_state.get("show_msci_val", False)

                    if not df_2_filtered.empty:
                        normalize = lab_cols[col_idx].checkbox(
                            "📊 Prozentualer Vergleich (%)", 
                            value=True,
                            disabled=show_msci_active,
                            help="Aktiviert den relativen Prozentvergleich, um die Wertentwicklung beider Aktien direkt vergleichen zu können." + (" (Automatisch aktiv, wenn MSCI World Index angezeigt wird.)" if show_msci_active else ""),
                            key="normalize_val"
                        )
                        col_idx += 1

                    # Wenn MSCI World oder Prozentvergleich aktiv ist, erzwingen wir prozentuale Skalierung.
                    is_normalized_mode = normalize

                    if show_msci_active:
                        is_normalized_mode = True

                    if is_normalized_mode:
                        st.session_state["show_sma_val"] = False
                        st.session_state["show_bollinger_val"] = False

                    show_sma = lab_cols[col_idx].checkbox(
                        "🔄 30-Tage Glättungslinie (SMA)",
                        value=True if not is_normalized_mode else False,
                        disabled=is_normalized_mode,
                        help="Zeigt den gleitenden 30-Tage-Durchschnitt des Aktienkurses. Glättet kurzfristige Schwankungen und macht den langfristigen Trend sichtbar. (Deaktiviert bei prozentualem Vergleich).",
                        key="show_sma_val"
                    )
                    col_idx += 1
                    
                    show_bollinger = lab_cols[col_idx].checkbox(
                        "🛡️ Schwankungskanal (Bollinger)",
                        value=False if not is_normalized_mode else False,
                        disabled=is_normalized_mode,
                        help="Zeigt ein statistisches Band um den Durchschnittskurs. Wenn der Kurs das Band berührt oder verlässt, kann das auf eine starke Bewegung hindeuten. (Deaktiviert bei prozentualem Vergleich).",
                        key="show_bollinger_val"
                    )
                    col_idx += 1
                    
                    show_drawdown = lab_cols[col_idx].checkbox(
                        "📉 Größter Einbruch (Drawdown)", 
                        value=False,
                        help="Berechnet den maximalen prozentualen Kurssturz vom Höchststand bis zum Tiefststand im gewählten Zeitraum. Ein Maß für das Verlustrisiko.",
                        key="show_drawdown_val"
                    )
                    col_idx += 1
                    
                    show_msci = lab_cols[col_idx].checkbox(
                        "🌍 MSCI World Index", 
                        value=False,
                        help="Vergleicht den Kursverlauf mit dem MSCI World Index – einer globalen Benchmark, die ~1.500 Unternehmen aus 23 Ländern abbildet. Aktiviert automatisch den prozentualen Modus.",
                        key="show_msci_val"
                    )
                    # Dynamic and clearer helper tips for technical indicators
                    if show_sma and show_bollinger:
                        st.caption("💡 **Tipp:** Die *Glättungslinie (SMA)* zeigt den langfristigen Trend, während der *Schwankungskanal* die typische Bandbreite der Kursbewegungen abbildet.")
                    elif show_sma:
                        st.caption("💡 **Tipp:** Die *Glättungslinie (SMA)* glättet tägliche Schwankungen, um den langfristigen Trend deutlicher zu machen.")
                    elif show_bollinger:
                        st.caption("💡 **Tipp:** Der *Schwankungskanal* veranschaulicht die normale Bandbreite, in der sich der Kurs meistens bewegt.")

                    chart_data = pd.DataFrame()
                    chart_data[name_1] = df_1_filtered['Close']

                    if show_sma:
                        chart_data[f"{name_1} (30-Tage SMA)"] = df_1_filtered['Close'].rolling(window=30).mean()
                    if show_bollinger and len(df_1_filtered) >= 20:
                        sma20 = df_1_filtered['Close'].rolling(window=20).mean()
                        std20 = df_1_filtered['Close'].rolling(window=20).std()
                        chart_data[f"{name_1} Oben (Kanal)"] = sma20 + (std20 * 2)
                        chart_data[f"{name_1} Unten (Kanal)"] = sma20 - (std20 * 2)
                    if not df_2_filtered.empty:
                        chart_data[name_2] = df_2_filtered['Close']
                    if show_msci and not df_msci_filtered.empty:
                        chart_data["MSCI World Index (Weltmarkt)"] = df_msci_filtered['Close']

                    if is_normalized_mode:
                        chart_data = (chart_data / chart_data.iloc[0] - 1) * 100

                    # Chart-Generierung mit Plotly um Dragging/Panning zu unterbinden
                    fig_line = go.Figure()
                    for col_name in chart_data.columns:
                        fig_line.add_trace(go.Scatter(
                            x=chart_data.index,
                            y=chart_data[col_name],
                            mode='lines',
                            name=col_name,
                            line=dict(width=2.5) 
                        ))
                    
                    fig_line.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(
                            showgrid=True,
                            gridcolor="rgba(148, 163, 184, 0.1)",
                            linecolor="rgba(148, 163, 184, 0.2)"
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor="rgba(148, 163, 184, 0.1)",
                            linecolor="rgba(148, 163, 184, 0.2)",
                            ticksuffix=" %" if is_normalized_mode else ""
                        ),
                        height=400,
                        margin=dict(l=10, r=10, t=10, b=10),
                        dragmode=False, # Verhindert jegliches Verschieben/Panning
                        hovermode='x unified',
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                            bgcolor="rgba(0,0,0,0)"
                        )
                    )

                    st.plotly_chart(fig_line, use_container_width=True, config={'displayModeBar': False})

                    if is_normalized_mode:
                        st.caption(
                            "⚠️ Hinweis: Die vertikale Achse zeigt automatisch die **prozentuale Entwicklung (%)** seit dem Startdatum an.")

                    if show_drawdown:
                        def calc_max_drawdown(df):
                            if df.empty:
                                return 0.0
                            roll_max = df['Close'].cummax()
                            return ((df['Close'] - roll_max) / roll_max).min() * 100

                        if not df_2_filtered.empty:
                            col_dd1, col_dd2 = st.columns(2)
                            with col_dd1:
                                st.info(f"📉 **Größter Einbruch ({name_1}):** `{calc_max_drawdown(df_1_filtered):.2f}%`")
                            with col_dd2:
                                st.info(f"📉 **Größter Einbruch ({name_2}):** `{calc_max_drawdown(df_2_filtered):.2f}%`")
                        else:
                            st.info(f"📉 **Größter Einbruch ({name_1}):** `{calc_max_drawdown(df_1_filtered):.2f}%`")

                else:
                    st.markdown(f"**Mustererkennung im Kerzenchart von {name_1}:**")
                    df_1_filtered = df_1_filtered.copy()
                    df_1_filtered['Body'] = abs(df_1_filtered['Open'] - df_1_filtered['Close'])
                    df_1_filtered['Range'] = df_1_filtered['High'] - df_1_filtered['Low']
                    df_1_filtered['Doji'] = (df_1_filtered['Body'] <= df_1_filtered['Range'] * 0.1) & (df_1_filtered['Range'] > 0)

                    df_1_filtered['Lower_Shadow'] = np.minimum(df_1_filtered['Open'], df_1_filtered['Close']) - df_1_filtered['Low']
                    df_1_filtered['Upper_Shadow'] = df_1_filtered['High'] - np.maximum(df_1_filtered['Open'], df_1_filtered['Close'])
                    df_1_filtered['Hammer'] = (df_1_filtered['Lower_Shadow'] >= df_1_filtered['Body'] * 2) & (
                                df_1_filtered['Upper_Shadow'] <= df_1_filtered['Body'] * 0.5) & (df_1_filtered['Body'] > 0)

                    fig_candle = go.Figure()
                    fig_candle.add_trace(go.Candlestick(
                        x=df_1_filtered.index, open=df_1_filtered['Open'], high=df_1_filtered['High'], low=df_1_filtered['Low'], close=df_1_filtered['Close'],
                        name=name_1, increasing_line_color='#2ecc71', decreasing_line_color='#e74c3c'
                    ))

                    doji_days = df_1_filtered[df_1_filtered['Doji']]
                    if not doji_days.empty:
                        fig_candle.add_trace(go.Scatter(x=doji_days.index, y=doji_days['High'] * 1.02, mode='markers',
                                                        marker=dict(symbol='star', size=10, color='gold'),
                                                        name='Doji (⚡ Unentschlossenheit)'))
                    hammer_days = df_1_filtered[df_1_filtered['Hammer']]
                    if not hammer_days.empty:
                        fig_candle.add_trace(
                            go.Scatter(x=hammer_days.index, y=hammer_days['Low'] * 0.98, mode='markers',
                                       marker=dict(symbol='triangle-up', size=10, color='cyan'),
                                       name='Hammer (🔨 Mögliche Trendwende)'))

                    fig_candle.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                                             xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_candle, use_container_width=True)

                st.markdown("---")
                with st.expander("📋 Technische Rohdaten einsehen"):
                    st.markdown(
                        "Hier findest du die unverarbeiteten mathematischen Tabellenreihen direkt aus der Programmierschnittstelle.")
                    st.write(f"**Tägliche Kursdaten für {name_1}:**")
                    st.dataframe(df_1_filtered, use_container_width=True)
                    if not df_2_filtered.empty:
                        st.write(f"**Tägliche Kursdaten für {name_2}:**")
                        st.dataframe(df_2_filtered, use_container_width=True)

            # --- TAB 3: FUNDAMENTAL-ANALYSE ---
            with tab3:
                st.subheader("🏢 Firmenprofil & Kennzahlen")
                f_cols = st.columns(2 if not df_2.empty else 1)

                st.markdown("""
<style>
.fund-card {
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-bottom: 10px;
    background: var(--secondary-background-color);
}
.fund-label {
    font-size: 0.75rem;
    color: var(--text-color);
    opacity: 0.65;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 4px;
}
.fund-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-color);
}
.fund-interp {
    font-size: 0.73rem;
    color: var(--text-color);
    opacity: 0.65;
    margin-top: 3px;
}
.fund-help {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: rgba(128,128,128,0.22);
    color: var(--text-color);
    font-size: 9px;
    font-weight: 700;
    cursor: pointer;
    flex-shrink: 0;
}
.fund-bar-tick {
    font-size: 0.72rem;
    color: var(--text-color);
    opacity: 0.55;
    white-space: nowrap;
}
.fund-bar-track {
    flex: 1;
    background: rgba(128,128,128,0.22);
    border-radius: 4px;
    height: 8px;
    position: relative;
}
.fund-bar-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-color);
}
</style>""", unsafe_allow_html=True)

                def _farbe(status):
                    return {"gruen": "#2ecc71", "gelb": "#f0b429", "rot": "#e74c3c"}.get(status, "#888")

                def _metric_card(col, label, value, interpretation, status, help_text=""):
                    farbe = _farbe(status)
                    icon = {"gruen": "🟢", "gelb": "🟡", "rot": "🔴"}.get(status, "⚪")
                    help_icon = (
                        f'<span class="fund-help" title="{help_text}">?</span>'
                    ) if help_text else ""
                    col.markdown(f"""
<div class="fund-card" style="border-left: 4px solid {farbe};">
    <div class="fund-label">{icon}&nbsp;{label}{help_icon}</div>
    <div class="fund-value">{value}</div>
    <div class="fund-interp">{interpretation}</div>
</div>""", unsafe_allow_html=True)

                def _52w_bar(col, current, low, high, currency):
                    if not (low and high and current and high > low):
                        return
                    pct = (current - low) / (high - low) * 100
                    pct_clamped = max(0, min(100, pct))
                    if pct_clamped < 30:
                        bar_color = "#e74c3c"
                        interpretation = "Nahe dem Jahrestief — möglicherweise günstig, aber prüfe die Gründe."
                        icon = "🔴"
                    elif pct_clamped > 75:
                        bar_color = "#2ecc71"
                        interpretation = "Nahe dem Jahreshoch — starke Kursdynamik, aber ggf. bereits teuer."
                        icon = "🟢"
                    else:
                        bar_color = "#f0b429"
                        interpretation = "Im mittleren Bereich des Jahres — weder besonders günstig noch teuer."
                        icon = "🟡"
                    help_52w = "Der aktuelle Kurs im Verhältnis zum 52-Wochen-Hoch und -Tief. Nah am Tief könnte auf eine günstige Einstiegsgelegenheit hindeuten, nah am Hoch auf starke Dynamik – aber auch höheres Einstiegsrisiko."
                    col.markdown(f"""
<div class="fund-card" style="border-left: 4px solid {bar_color};">
    <div class="fund-label">{icon}&nbsp;52-Wochen-Position<span class="fund-help" title="{help_52w}">?</span></div>
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
        <span class="fund-bar-tick">{low:.0f} {currency}</span>
        <div class="fund-bar-track">
            <div style="width:{pct_clamped:.1f}%; background:{bar_color}; height:100%; border-radius:4px;"></div>
            <div style="
                position:absolute;
                left:calc({pct_clamped:.1f}% - 6px);
                top:-4px;
                width:12px; height:16px;
                background:{bar_color};
                border-radius:3px;
                border:2px solid var(--background-color);
            "></div>
        </div>
        <span class="fund-bar-tick">{high:.0f} {currency}</span>
    </div>
    <div class="fund-bar-value">
        {current:.2f} {currency} <span style="font-size:0.8rem; color:{bar_color};">({pct_clamped:.0f}%)</span>
    </div>
    <div class="fund-interp">{interpretation}</div>
</div>""", unsafe_allow_html=True)

                def zeige_fundamentals_accessible(info, col, name):
                    col.markdown(f"### **{name}**")

                    sector = info.get('sector', '')
                    industry = info.get('industry', '')
                    if sector or industry:
                        col.caption(f"🏭 {sector}{' · ' + industry if industry else ''}")

                    col.markdown("---")

                    # --- Analystenempfehlung ---
                    rec = info.get('recommendationKey', '')
                    num_analysts = info.get('numberOfAnalystOpinions')
                    rec_map = {
                        'strong_buy':   ('gruen', 'Starker Kauf'),
                        'buy':          ('gruen', 'Kauf'),
                        'hold':         ('gelb',  'Halten'),
                        'underperform': ('rot',   'Unterperformance'),
                        'sell':         ('rot',   'Verkaufen'),
                        'strong_sell':  ('rot',   'Starker Verkauf'),
                    }
                    if rec and rec.lower() in rec_map:
                        rec_status, rec_label = rec_map[rec.lower()]
                    else:
                        rec_status, rec_label = 'gelb', 'Keine Empfehlung'
                    analyst_suffix = f" — {num_analysts} Analysten" if num_analysts else ""
                    interp_rec = {
                        'gruen': "Analysten erwarten mehrheitlich Kurssteigerungen.",
                        'gelb':  "Analysten empfehlen, die Position zu halten.",
                        'rot':   "Analysten erwarten mehrheitlich Kursverluste.",
                    }[rec_status]
                    _metric_card(col, f"Analystenempfehlung{analyst_suffix}", rec_label,
                                 interp_rec, rec_status,
                                 "Gebündelte Einschätzung professioneller Finanzanalysten.")

                    m1, m2 = col.columns(2)

                    # --- KGV ---
                    kgv = info.get('trailingPE')
                    if kgv:
                        kgv_txt = f"{kgv:.1f}x"
                        if kgv < 0:
                            kgv_status, kgv_interp = "rot", "Negativ — das Unternehmen schreibt Verluste."
                        elif kgv < 15:
                            kgv_status, kgv_interp = "gruen", f"Günstig — Anleger zahlen {kgv:.0f}€ je 1€ Gewinn."
                        elif kgv < 30:
                            kgv_status, kgv_interp = "gelb", f"Moderat — Anleger zahlen {kgv:.0f}€ je 1€ Gewinn."
                        else:
                            kgv_status, kgv_interp = "rot", f"Teuer — Anleger zahlen {kgv:.0f}€ je 1€ Gewinn."
                    else:
                        kgv_txt, kgv_status, kgv_interp = "N/A", "gelb", "Nicht verfügbar."
                    _metric_card(m1, "KGV (Bewertung)", kgv_txt, kgv_interp, kgv_status,
                                 "Kurs-Gewinn-Verhältnis: unter 15 = günstig, 15–30 = moderat, über 40 = teuer.")

                    # --- Dividende ---
                    div = info.get('dividendYield')
                    if div:
                        div_pct = div * 100
                        div_txt = f"{div_pct:.2f}%"
                        if div_pct >= 2.0:
                            div_status, div_interp = "gruen", f"Attraktive Ausschüttung von {div_pct:.2f}% p.a."
                        else:
                            div_status, div_interp = "gelb", f"Moderate Ausschüttung von {div_pct:.2f}% p.a."
                    else:
                        div_txt, div_status, div_interp = "0%", "gelb", "Keine Dividende — Gewinne werden reinvestiert."
                    _metric_card(m2, "Dividendenrendite", div_txt, div_interp, div_status,
                                 "Jährliche Gewinnausschüttung in % des Aktienkurses.")

                    m3, m4 = col.columns(2)

                    # --- EPS ---
                    eps = info.get('trailingEps')
                    currency = info.get('currency', 'USD')
                    if eps is not None:
                        eps_txt = f"{eps:.2f} {currency}"
                        if eps > 0:
                            eps_status, eps_interp = "gruen", f"Gewinnend — {eps:.2f} {currency} Gewinn je Aktie."
                        else:
                            eps_status, eps_interp = "rot", f"Verlustmachend — {eps:.2f} {currency} Verlust je Aktie."
                    else:
                        eps_txt, eps_status, eps_interp = "N/A", "gelb", "Nicht verfügbar."
                    _metric_card(m3, "Gewinn je Aktie (EPS)", eps_txt, eps_interp, eps_status,
                                 "Positiv = Gewinn, negativ = das Unternehmen schreibt Verluste.")

                    # --- Market Cap ---
                    cap = info.get('marketCap')
                    if cap:
                        if cap >= 1e12:
                            cap_txt = f"{cap / 1e12:.2f} Bio. {currency}"
                            cap_interp, cap_status = "Mega-Cap — eines der größten Unternehmen weltweit.", "gruen"
                        elif cap >= 10e9:
                            cap_txt = f"{cap / 1e9:.2f} Mrd. {currency}"
                            cap_interp, cap_status = "Large-Cap — stabiles Großunternehmen.", "gruen"
                        elif cap >= 2e9:
                            cap_txt = f"{cap / 1e9:.2f} Mrd. {currency}"
                            cap_interp, cap_status = "Mid-Cap — mittelgroßes Unternehmen.", "gelb"
                        else:
                            cap_txt = f"{cap / 1e9:.2f} Mrd. {currency}"
                            cap_interp, cap_status = "Small-Cap — kleines Unternehmen, höheres Risiko.", "rot"
                    else:
                        cap_txt, cap_status, cap_interp = "Unbekannt", "gelb", "Nicht verfügbar."
                    _metric_card(m4, "Börsenwert", cap_txt, cap_interp, cap_status,
                                 "<2 Mrd = Small Cap, 2–10 Mrd = Mid Cap, >10 Mrd = Large Cap.")

                    # --- 52-Wochen-Position ---
                    high_52 = info.get('fiftyTwoWeekHigh')
                    low_52 = info.get('fiftyTwoWeekLow')
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                    _52w_bar(col, current_price, low_52, high_52, currency)

                    # --- P/B ---
                    pb = info.get('priceToBook')
                    if pb is not None:
                        pb_txt = f"{pb:.2f}x"
                        if pb < 1.0:
                            pb_status, pb_interp = "gruen", "Unter Substanzwert — rechnerisch günstig."
                        elif pb < 4.0:
                            pb_status, pb_interp = "gelb", f"Moderates Aufgeld von {pb:.1f}x auf den Buchwert."
                        else:
                            pb_status, pb_interp = "rot", f"Hohes Aufgeld — Anleger zahlen {pb:.1f}x den Buchwert."
                    else:
                        pb_txt, pb_status, pb_interp = "N/A", "gelb", "Nicht verfügbar."
                    _metric_card(col, "Kurs-Buchwert (P/B)", pb_txt, pb_interp, pb_status,
                                 "Unter 1,0 = unter Substanzwert. Über 4 = teuer relativ zum Buchwert.")


                zeige_fundamentals_accessible(info_1, f_cols[0], name_1)
                if not df_2.empty:
                    zeige_fundamentals_accessible(info_2, f_cols[1], name_2)

            # --- TAB 4: RENDITE-RECHNER & MIXER ---
            with tab4:
                st.subheader("💰 Rendite-Rechner")

                time_period_rechner = st.segmented_control(
                    "Simulationszeitraum:",
                    options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                    default="1y",
                    format_func=lambda x: {
                        "1mo": "📅 1 Monat", "3mo": "📅 3 Monate", "6mo": "📅 6 Monate",
                        "1y": "📅 1 Jahr", "2y": "📅 2 Jahre", "5y": "📅 5 Jahre", "max": "⏳ Max"
                    }[x],
                    key="time_period_rechner"
                )

                df_1_filtered = filter_data_by_period(df_1, time_period_rechner)
                df_2_filtered = filter_data_by_period(df_2, time_period_rechner) if not df_2.empty else df_2

                if not df_2_filtered.empty:
                    st.markdown(
                        "Vergleiche die Wertentwicklung deiner Investments für beide ausgewählten Aktien über den gewählten Zeitraum.")

                    # Session state: link toggle (default: linked)
                    if "invest_linked" not in st.session_state:
                        st.session_state["invest_linked"] = True

                    col_inv1, col_link, col_inv2 = st.columns([5, 1, 5])

                    with col_inv1:
                        invest_sum_1 = st.number_input(
                            f"Investitionsbetrag für {name_1} (€):",
                            min_value=1,
                            value=st.session_state.get("invest_1", 1000),
                            step=100,
                            key="invest_1",
                            help="Gib den Betrag ein, den du zu Beginn des gewählten Zeitraums in diese Aktie investiert hättest."
                        )

                    # Link / Unlink icon — vertically centered between the two fields
                    with col_link:
                        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                        link_icon = "🔒" if st.session_state["invest_linked"] else "🔓"
                        link_help = "Beträge sind gekoppelt – klicken zum Trennen" if st.session_state["invest_linked"] else "Beträge sind getrennt – klicken zum Koppeln"
                        if st.button(link_icon, key="link_toggle", help=link_help, use_container_width=True):
                            st.session_state["invest_linked"] = not st.session_state["invest_linked"]
                            st.rerun()

                    with col_inv2:
                        if st.session_state["invest_linked"]:
                            # Force session state to mirror field 1 so the disabled widget auto-updates
                            st.session_state["invest_2"] = invest_sum_1
                            # Mirror field 1 — show as disabled
                            invest_sum_2 = st.number_input(
                                f"Investitionsbetrag für {name_2} (€):",
                                min_value=1,
                                value=invest_sum_1,
                                step=100,
                                key="invest_2",
                                disabled=True,
                                help="Gekoppelt mit dem linken Betrag. Trenne die Felder (🔓) um unterschiedliche Beträge einzugeben."
                            )
                            invest_sum_2 = invest_sum_1  # belt-and-suspenders sync
                        else:
                            invest_sum_2 = st.number_input(
                                f"Investitionsbetrag für {name_2} (€):",
                                min_value=1,
                                value=st.session_state.get("invest_2", invest_sum_1),
                                step=100,
                                key="invest_2",
                                help="Gib den Betrag ein, den du zu Beginn des gewählten Zeitraums in die Vergleichsaktie investiert hättest."
                            )

                    start_1, end_1 = df_1_filtered['Close'].iloc[0], df_1_filtered['Close'].iloc[-1]
                    end_val_1 = invest_sum_1 * (end_1 / start_1)
                    profit_1 = end_val_1 - invest_sum_1
                    perf_percent_1 = (end_val_1 / invest_sum_1 - 1) * 100

                    start_2, end_2 = df_2_filtered['Close'].iloc[0], df_2_filtered['Close'].iloc[-1]
                    end_val_2 = invest_sum_2 * (end_2 / start_2)
                    profit_2 = end_val_2 - invest_sum_2
                    perf_percent_2 = (end_val_2 / invest_sum_2 - 1) * 100

                    st.markdown("---")
                    mix_cols = st.columns(2)

                    with mix_cols[0]:
                        st.markdown(f"### **{name_1}**")
                        st.metric(label="Depot-Endwert nach Ablauf des Zeitraums", value=f"{end_val_1:.2f} €",
                                           delta=f"{'🔺 Gewinn:' if profit_1 >= 0 else '🔻 Verlust:'} {profit_1:.2f} € ({perf_percent_1:.2f}%)")

                    with mix_cols[1]:
                        st.markdown(f"### **{name_2}**")
                        st.metric(label="Depot-Endwert nach Ablauf des Zeitraums", value=f"{end_val_2:.2f} €",
                                           delta=f"{'🔺 Gewinn:' if profit_2 >= 0 else '🔻 Verlust:'} {profit_2:.2f} € ({perf_percent_2:.2f}%)")

                    st.markdown("---")
                    perf_diff = perf_percent_1 - perf_percent_2
                    if perf_diff > 0:
                        st.success(f"🏆 **{name_1}** hat in diesem Zeitraum um **{perf_diff:.2f} %** besser abgeschnitten als **{name_2}**.")
                    elif perf_diff < 0:
                        st.warning(f"📉 **{name_1}** hat in diesem Zeitraum um **{abs(perf_diff):.2f} %** schlechter abgeschnitten als **{name_2}**.")
                    else:
                        st.info(f"⚖️ Beide Aktien haben in diesem Zeitraum exakt die gleiche Wertentwicklung erzielt ({perf_percent_1:.2f} %).")

                    # Trajectory chart: Beide Depotwerte über Zeit
                    traj = pd.DataFrame({
                        f"Depot {name_1} (€)": (df_1_filtered['Close'] / df_1_filtered['Close'].iloc[0]) * invest_sum_1,
                        f"Depot {name_2} (€)": (df_2_filtered['Close'] / df_2_filtered['Close'].iloc[0]) * invest_sum_2,
                    })
                    st.line_chart(traj)
                    start_date_str = df_1_filtered.index[0].strftime("%d. %b %Y")
                    st.caption(f"📅 Simulation basiert auf historischen Kursdaten ab {start_date_str}. Vergangene Wertentwicklungen sind kein Indikator für zukünftige Ergebnisse.")
                else:
                    st.markdown(
                        "Berechne die Wertentwicklung deines Investments über den ausgewählten Zeitraum.")

                    col_invest, _ = st.columns([1, 7])
                    with col_invest:
                        invest_sum = st.number_input(
                            "Investitionsbetrag eingeben (€):", 
                            min_value=1, 
                            value=1000, 
                            step=100,
                            help="Gib den Betrag ein, den du zu Beginn des gewählten Zeitraums in die Aktie investiert hättest."
                        )

                    st.info(
                        "💡 Gib in der Seitenleiste ein zweites Vergleichsunternehmen ein, um den interaktiven Portfolio-Mixer freizuschalten.")
                    start_price = df_1_filtered['Close'].iloc[0]
                    end_price = df_1_filtered['Close'].iloc[-1]
                    end_wert = invest_sum * (end_price / start_price)
                    st.metric(label=f"Endwert deines Investments in {name_1}", value=f"{end_wert:.2f} €",
                              delta=f"{'🔺 Gewinn:' if (end_wert - invest_sum) >= 0 else '🔻 Verlust:'} {(end_wert - invest_sum):.2f} €")

                    # Trajectory chart: Simulierter Depotwert über Zeit
                    portfolio_series = (df_1_filtered['Close'] / start_price) * invest_sum
                    portfolio_series.name = f"Depotwert {name_1} (€)"
                    st.line_chart(portfolio_series)
                    start_date_str = df_1_filtered.index[0].strftime("%d. %b %Y")
                    st.caption(f"📅 Simulation basiert auf historischen Kursdaten ab {start_date_str}. Vergangene Wertentwicklungen sind kein Indikator für zukünftige Ergebnisse.")

            # --- TAB 5: NEWS & SCHLAGZEILEN ---
            with tab5:
                st.subheader("📰 Aktuelle Berichte & Markttreiber")

                # --- Filter bar: [Filter-Gruppe] | [Sortierung] ---
                filt_col1, filt_col2, filt_sep, filt_col3 = st.columns([4, 4, 0.4, 3])

                zeitraum_map = {
                    "Letzte 12 Stunden": 12,
                    "Letzte 24 Stunden": 24,
                    "Letzte 2 Tage": 48,
                    "Letzte 4 Tage": 96,
                    "Letzte Woche": 168,
                    "Letzter Monat": 720,
                }
                with filt_col1:
                    zeitraum_label = st.selectbox(
                        "🕐 Zeitraum",
                        options=list(zeitraum_map.keys()),
                        index=2,
                        key="news_zeitraum",
                        help="Filtert Artikel nach ihrem Veröffentlichungsdatum."
                    )
                    max_hours = zeitraum_map[zeitraum_label]

                with filt_col2:
                    anzahl_artikel = st.selectbox(
                        "📋 Anzahl Artikel",
                        options=[1, 2, 4, 6, 10],
                        index=2,
                        key="news_anzahl",
                        help="Maximale Anzahl der angezeigten Artikel pro Aktie."
                    )

                # Visual separator between filter group and sort
                with filt_sep:
                    st.markdown(
                        "<div style='height:62px; border-left:1px solid var(--text-color); opacity:0.15; margin:auto;'></div>",
                        unsafe_allow_html=True
                    )

                with filt_col3:
                    sortierung = st.selectbox(
                        "↕5 Sortierung",
                        options=["Neueste zuerst", "Älteste zuerst"],
                        index=0,
                        key="news_sort",
                        help="Reihenfolge der Artikel nach Veröffentlichungsdatum."
                    )

                # CSS for hover highlight on article cards
                st.markdown("""
<style>
.news-card-link {
    text-decoration: none !important;
    color: inherit !important;
    display: block;
    margin-bottom: 12px;
}
.news-card {
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-left: 4px solid var(--primary-color);
    background: var(--secondary-background-color);
    border-radius: 4px 8px 8px 4px;
    padding: 12px 14px;
    transition: all 0.2s ease-in-out;
    cursor: pointer;
}
.news-card-link:hover .news-card {
    border-color: var(--primary-color);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    background: color-mix(in srgb, var(--secondary-background-color) 92%, var(--primary-color) 8%);
    transform: translateY(-2px);
}
.news-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-color);
    line-height: 1.4;
    transition: color 0.2s ease-in-out;
}
.news-card-link:hover .news-title {
    color: var(--primary-color);
}
.news-card .news-meta {
    font-size: 0.72rem;
    color: var(--text-color);
    opacity: 0.55;
    margin-top: 6px;
}
</style>""", unsafe_allow_html=True)

                from datetime import datetime, timezone

                def _parse_article(art):
                    cb = art.get('content', {})
                    title = cb.get('title', art.get('title', 'Kein Titel verfügbar'))
                    link = cb.get('canonicalUrl', {}).get('url', art.get('link', '#'))
                    publisher = cb.get('provider', {}).get('displayName', art.get('publisher', 'Unbekannt'))
                    pub_ts = cb.get('pubDate') or art.get('providerPublishTime')
                    pub_dt = None
                    if pub_ts:
                        try:
                            if isinstance(pub_ts, (int, float)):
                                pub_dt = datetime.fromtimestamp(pub_ts, tz=timezone.utc)
                            else:
                                pub_dt = datetime.fromisoformat(str(pub_ts).replace("Z", "+00:00"))
                        except Exception:
                            pass
                    return {"title": title, "link": link, "publisher": publisher, "pub_dt": pub_dt}

                def _format_age(pub_dt, now):
                    if not pub_dt:
                        return ""
                    diff = now - pub_dt
                    hours = int(diff.total_seconds() // 3600)
                    if hours < 1:
                        return "vor weniger als einer Stunde"
                    elif hours < 24:
                        return f"vor {hours} Stunde{'n' if hours > 1 else ''}"
                    else:
                        days = diff.days
                        return f"vor {days} Tag{'en' if days > 1 else ''}" if days < 7 else pub_dt.strftime("%d. %b %Y")

                def _filter_sort(articles, max_hours, newest_first, limit, now, exclude_titles=None):
                    parsed = [_parse_article(a) for a in articles]
                    cutoff = now.timestamp() - max_hours * 3600
                    filtered = [
                        p for p in parsed
                        if p["pub_dt"] is None or p["pub_dt"].timestamp() >= cutoff
                    ]
                    if exclude_titles:
                        filtered = [p for p in filtered if p["title"] not in exclude_titles]
                    filtered.sort(
                        key=lambda p: p["pub_dt"].timestamp() if p["pub_dt"] else 0,
                        reverse=newest_first
                    )
                    return filtered[:limit]

                def _render_card(col, article, now):
                    title = article["title"]
                    link = article["link"]
                    publisher = article["publisher"]
                    age_str = _format_age(article["pub_dt"], now)
                    meta = f"📰 {publisher}" + (f"  ·  🕐 {age_str}" if age_str else "")
                    col.markdown(f"""
<a href="{link}" target="_blank" class="news-card-link">
    <div class="news-card">
        <div class="news-title">{title} ↗</div>
        <div class="news-meta">{meta}</div>
    </div>
</a>""", unsafe_allow_html=True)

                def zeige_news_clean(articles, col, name, max_hours, limit, newest_first, now, exclude_titles=None):
                    col.markdown(f"### Schlagzeilen zu **{name}**")
                    try:
                        if not articles:
                            col.info("Derzeit liegen keine aktuellen Meldungen vor.")
                            return set()
                        parsed = _filter_sort(articles, max_hours, newest_first, limit, now, exclude_titles)
                        if not parsed:
                            col.info(f"Keine Artikel im gewählten Zeitraum ({zeitraum_label}) gefunden.")
                            return set()
                        for art in parsed:
                            _render_card(col, art, now)
                        return {p["title"] for p in parsed}
                    except Exception:
                        col.info("Nachrichten-Schnittstelle temporär ausgelastet.")
                        return set()

                now_utc = datetime.now(timezone.utc)
                newest_first = (sortierung == "Neueste zuerst")
                news_cols = st.columns(2 if not df_2.empty else 1)

                news_1 = load_stock_news(ticker_input_1)
                titles_1 = zeige_news_clean(
                    news_1, news_cols[0], name_1,
                    max_hours, anzahl_artikel, newest_first, now_utc
                )
                if not df_2.empty:
                    news_2 = load_stock_news(ticker_input_2)
                    zeige_news_clean(
                        news_2, news_cols[1], name_2,
                        max_hours, anzahl_artikel, newest_first, now_utc,
                        exclude_titles=titles_1
                    )

        except Exception as e:
            st.error(f"⚠️ Beim Berechnen des Interfaces ist ein Fehler aufgetreten: {e}. Bitte lade die Seite neu.")