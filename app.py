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

    /* Einzelner Tab im Normalzustand (Inaktiv) */
    .stTabs [data-baseweb="tab"] { 
        background-color: #f1f5f9 !important; color: #475569 !important;
        border-radius: 6px 6px 0px 0px; padding: 10px 20px !important; 
        border: 1px solid #cbd5e1 !important; font-weight: 600 !important;
        display: inline-flex !important; white-space: nowrap !important;
        text-overflow: unset !important; overflow: visible !important;
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

# --- SIDEBAR (KLARNAME STATT TICKER-REFACTOR NACH NIELSEN) ---
st.sidebar.header("⚙️ Aktien-Auswahl")
st.sidebar.markdown("Wähle Unternehmen anhand ihres echten Namens aus. Kürzel wurden vollständig entfernt.")

# Vordefiniertes Wörterbuch beliebter Aktien (Verhindert Tippfehler komplett)
STOCK_OPTIONS = {
    "Apple Inc.": "AAPL",
    "NVIDIA Corporation": "NVDA",
    "Microsoft Corporation": "MSFT",
    "Tesla, Inc.": "TSLA",
    "Amazon.com, Inc.": "AMZN",
    "Alphabet Inc. (Google)": "GOOGL",
    "Meta Platforms, Inc. (Facebook)": "META",
    "Netflix, Inc.": "NFLX",
    "SAP SE": "SAP",
    "Siemens AG": "SIE.DE",
    "Allianz SE": "ALV.DE"
}

selected_company_1 = st.sidebar.selectbox(
    "1. Hauptunternehmen wählen:",
    options=list(STOCK_OPTIONS.keys()),
    index=0,
    help="Wähle das Unternehmen aus, dessen Kursschwankungen und Kennzahlen du im Detail analysieren möchtest."
)
ticker_input_1 = STOCK_OPTIONS[selected_company_1]

# Vorbereitung der Vergleichsliste mit einer leeren Option
COMPARE_OPTIONS = {"-- Kein Vergleich --": ""}
COMPARE_OPTIONS.update(STOCK_OPTIONS)

selected_company_2 = st.sidebar.selectbox(
    "2. Vergleichsunternehmen wählen (Optional):",
    options=list(COMPARE_OPTIONS.keys()),
    index=0,
    help="Wähle optional ein zweites Unternehmen aus, um ein vergleichendes Stärkenprofil und eine Gegenüberstellung zu aktivieren."
)
ticker_input_2 = COMPARE_OPTIONS[selected_company_2]

st.sidebar.markdown("---")

time_period = st.sidebar.selectbox(
    "Betrachtungszeitraum:",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
    index=3,
    format_func=lambda x: {
        "1mo": "📅 1 Monat", "3mo": "📅 3 Monate", "6mo": "📅 6 Monate",
        "1y": "📅 1 Jahr (Standard)", "2y": "📅 2 Jahre", "5y": "📅 5 Jahre", "max": "⏳ Maximale Historie"
    }[x],
    help="Bestimmt das Startdatum der historischen Zeitreihen."
)

# --- DATENABRUF ---
if ticker_input_1:
    with st.spinner("🚀 Marktdaten werden benutzerfreundlich aufbereitet..."):
        try:
            data_1 = yf.Ticker(ticker_input_1)
            df_1 = data_1.history(period=time_period)
            try:
                info_1 = data_1.info
            except:
                info_1 = {}

            try:
                msci_data = yf.Ticker("URTH")
                df_msci = msci_data.history(period=time_period)
            except:
                df_msci = pd.DataFrame()

            # Dynamische Namensauflösung für die restliche App
            name_1 = info_1.get('longName', selected_company_1)

            df_2 = pd.DataFrame()
            info_2 = {}
            name_2 = ""
            if ticker_input_2:
                data_2 = yf.Ticker(ticker_input_2)
                df_2 = data_2.history(period=time_period)
                try:
                    info_2 = data_2.info
                except:
                    info_2 = {}
                name_2 = info_2.get('longName', selected_company_2)

            # --- 1. PROMINENTE KPIs MIT KLARNAMEN ---
            st.markdown(f"### 🔍 Aktueller Marktstatus (Schlusskurse)")
            kpi_cols = st.columns(2 if not df_2.empty else 1)


            def rendere_saubere_kpis(df, name, info, col):
                if len(df) >= 2:
                    aktueller_kurs = df['Close'].iloc[-1]
                    vortag_kurs = df['Close'].iloc[-2]
                    differenz = aktueller_kurs - vortag_kurs
                    prozent = (differenz / vortag_kurs) * 100
                    waehrung = info.get('currency', 'USD')
                    richtungs_text = "🔺 Gewinn:" if differenz >= 0 else "🔻 Verlust:"

                    col.metric(
                        label=name,
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

            # --- TAB 1: ANLAGE-KOMPASS (KLARNAMEN IN CHART & TEXT) ---
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
                    kgv_score = 5 if not kgv or kgv < 15 else (4 if kgv < 25 else (2 if kgv < 40 else 1))
                    div = info.get('dividendYield', 0)
                    div_score = 1 if not div or div == 0 else (2 if div < 0.015 else (4 if div < 0.035 else 5))
                    beta = info.get('beta', 1.0)
                    beta_score = 5 if beta < 0.75 else (
                        4 if beta < 1.05 else (3 if beta < 1.35 else (2 if beta < 1.75 else 1)))

                    target = info.get('targetMeanPrice', current_price)
                    potential = ((target / current_price) - 1) * 100
                    pot_score = 5 if potential > 20 else (4 if potential > 8 else (3 if potential > 0 else 2))
                    trend_score = 5 if current_price > (sma_30 * 1.06) else (
                        4 if current_price > sma_30 else (3 if current_price > (sma_30 * 0.94) else 1))

                    categories = ['Günstige Bewertung (KGV)', 'Dividenden-Rendite', 'Kurs-Stabilität (Sicherheit)',
                                  'Analysten-Potenzial', 'Trend-Stärke (SMA)']
                    values = [kgv_score, div_score, beta_score, pot_score, trend_score]
                    categories += [categories[0]]
                    values += [values[0]]

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values, theta=categories, fill='toself',
                        fillcolor=color_theme['fill'], line=dict(color=color_theme['line'], width=2.5), name=name
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 5], tickvals=[1, 3, 5],
                                            ticktext=['Niedrig', 'Mittel', 'Hoch'],
                                            tickfont=dict(size=9, color="#64748b")),
                            angularaxis=dict(tickfont=dict(size=10, color="#1e293b"))
                        ),
                        showlegend=False, height=280, margin=dict(l=40, r=40, t=20, b=20)
                    )
                    col.plotly_chart(fig, use_container_width=True)

                    with col.expander("📝 Details zum Stärkenprofil einsehen"):
                        st.write(f"**Schwankungsrisiko (Beta):** `{beta:.2f}`")
                        if info.get('targetMeanPrice'):
                            st.write(
                                f"**Kursziel der Experten:** `{target:.2f}` {info.get('currency', 'USD')} (Potenzial: `{potential:.2f}%`).")


                theme_blue = {'fill': 'rgba(59, 130, 246, 0.25)', 'line': '#3b82f6'}
                theme_purple = {'fill': 'rgba(147, 51, 234, 0.25)', 'line': '#9333ea'}

                rendere_kompass_refactored(name_1, df_1, info_1,
                                           tab1.columns if hasattr(tab1, 'columns') else kompass_cols[0], theme_blue)
                if not df_2.empty:
                    rendere_kompass_refactored(name_2, df_2, info_2, kompass_cols[1], theme_purple)

                st.markdown("---")
                st.download_button(
                    label="📄 Diese Kurzanalyse als Text-Spickzettel herunterladen",
                    data=report_text,
                    file_name=f"Anlage_Zusammenfassung_{name_1.replace(' ', '_')}.txt",
                    mime="text/plain"
                )

            # --- TAB 2: KURSVERLAUF & LABOR (KLARNAMEN IN CHART-LEGENDEN) ---
            with tab2:
                st.subheader("📈 Interaktiver Kursverlauf")

                if df_2.empty:
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

                    num_cols = 5 if not df_2.empty else 4
                    lab_cols = st.columns(num_cols)

                    col_idx = 0
                    normalize = False

                    if not df_2.empty:
                        normalize = lab_cols[col_idx].checkbox("📊 Prozentualer Vergleich (%)", value=True)
                        col_idx += 1

                    show_sma = lab_cols[col_idx].checkbox("🔄 30-Tage Durchschnitt",
                                                          value=True) if not normalize else False
                    col_idx += 1
                    show_bollinger = lab_cols[col_idx].checkbox("🛡️ Bollinger Bänder",
                                                                value=False) if not normalize else False
                    col_idx += 1
                    show_drawdown = lab_cols[col_idx].checkbox("📉 Maximaler Verlust", value=False)
                    col_idx += 1
                    show_msci = lab_cols[col_idx].checkbox("🌍 MSCI World Index", value=False)

                    chart_data = pd.DataFrame()
                    chart_data[name_1] = df_1['Close']

                    if show_sma:
                        chart_data[f"{name_1} (30-Tage SMA)"] = df_1['Close'].rolling(window=30).mean()
                    if show_bollinger and len(df_1) >= 20:
                        sma20 = df_1['Close'].rolling(window=20).mean()
                        std20 = df_1['Close'].rolling(window=20).std()
                        chart_data[f"{name_1} Oben (Kanal)"] = sma20 + (std20 * 2)
                        chart_data[f"{name_1} Unten (Kanal)"] = sma20 - (std20 * 2)
                    if not df_2.empty:
                        chart_data[name_2] = df_2['Close']
                    if show_msci and not df_msci.empty:
                        chart_data["MSCI World Index (Weltmarkt)"] = df_msci['Close']

                    if normalize or show_msci:
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
                            f"📉 **Maximaler Verlust im gewählten Zeitraum ({name_1}):** `{calc_max_drawdown(df_1):.2f}%`")

                else:
                    st.markdown(f"**Mustererkennung im Kerzenchart von {name_1}:**")
                    df_1['Body'] = abs(df_1['Open'] - df_1['Close'])
                    df_1['Range'] = df_1['High'] - df_1['Low']
                    df_1['Doji'] = (df_1['Body'] <= df_1['Range'] * 0.1) & (df_1['Range'] > 0)

                    df_1['Lower_Shadow'] = np.minimum(df_1['Open'], df_1['Close']) - df_1['Low']
                    df_1['Upper_Shadow'] = df_1['High'] - np.maximum(df_1['Open'], df_1['Close'])
                    df_1['Hammer'] = (df_1['Lower_Shadow'] >= df_1['Body'] * 2) & (
                                df_1['Upper_Shadow'] <= df_1['Body'] * 0.5) & (df_1['Body'] > 0)

                    fig_candle = go.Figure()
                    fig_candle.add_trace(go.Candlestick(
                        x=df_1.index, open=df_1['Open'], high=df_1['High'], low=df_1['Low'], close=df_1['Close'],
                        name=name_1, increasing_line_color='#2ecc71', decreasing_line_color='#e74c3c'
                    ))

                    doji_days = df_1[df_1['Doji']]
                    if not doji_days.empty:
                        fig_candle.add_trace(go.Scatter(x=doji_days.index, y=doji_days['High'] * 1.02, mode='markers',
                                                        marker=dict(symbol='star', size=10, color='gold'),
                                                        name='Doji (⚡ Unentschlossenheit)'))
                    hammer_days = df_1[df_1['Hammer']]
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
                    st.dataframe(df_1, use_container_width=True)
                    if not df_2.empty:
                        st.write(f"**Tägliche Kursdaten für {name_2}:**")
                        st.dataframe(df_2, use_container_width=True)

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
                st.subheader("💰 Vermögens-Simulator & Portfolio-Mischer")
                st.markdown(
                    "Bewege die Regler, um spielerisch zu lernen, wie Diversifikation (Risikostreuung) die Stabilität deines Ersparten erhöht.")

                invest_sum = st.slider("Investitionsbetrag wählen (€):", min_value=100, max_value=10000, value=1000,
                                       step=100)

                if not df_2.empty:
                    weight_1 = st.slider(f"Gewichtung von {name_1} im Depot (%)", 0, 100, 50, 5)
                    weight_2 = 100 - weight_1
                    st.caption(f"Daraus ergibt sich automatisch eine Gewichtung von **{weight_2}%** für **{name_2}**.")

                    start_1, end_1 = df_1['Close'].iloc[0], df_1['Close'].iloc[-1]
                    end_val_1 = (invest_sum * (weight_1 / 100)) * (end_1 / start_1)
                    start_2, end_2 = df_2['Close'].iloc[0], df_2['Close'].iloc[-1]
                    end_val_2 = (invest_sum * (weight_2 / 100)) * (end_2 / start_2)

                    total_end_val = end_val_1 + end_val_2
                    total_profit = total_end_val - invest_sum
                    total_perf_percent = (total_end_val / invest_sum - 1) * 100

                    beta_1 = info_1.get('beta', 1.0)
                    beta_2 = info_2.get('beta', 1.0)
                    combined_beta = (weight_1 / 100) * beta_1 + (weight_2 / 100) * beta_2

                    st.markdown("---")
                    mix_cols = st.columns(2)

                    mix_cols[0].metric(label="Depot-Endwert nach Ablauf des Zeitraums", value=f"{total_end_val:.2f} €",
                                       delta=f"{'🔺 Gewinn:' if total_profit >= 0 else '🔻 Verlust:'} {total_profit:.2f} € ({total_perf_percent:.2f}%)")

                    if combined_beta > 1.3:
                        status_mix = "🔥 Stark schwankend (Höheres Risiko)"
                    elif combined_beta < 0.8:
                        status_mix = "🛡️ Sehr wertstabil (Konservativ)"
                    else:
                        status_mix = "⚖️ Ausgewogenes Marktrisiko"

                    mix_cols[1].metric(label="Kombiniertes Depot-Risiko (Beta)", value=f"{combined_beta:.2f}",
                                       delta=status_mix, delta_color="off")
                else:
                    st.info(
                        "💡 Gib in der Seitenleiste ein zweites Vergleichsunternehmen ein, um den interaktiven Portfolio-Mixer freizuschalten.")
                    start_price = df_1['Close'].iloc[0]
                    end_price = df_1['Close'].iloc[-1]
                    end_wert = invest_sum * (end_price / start_price)
                    st.metric(label=f"Endwert deines Investments in {name_1}", value=f"{end_wert:.2f} €",
                              delta=f"{'🔺 Gewinn:' if (end_wert - invest_sum) >= 0 else '🔻 Verlust:'} {(end_wert - invest_sum):.2f} €")

            # --- TAB 5: NEWS & SCHLAGZEILEN ---
            with tab5:
                st.subheader("📰 Aktuelle Berichte & Markttreiber")
                news_cols = st.columns(2 if not df_2.empty else 1)


                def zeige_news_clean(data, col, name):
                    col.markdown(f"### Schlagzeilen zu **{name}**")
                    try:
                        articles = getattr(data, 'news', [])
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


                zeige_news_clean(data_1, news_cols[0], name_1)
                if not df_2.empty:
                    zeige_news_clean(data_2, news_cols[1], name_2)

        except Exception as e:
            st.error(f"⚠️ Beim Berechnen des Interfaces ist ein Fehler aufgetreten: {e}. Bitte lade die Seite neu.")