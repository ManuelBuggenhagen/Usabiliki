import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION & ACCESSIBLE STYLING ---
st.set_page_config(
    page_title="Finanz-Dashboard für Gelegenheitsanleger",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für exzellente Tab-Usability
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1200px; padding-top: 2rem; }
    h1 { font-weight: 800; color: #1e293b; letter-spacing: -0.025em; }
    h2, h3 { color: #334155; font-weight: 700; }

    /* Hauptcontainer für Tab-Liste */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; 
        overflow-x: auto !important; white-space: nowrap !important;
    }

    /* Einzelner Tab im Normalzustand */
    .stTabs [data-baseweb="tab"] { 
        background-color: #f1f5f9 !important; color: #475569 !important;
        border-radius: 6px 6px 0px 0px; padding: 10px 20px !important; 
        border: 1px solid #cbd5e1 !important; font-weight: 600 !important;
        display: inline-flex !important; white-space: nowrap !important;
    }

    /* Aktiver / Ausgewählter Tab */
    .stTabs [aria-selected="true"] { 
        background-color: #e0f2fe !important; color: #0369a1 !important; 
        border: 1px solid #7dd3fc !important; border-bottom: 4px solid #0284c7 !important; 
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Nutzerzentriertes Aktien- & Volatilitäts-Dashboard")
st.caption("Konzipiert für Gelegenheitsanleger zur intuitiven Analyse von Marktschwankungen.")

# --- DATENBANK FÜR DIE INTELLIGENTE FILTERUNG ---
STOCK_DATABASE = {
    "Apple Inc.": "AAPL",
    "NVIDIA Corporation": "NVDA",
    "Microsoft Corporation": "MSFT",
    "Tesla, Inc.": "TSLA",
    "Amazon.com, Inc.": "AMZN",
    "Alphabet Inc. (Google)": "GOOGL",
    "Meta Platforms, Inc. (Facebook)": "META",
    "Netflix, Inc.": "NFLX",
    "Advanced Micro Devices": "AMD",
    "Intel Corporation": "INTC",
    "SAP SE": "SAP",
    "Siemens AG": "SIE.DE",
    "Allianz SE": "ALV.DE"
}

# --- SIDEBAR (ECHTE AUTOCOMPLETE-SUCHE) ---
st.sidebar.header("⚙️ Aktien-Suche")

# 1. Hauptaktie Eingabefeld
search_query_1 = st.sidebar.text_input(
    "1. Hauptunternehmen suchen & tippen:",
    value=st.session_state.get('search_1', ''),
    placeholder="Name oder Kürzel eintippen...",
    help="Tippe z.B. 'Apple' oder 'AAPL'. Das System reagiert nur auf deine Eingabe."
)

ticker_input_1 = None
name_1 = ""

if search_query_1:
    # Filtert die Datenbank live anhand des Getippten
    matches_1 = [comp for comp in STOCK_DATABASE.keys() if
                 search_query_1.lower() in comp.lower() or STOCK_DATABASE[comp].lower() in search_query_1.lower()]

    if matches_1:
        st.sidebar.markdown("*Meintest du:*")
        # Zeigt nur Vorschläge passend zum Getippten als Klick-Buttons an
        for match in matches_1[:3]:
            if st.sidebar.button(f"🎯 {match}", key=f"btn_1_{match}"):
                st.session_state['selected_ticker_1'] = STOCK_DATABASE[match]
                st.session_state['selected_name_1'] = match

        if 'selected_ticker_1' in st.session_state:
            ticker_input_1 = st.session_state['selected_ticker_1']
            name_1 = st.session_state['selected_name_1']
    else:
        # Fallback: Wenn es nicht in der Liste ist, wird die Eingabe direkt als Ticker genommen + Enter-Bestätigung
        ticker_input_1 = search_query_1.upper().strip()
        name_1 = search_query_1.upper().strip()

# 2. Vergleichsaktie Eingabefeld
search_query_2 = st.sidebar.text_input(
    "2. Vergleichsunternehmen suchen (Optional):",
    value=st.session_state.get('search_2', ''),
    placeholder="Optional: Name oder Kürzel...",
    help="Tippe ein zweites Unternehmen ein, um einen direkten Performance-Vergleich zu starten."
)

ticker_input_2 = None
name_2 = ""

if search_query_2:
    matches_2 = [comp for comp in STOCK_DATABASE.keys() if
                 search_query_2.lower() in comp.lower() or STOCK_DATABASE[comp].lower() in search_query_2.lower()]
    if matches_2:
        st.sidebar.markdown("*Meintest du:*")
        for match in matches_2[:3]:
            if st.sidebar.button(f"🎯 {match}", key=f"btn_2_{match}"):
                st.session_state['selected_ticker_2'] = STOCK_DATABASE[match]
                st.session_state['selected_name_2'] = match

        if 'selected_ticker_2' in st.session_state:
            ticker_input_2 = st.session_state['selected_ticker_2']
            name_2 = st.session_state['selected_name_2']
    else:
        ticker_input_2 = search_query_2.upper().strip()
        name_2 = search_query_2.upper().strip()

st.sidebar.markdown("---")

time_period = st.sidebar.selectbox(
    "Betrachtungszeitraum:",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    index=3,
    format_func=lambda x: {
        "1mo": "📅 1 Monat", "3mo": "📅 3 Monate", "6mo": "📅 6 Monate",
        "1y": "📅 1 Jahr (Standard)", "2y": "📅 2 Jahre", "5y": "📅 5 Jahre", "max": "⏳ Maximale Historie"
    }[x]
)

# --- HAUPTFENSTER: PRÜFUNG AUF EMPTY STATE ---
if not ticker_input_1:
    st.markdown("### 👋 Willkommen im Volatilitäts-Dashboard")
    st.info(
        "💡 **Es ist noch kein Unternehmen ausgewählt.**\n\nBitte nutze das freie Suchfeld in der linken Seitenleiste und fange an zu tippen. Das Menü bleibt geschlossen und filtert sich **ausschließlich basierend auf deiner Eingabe**.")
    st.markdown("---")
    st.caption(
        "✨ **Einstiegs-Beispiel:** Tippe links einfach mal **'nv'** für Nvidia oder **'Apple'** ein und klicke auf den vorgeschlagenen Treffer.")

else:
    # --- DATENABRUF & REITER-GENERIERUNG BEI AKTIVER AUSWAHL ---
    with st.spinner("🚀 Marktdaten werden benutzerfreundlich aufbereitet..."):
        try:
            data_1 = yf.Ticker(ticker_input_1)
            df_1 = data_1.history(period=time_period)
            try:
                info_1 = data_1.info
            except:
                info_1 = {}

            # Falls yfinance einen besseren offiziellen Namen kennt, nutzen wir den
            name_1 = info_1.get('longName', name_1)

            try:
                msci_data = yf.Ticker("URTH")
                df_msci = msci_data.history(period=time_period)
            except:
                df_msci = pd.DataFrame()

            df_2 = pd.DataFrame()
            info_2 = {}
            if ticker_input_2:
                data_2 = yf.Ticker(ticker_input_2)
                df_2 = data_2.history(period=time_period)
                try:
                    info_2 = data_2.info
                except:
                    info_2 = {}
                name_2 = info_2.get('longName', name_2)

            # --- 1. PROMINENTE KPIs ---
            st.markdown(f"### 🔍 Aktueller Marktstatus ({name_1})")
            kpi_cols = st.columns(2 if not df_2.empty else 1)


            def rendere_saubere_kpis(df, name_lbl, info, col):
                if len(df) >= 2:
                    aktueller_kurs = df['Close'].iloc[-1]
                    vortag_kurs = df['Close'].iloc[-2]
                    differenz = aktueller_kurs - vortag_kurs
                    prozent = (differenz / vortag_kurs) * 100
                    waehrung = info.get('currency', 'USD')
                    richtungs_text = "🔺 Gewinn:" if differenz >= 0 else "🔻 Verlust:"

                    col.metric(
                        label=name_lbl,
                        value=f"{aktueller_kurs:.2f} {waehrung}",
                        delta=f"{richtungs_text} {differenz:.2f} {waehrung} ({prozent:.2f}%)"
                    )


            rendere_saubere_kpis(df_1, name_1, info_1, kpi_cols[0])
            if not df_2.empty:
                rendere_saubere_kpis(df_2, name_2, info_2, kpi_cols[1])

            st.markdown("---")

            # --- 2. TABS ---
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🔮 1. Anlage-Kompass",
                "📈 2. Kursverlauf & Labor",
                "🔬 3. Fundamental-Analyse",
                "💰 4. Rendite-Rechner & Mixer",
                "📰 5. Nachrichten-Feed"
            ])

            report_text = f"=== ANLAGE-REPORT ===\nZeitraum: {time_period}\n\n"

            # --- TAB 1: ANLAGE-KOMPASS ---
            with tab1:
                st.subheader("💡 Intuitive Entscheidungshilfe für Gelegenheitsanleger")
                kompass_cols = st.columns(2 if not df_2.empty else 1)


                def genere_radar(name_lbl, df, info, col, color_theme):
                    global report_text
                    current_price = df['Close'].iloc[-1]
                    sma_30 = df['Close'].rolling(window=30).mean().iloc[-1] if len(df) >= 30 else current_price
                    rec_key = info.get('recommendationKey', 'none').lower()

                    if "buy" in rec_key or current_price > (sma_30 * 1.03):
                        col.success(f"📈 **Kauf-Signal für {name_lbl}**")
                        signal_txt = "Kauf-Signal"
                    elif "sell" in rec_key or current_price < (sma_30 * 0.97):
                        col.error(f"📉 **Verkaufs-Signal für {name_lbl}**")
                        signal_txt = "Verkaufs-Signal"
                    else:
                        col.warning(f"↔️ **Halte-Signal für {name_lbl}**")
                        signal_txt = "Halte-Signal"

                    report_text += f"{name_lbl}: {signal_txt}\n"

                    kgv = info.get('trailingPE', 25)
                    kgv_score = 5 if kgv < 15 else (4 if kgv < 25 else (2 if kgv < 40 else 1))
                    div = info.get('dividendYield', 0)
                    div_score = 1 if div == 0 else (2 if div < 0.015 else (4 if div < 0.035 else 5))
                    beta = info.get('beta', 1.0)
                    beta_score = 5 if beta < 0.75 else (
                        4 if beta < 1.05 else (3 if beta < 1.35 else (2 if beta < 1.75 else 1)))
                    target = info.get('targetMeanPrice', current_price)
                    potential = ((target / current_price) - 1) * 100
                    pot_score = 5 if potential > 20 else (4 if potential > 8 else (3 if potential > 0 else 2))
                    trend_score = 5 if current_price > (sma_30 * 1.06) else (
                        4 if current_price > sma_30 else (3 if current_price > (sma_30 * 0.94) else 1))

                    categories = ['Günstiges KGV', 'Dividende', 'Kurs-Stabilität', 'Experten-Potenzial', 'Trend-Stärke']
                    values = [kgv_score, div_score, beta_score, pot_score, trend_score]
                    categories += [categories[0]]
                    values += [values[0]]

                    fig = go.Figure(
                        go.Scatterpolar(r=values, theta=categories, fill='toself', fillcolor=color_theme['fill'],
                                        line=dict(color=color_theme['line'])))
                    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False,
                                      height=250, margin=dict(l=20, r=20, t=20, b=20))
                    col.plotly_chart(fig, use_container_width=True)


                genere_radar(name_1, df_1, info_1, kompass_cols[0],
                             {'fill': 'rgba(59, 130, 246, 0.25)', 'line': '#3b82f6'})
                if not df_2.empty:
                    genere_radar(name_2, df_2, info_2, kompass_cols[1],
                                 {'fill': 'rgba(147, 51, 234, 0.25)', 'line': '#9333ea'})

            # --- TAB 2: KURSVERLAUF & LABOR ---
            with tab2:
                st.subheader("📈 Interaktiver Kursverlauf")
                if df_2.empty:
                    chart_view = st.radio("Modus:", ["Linie", "Kerzen (Candlestick)"], horizontal=True)
                else:
                    chart_view = "Linie"

                if chart_view == "Linie":
                    lab_cols = st.columns(4)
                    normalize = lab_cols[0].checkbox("📊 Prozentual (%)", value=True) if not df_2.empty else False
                    show_sma = lab_cols[1].checkbox("🔄 30-Tage SMA", value=True) if not normalize else False
                    show_bollinger = lab_cols[2].checkbox("🛡️ Bollinger Bänder",
                                                          value=False) if not normalize else False
                    show_msci = lab_cols[3].checkbox("🌍 MSCI World Index", value=False)

                    chart_data = pd.DataFrame()
                    chart_data[name_1] = df_1['Close']
                    if show_sma:
                        chart_data[f"{name_1} SMA"] = df_1['Close'].rolling(window=30).mean()
                    if not df_2.empty:
                        chart_data[name_2] = df_2['Close']
                    if show_msci and not df_msci.empty:
                        chart_data["MSCI World"] = df_msci['Close']

                    if normalize or show_msci:
                        chart_data = (chart_data / chart_data.iloc[0] - 1) * 100
                    st.line_chart(chart_data)
                else:
                    fig_candle = go.Figure(
                        go.Candlestick(x=df_1.index, open=df_1['Open'], high=df_1['High'], low=df_1['Low'],
                                       close=df_1['Close']))
                    fig_candle.update_layout(xaxis_rangeslider_visible=False, height=400)
                    st.plotly_chart(fig_candle, use_container_width=True)

                with st.expander("📋 Technische Rohdaten einsehen"):
                    st.dataframe(df_1, use_container_width=True)

            # --- TAB 3: FUNDAMENTAL-ANALYSE ---
            with tab3:
                st.subheader("🔬 Fundamentale Kennzahlen")
                f_cols = st.columns(2 if not df_2.empty else 1)
                f_cols[0].metric("KGV (Kurs-Gewinn-Verhältnis)", f"{info_1.get('trailingPE', 20.0):.2f}")
                if not df_2.empty:
                    f_cols[1].metric("KGV (Kurs-Gewinn-Verhältnis)", f"{info_2.get('trailingPE', 20.0):.2f}")

            # --- TAB 4: RENDITE-RECHNER ---
            with tab4:
                st.subheader("💰 Vermögens-Simulator")
                invest_sum = st.slider("Investitionsbetrag (€):", 100, 10000, 1000)
                start_p, end_p = df_1['Close'].iloc[0], df_1['Close'].iloc[-1]
                st.metric(f"Endwert für {name_1}", f"{(invest_sum * (end_p / start_p)):.2f} €")

            # --- TAB 5: NEWS ---
            with tab5:
                st.subheader("📰 Aktuelle Berichte")
                try:
                    for art in data_1.news[:3]:
                        st.markdown(f"🔗 **[{art['content']['title']}]({art['content']['canonicalUrl']['url']})**")
                except:
                    st.info("News-Schnittstelle ausgelastet.")

        except Exception as e:
            st.error(f"⚠️ Fehler beim Laden: {e}. Bitte überprüfe das Symbol.")