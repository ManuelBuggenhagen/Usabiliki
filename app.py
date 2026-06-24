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


def set_selected_stock(select_key):
    st.session_state["selected_option_1"] = select_key
    st.session_state["use_custom_ticker_1"] = False

def handle_custom_search():
    val = st.session_state.get("landing_search_input_val", "").upper().strip()
    if val:
        st.session_state["use_custom_ticker_1"] = True
        st.session_state["custom_ticker_input_1"] = val


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

    /* Farbcodierung für spezielle Metriken (Verhindert vertikale Offsets in Spalten) */
    div.third-metric-green div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] {
        color: #2ecc71 !important;
    }
    div.third-metric-red div[data-testid="column"]:nth-of-type(3) [data-testid="stMetricValue"] {
        color: #e74c3c !important;
    }

    /* Hauptcontainer für Tab-Liste */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; 
        overflow-x: auto !important; white-space: nowrap !important;
    }

    /* Einzelner Tab im Normalzustand (Inaktiv) */
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(148, 163, 184, 0.08) !important; color: #475569 !important;
        border-radius: 6px 6px 0px 0px; padding: 10px 20px !important; 
        border: 1px solid rgba(148, 163, 184, 0.2) !important; font-weight: 600 !important;
        display: inline-flex !important; white-space: nowrap !important;
        text-overflow: unset !important; overflow: visible !important;
    }

    /* Aktiver / Ausgewählter Tab */
    .stTabs [aria-selected="true"] { 
        background-color: rgba(14, 165, 233, 0.12) !important; color: #0284c7 !important; 
        border: 1px solid rgba(14, 165, 233, 0.4) !important; border-bottom: 4px solid #0284c7 !important; 
        font-weight: 700 !important;
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
        color: #334155;
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
#changed stuff here
#and here as well
ticker_input_1 = None
selected_option_1 = None
custom_ticker_input_1 = ""

if use_custom_ticker_1:
    custom_ticker_input_1 = st.sidebar.text_input(
        "✍️ Ticker-Symbol eingeben:",
        value=st.session_state.get("custom_ticker_input_1", ""),
        max_chars=10,
        help="Gib hier ein beliebiges Ticker-Symbol ein (z. B. 'MSFT' für Microsoft oder 'SAP.DE' für SAP).",
        key="custom_ticker_input_1"
    ).upper().strip()
    ticker_input_1 = custom_ticker_input_1 if custom_ticker_input_1 else None
else:
    selected_option_1 = st.sidebar.selectbox(
        "1. Top Aktien auf einen Blick:",
        options=[k for k in STOCK_OPTIONS.keys() if STOCK_OPTIONS[k] != "CUSTOM"],
        index=None,
        placeholder="Wähle eine Aktie...",
        help="Wähle ein beliebtes Unternehmen aus der Liste.",
        key="selected_option_1"
    )
    if selected_option_1:
        ticker_input_1 = STOCK_OPTIONS[selected_option_1]

st.sidebar.markdown("---")

# Checkbox für Vergleich aktivieren
compare_stock = st.sidebar.checkbox("⚖️ Aktie vergleichen", value=False, help="Aktiviere diese Option, um ein zweites Unternehmen für den direkten Vergleich hinzuzufügen.")

ticker_input_2 = None
selected_option_2 = None
custom_ticker_input_2 = ""

if compare_stock:
    # Abstand vergrößern und Überschrift anzeigen
    st.sidebar.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.sidebar.subheader("⚖️ Vergleichsaktie")

    # Toggle für Eingabe-Modus der Vergleichsaktie
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
            "2. Top Aktien auf einen Blick:",
            options=[k for k in STOCK_OPTIONS.keys() if STOCK_OPTIONS[k] != "CUSTOM"],
            index=None,
            placeholder="Wähle eine Vergleichsaktie...",
            help="Wähle ein beliebtes Vergleichsunternehmen aus der Liste.",
            key="select_comp"
        )
        if selected_option_2:
            ticker_input_2 = STOCK_OPTIONS[selected_option_2]

# --- HAUPTFENSTER: PRÜFUNG AUF LEEREN ZUSTAND (EMPTY STATE UX) ---
if not ticker_input_1:
    st.title("📊  Stockguide: Dein persöhnliches Aktiendashboard")
    st.caption("Konzipiert für Gelegenheitsanleger zur intuitiven Analyse des Marktes.")
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 12px; margin-bottom: 25px; border: 1px solid #334155; color: white;">
            <h2 style="color: white; margin-top: 0px;">📊 Willkommen bei Stockguide</h2>
            <p style="font-size: 16px; color: #cbd5e1; line-height: 1.6; margin-bottom: 0px;">
                Dein persönliches Aktiendashboard zur schnellen und verständlichen Marktanalyse. Speziell konzipiert für Gelegenheitsanleger, um wichtige Finanzdaten übersichtlich und intuitiv darzustellen.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Schnelleinstieg: Wähle eine beliebte Aktie")
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
    
    # Zusätzliche freie Suche auf der Landingpage zur Verringerung der Gulf of Execution
    st.markdown("### ✍️ Oder suche direkt nach einem Ticker-Symbol")
    
    st.text_input(
        "Gib ein globales Kürzel ein (z. B. 'MSFT' für Microsoft, 'SIE.DE' für Siemens):",
        value="",
        placeholder="z. B. AAPL, SAP.DE, MSFT...",
        key="landing_search_input_val",
        on_change=handle_custom_search
    )

else:
    st.title("📊  Stockguide")
    st.caption("Konzipiert für Gelegenheitsanleger zur intuitiven Analyse des Marktes.")
    # --- DATENABRUF & VERARBEITUNG BEI AKTIVER AUSWAHL ---
    with st.spinner("🚀 Marktdaten werden aufbereitet..."):
        try:
            # 1. Hauptaktie laden
            df_1, info_1 = load_stock_data(ticker_input_1)

            # Validierung der Hauptaktie zur Fehlervermeidung (Postel's Law / Nielsen Heuristik #5)
            if df_1.empty:
                st.error(f"⚠️ **Das Ticker-Symbol '{ticker_input_1}' konnte nicht geladen werden.**\n\nBitte überprüfe die Schreibweise in der Seitenleiste (z. B. 'AAPL' für Apple, 'NVDA' für NVIDIA oder 'SAP.DE' für SAP SE) und stelle sicher, dass eine Internetverbindung besteht.")
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
                "🔮 1. Anlage-Kompass",
                "📈 2. Kursverlauf",
                "🔬 3. Fundamental-Analyse",
                "💰 4. Rendite-Rechner",
                "📰 5. Nachrichten-Feed"
            ])

            report_text = f"=== ANLAGE-REPORT ===\nStand: Aktuell\n\n"

            # --- TAB 1: ANLAGE-KOMPASS ---
            with tab1:
                st.subheader("💡 Intuitive Entscheidungshilfe für Gelegenheitsanleger")
                st.markdown(
                    "Dieses Profil übersetzt komplexe Kennzahlen in ein geometrisches Stärkenprofil. Je größer die ausgefüllte Fläche, desto ausgeprägter ist diese Eigenschaft.")

                kompass_cols = st.columns(2 if not df_2.empty else 1)


                def rendere_kompass_refactored(name, df, info, col, color_theme):
                    global report_text
                    col.markdown(f"### **{name} Profil-Analyse**")
                    current_price = df['Close'].iloc[-1]
                    sma_30 = df['Close'].rolling(window=30).mean().iloc[-1] if len(df) >= 30 else current_price
                    rec_key = info.get('recommendationKey', 'none').lower()

                    if "buy" in rec_key or current_price > (sma_30 * 1.03):
                        col.success(
                            "📈 **Kauf-Signal / Nachkaufen** — Das Unternehmen befindet sich in einem stabilen Aufwärtstrend.")
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

                    categories = ['KGV (Bewertung)', 'Dividendenrendite', 'Kurs-Stabilität',
                                  'Analysten-Potenzial', 'Trend-Stärke']
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
                    col.markdown("""
                        <div style="font-size: 13px; color: #64748b; text-align: center; margin-top: -10px; margin-bottom: 20px;">
                            <i>Skala: 1 = Gering/Ungünstig | 3 = Neutral/Mittel | 5 = Hoch/Günstig</i>
                        </div>
                    """, unsafe_allow_html=True)

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
                            st.metric(
                                label="Schwankungsrisiko (Beta)",
                                value=f"{beta:.2f}",
                                help="Das Beta misst, wie stark die Aktie im Vergleich zum Gesamtmarkt schwankt.\n\n• Beta > 1.0: Stärkere Schwankungen (höheres Risiko)\n• Beta = 1.0: Gleiche Schwankungen wie der Markt\n• Beta < 1.0: Ruhigere Kursbewegungen (weniger Risiko)"
                            )
                        if target_price:
                            currency = info.get('currency', 'USD')
                            with col_d2:
                                st.metric(
                                    label="Kursziel der Experten",
                                    value=f"{target:.2f} {currency}",
                                    help="Das von professionellen Finanzanalysten geschätzte durchschnittliche Kursziel der Aktie für die nächsten 12 Monate."
                                )
                            with col_d3:
                                st.metric(
                                    label="Analysten-Potenzial",
                                    value=f"{potential:+.2f}%",
                                    help="Die prozentuale Differenz zwischen dem aktuellen Kurs und dem Experten-Kursziel.\n\n• Positiver Wert: Analysten erwarten Kurssteigerungen\n• Negativer Wert: Analysten erwarten Kursrückgänge"
                                )
                            st.markdown('</div>', unsafe_allow_html=True)


                theme_blue = {'fill': 'rgba(59, 130, 246, 0.25)', 'line': '#3b82f6'}
                theme_purple = {'fill': 'rgba(147, 51, 234, 0.25)', 'line': '#9333ea'}

                rendere_kompass_refactored(name_1, df_1, info_1, kompass_cols[0], theme_blue)
                if not df_2.empty:
                    rendere_kompass_refactored(name_2, df_2, info_2, kompass_cols[1], theme_purple)

                st.markdown("---")
                st.download_button(
                    label="📄 Diese Kurzanalyse als Text-Spickzettel herunterladen",
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
                df_2_filtered = filter_data_by_period(df_2, time_period_chart) if not df_2.empty else df_2
                df_msci_filtered = filter_data_by_period(df_msci, time_period_chart) if not df_msci.empty else df_msci

                if df_2_filtered.empty:
                    chart_view = st.radio(
                        "Visualisierungs-Modus wählen:",
                        options=["Einfache Linie (Einsteiger-UX)",
                                 "Kerzenchart / Candlestick (Fortgeschrittene Analyse)"],
                        horizontal=True
                    )
                else:
                    chart_view = "Einfache Linie (Einsteiger-UX)"
                    st.info(
                        "ℹ️ Bei aktiven Vergleichen ist der Linienmodus fest vorgegeben, um eine optische Überlagerung zu verhindern.")

                if chart_view == "Einfache Linie (Einsteiger-UX)":
                    st.markdown("**🔍 Optionale Filter & Zusatzlinien zuschalten:**")

                    num_cols = 5 if not df_2_filtered.empty else 4
                    lab_cols = st.columns(num_cols)

                    col_idx = 0
                    normalize = False

                    if not df_2_filtered.empty:
                        normalize = lab_cols[col_idx].checkbox(
                            "📊 Prozentualer Vergleich (%)", 
                            value=True,
                            help="Aktiviert den relativen Prozentvergleich, um die Wertentwicklung beider Aktien direkt vergleichen zu können.",
                            key="normalize_val"
                        )
                        col_idx += 1

                    # Wenn MSCI World oder Prozentvergleich aktiv ist, erzwingen wir prozentuale Skalierung.
                    is_normalized_mode = normalize

                    # Prüfen wir, ob MSCI Index ausgewählt werden soll (dieser muss später im Code erfasst werden)
                    # Da show_msci weiter unten definiert ist, lesen wir es aus st.session_state, falls vorhanden:
                    show_msci_active = st.session_state.get("show_msci_val", False)
                    if show_msci_active:
                        is_normalized_mode = True

                    show_sma = lab_cols[col_idx].checkbox(
                        "🔄 30-Tage Durchschnitt",
                        value=True if not is_normalized_mode else False,
                        disabled=is_normalized_mode,
                        help="Zeigt den gleitenden 30-Tage-Durchschnitt des Aktienkurses. (Deaktiviert bei prozentualem Vergleich).",
                        key="show_sma_val"
                    )
                    col_idx += 1
                    
                    show_bollinger = lab_cols[col_idx].checkbox(
                        "🛡️ Bollinger Bänder",
                        value=False if not is_normalized_mode else False,
                        disabled=is_normalized_mode,
                        help="Zeigt das statistische Band um den gleitenden Durchschnitt. Hilft bei der Einschätzung der Schwankungsbreite. (Deaktiviert bei prozentualem Vergleich).",
                        key="show_bollinger_val"
                    )
                    col_idx += 1
                    
                    show_drawdown = lab_cols[col_idx].checkbox(
                        "📉 Maximaler Verlust", 
                        value=False,
                        help="Berechnet und zeigt den maximalen prozentualen Kurssturz (Drawdown) im gewählten Zeitraum an.",
                        key="show_drawdown_val"
                    )
                    col_idx += 1
                    
                    show_msci = lab_cols[col_idx].checkbox(
                        "🌍 MSCI World Index", 
                        value=False,
                        help="Vergleicht den Kursverlauf mit dem MSCI World Index (Globale Benchmark für Aktien). Aktiviert automatisch den prozentualen Modus.",
                        key="show_msci_val"
                    )

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
                        st.line_chart(chart_data)
                        st.caption(
                            "⚠️ System-Hinweis: Die vertikale Achse zeigt automatisch die **prozentuale Entwicklung (%)** seit dem Startdatum an.")
                    else:
                        st.line_chart(chart_data)

                    if show_drawdown:
                        def calc_max_drawdown(df):
                            roll_max = df['Close'].cummax()
                            return ((df['Close'] - roll_max) / roll_max).min() * 100


                        st.info(
                            f"📉 **Maximaler Verlust im gewählten Zeitraum ({name_1}):** `{calc_max_drawdown(df_1_filtered):.2f}%`")

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
                st.subheader("🔬 Fundamentale Firmenkennzahlen")
                st.markdown(
                    "Fahre mit der Maus über die kleinen Fragezeichen, um eine einfache Erklärung der Fachbegriffe zu erhalten.")
                f_cols = st.columns(2 if not df_2.empty else 1)


                def zeige_fundamentals_accessible(info, col, name):
                    col.markdown(f"### **{name}**")
                    kgv = info.get('trailingPE')
                    kgv_txt = f"{kgv:.2f}" if kgv else "Nicht verfügbar"
                    col.metric(label="KGV (Kurs-Gewinn-Verhältnis)", value=kgv_txt,
                               help="Das KGV sagt aus, wie viele Jahre es theoretisch dauert, bis das Unternehmen seinen eigenen Kaufpreis durch Gewinne wieder eingespielt hat. Ein Wert unter 20 gilt oft als günstig.")

                    div = info.get('dividendYield')
                    div_txt = f"{(div * 100):.2f} %" if div else "0.00 %"
                    col.metric(label="Dividendenrendite (Zinsertrag)", value=div_txt,
                               help="Die jährliche 'Bonus-Ausschüttung' der Firma an ihre Aktionäre, umgerechnet in Prozent des aktuellen Aktienkurses.")

                    cap = info.get('marketCap')
                    cap_txt = f"{cap / 1e9:.2f} Mrd. {info.get('currency', 'USD')}" if cap else "Unbekannt"
                    col.write(f"**Börsenwert des gesamten Unternehmens (Market Cap):** {cap_txt}")


                zeige_fundamentals_accessible(info_1, f_cols[0], name_1)
                if not df_2.empty:
                    zeige_fundamentals_accessible(info_2, f_cols[1], name_2)

            # --- TAB 4: RENDITE-RECHNER & MIXER ---
            with tab4:
                st.subheader("💰 Vermögens-Simulator")

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

                    col_inv1, col_inv2 = st.columns(2)
                    with col_inv1:
                        invest_sum_1 = st.number_input(
                            f"Investitionsbetrag für {name_1} (€):", 
                            min_value=1, 
                            value=1000, 
                            step=100, 
                            key="invest_1",
                            help="Gib den Betrag ein, den du zu Beginn des gewählten Zeitraums in diese Aktie investiert hättest."
                        )
                    with col_inv2:
                        invest_sum_2 = st.number_input(
                            f"Investitionsbetrag für {name_2} (€):", 
                            min_value=1, 
                            value=1000, 
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

            # --- TAB 5: NEWS & SCHLAGZEILEN ---
            with tab5:
                st.subheader("📰 Aktuelle Berichte & Markttreiber")
                news_cols = st.columns(2 if not df_2.empty else 1)


                def zeige_news_clean(articles, col, name):
                    col.markdown(f"### Schlagzeilen zu **{name}**")
                    try:
                        if not articles:
                            col.info("Derzeit liegen keine aktuellen Meldungen vor.")
                            return
                        for art in articles[:4]:
                            content_block = art.get('content', {})
                            title = content_block.get('title', art.get('title', 'Kein Titel verfügbar'))
                            link = content_block.get('canonicalUrl', {}).get('url', art.get('link', '#'))
                            publisher = content_block.get('provider', {}).get('displayName',
                                                                              art.get('publisher', 'Unbekannt'))

                            col.markdown(f"🔗 **[{title}]({link})**")
                            col.caption(f"Quelle: {publisher}")
                            col.markdown("---")
                    except:
                        col.info("Nachrichten-Schnittstelle temporär ausgelastet.")


                news_1 = load_stock_news(ticker_input_1)
                zeige_news_clean(news_1, news_cols[0], name_1)
                if not df_2.empty:
                    news_2 = load_stock_news(ticker_input_2)
                    zeige_news_clean(news_2, news_cols[1], name_2)

        except Exception as e:
            st.error(f"⚠️ Beim Berechnen des Interfaces ist ein Fehler aufgetreten: {e}. Bitte lade die Seite neu.")