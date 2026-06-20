import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go  # NEU: Für das Tachometer-Diagramm

# Konfiguration der Seite
st.set_page_config(page_title="Premium Aktien- & Volatilitäts-Dashboard", layout="wide")
st.title("🚀 Professionelles Aktien- & Volatilitäts-Dashboard")

# --- EINSTELLUNGEN (SIDEBAR) ---
st.sidebar.header("⚙️ Einstellungen")

ticker_input_1 = st.sidebar.text_input("1. Aktien-Ticker (Hauptaktie):", "AAPL").upper()
ticker_input_2 = st.sidebar.text_input("2. Aktien-Ticker (Vergleich - Optional):", "").upper()

time_period = st.sidebar.selectbox(
    "Zeitraum auswählen:",
    ("1mo", "3mo", "6mo", "1y", "2y", "5y", "max"),
    index=3
)

# Globaler Switch für Prozent-Vergleich
normalize = False
if ticker_input_2:
    normalize = st.sidebar.checkbox(
        "Performance vergleichen (%)",
        value=True,
        help="Setzt den Startwert beider Aktien auf 0%, um die reine Performance zu vergleichen."
    )

# --- DATENABRUF & ERROR HANDLING ---
if ticker_input_1:
    with st.spinner("Lade Markdaten, MSCI World Benchmark, Kennzahlen und News..."):
        try:
            # 1. Hauptaktie laden
            data_1 = yf.Ticker(ticker_input_1)
            df_1 = data_1.history(period=time_period)
            try:
                info_1 = data_1.info
            except:
                info_1 = {}

            # 2. MSCI World als Benchmark im Hintergrund laden
            try:
                msci_data = yf.Ticker("URTH")
                df_msci = msci_data.history(period=time_period)
            except:
                df_msci = pd.DataFrame()

            if df_1.empty:
                st.error(f"Keine Daten für {ticker_input_1} gefunden.")
            else:
                # 3. Vergleichsaktie laden (falls vorhanden)
                df_2 = pd.DataFrame()
                info_2 = {}
                if ticker_input_2:
                    data_2 = yf.Ticker(ticker_input_2)
                    df_2 = data_2.history(period=time_period)
                    try:
                        info_2 = data_2.info
                    except:
                        info_2 = {}
                    if df_2.empty:
                        st.sidebar.warning(f"Keine Daten für {ticker_input_2} gefunden.")

                # --- ZENTRALE KPIs ("Auf einen Blick") ---
                cols = st.columns(2 if not df_2.empty else 1)


                def zeige_kpis(df, ticker, col):
                    if len(df) >= 2:
                        aktueller_kurs = df['Close'].iloc[-1]
                        vortag_kurs = df['Close'].iloc[-2]
                        differenz = aktueller_kurs - vortag_kurs
                        prozent = (differenz / vortag_kurs) * 100
                        col.metric(
                            label=f"Letzter Schlusskurs: {ticker}",
                            value=f"{aktueller_kurs:.2f} {info_1.get('currency', 'USD')}",
                            delta=f"{differenz:.2f} ({prozent:.2f}%)"
                        )


                zeige_kpis(df_1, ticker_input_1, cols[0])
                if not df_2.empty:
                    zeige_kpis(df_2, ticker_input_2, cols[1])

                st.markdown("---")

                # --- ERWEITERTE TABS ---
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "🔮 Anlage-Kompass",
                    "📈 Kursverlauf & Labor",
                    "🔬 Fundamental-Analyse",
                    "💰 Rendite-Rechner & Mixer",
                    "📰 News & Schlagzeilen",
                    "📋 Rohdaten"
                ])

                # --- Strings für den Report-Export sammeln ---
                report_text = f"=== ANLAGE-REPORT ===\nZeitraum: {time_period}\n\n"

                # --- TAB 1: ANLAGE-KOMPASS (JETZT MIT TACHO-DIAGRAMM!) ---
                with tab1:
                    st.subheader("💡 Entscheidungshilfe für Gelegenheitsanleger")
                    kompass_cols = st.columns(2 if not df_2.empty else 1)


                    def rendere_kompass(ticker, df, info, col):
                        global report_text
                        col.markdown(f"### **{ticker}**")
                        current_price = df['Close'].iloc[-1]
                        sma_30 = df['Close'].rolling(window=30).mean().iloc[-1] if len(df) >= 30 else current_price
                        rec_key = info.get('recommendationKey', 'none').lower()

                        # Signalbestimmung
                        if "buy" in rec_key or current_price > (sma_30 * 1.03):
                            signal = "🟢 Kauf-Signal / Nachkaufen"
                            details = "Starker Aufwärtstrend oder klare Kaufempfehlung der Analysten."
                            col.success(f"**{signal}**\n\n{details}")
                        elif "sell" in rec_key or current_price < (sma_30 * 0.97):
                            signal = "🔴 Verkaufs-Signal / Vorsicht"
                            details = "Abwärtstrend oder Analysten raten zum Ausstieg."
                            col.error(f"**{signal}**\n\n{details}")
                        else:
                            signal = "🟡 Halte-Signal / Abwarten"
                            details = "Kein eindeutiger Trend. Bestehende Positionen halten."
                            col.warning(f"**{signal}**\n\n{details}")

                        report_text += f"Aktie: {ticker}\nSignal: {signal}\n"

                        target = info.get('targetMeanPrice')
                        if target:
                            potential = ((target / current_price) - 1) * 100
                            col.metric(label="Mittleres Analysten-Kursziel", value=f"{target:.2f}",
                                       delta=f"{potential:.2f}% Potenzial")
                            report_text += f"Kursziel: {target:.2f} ({potential:.2f}% Potenzial)\n"

                        # Volatilitäts-Wetterbericht Berechnung
                        beta = info.get('beta', 1.0)
                        score = int(np.clip(round(beta * 5), 1, 10))

                        if score <= 3:
                            wetter_status = "Sonnig & Ruhig"
                            wetter_desc = "Diese Aktie schwankt kaum. Perfekt für risikoarme Anleger zum langfristigen Halten."
                        elif score <= 6:
                            wetter_status = "Leicht Wechselhaft"
                            wetter_desc = "Normale Marktschwankungen. Solides Fundament mit gesundem Risiko-Rendite-Verhältnis."
                        elif score <= 8:
                            wetter_status = "Stürmisch"
                            wetter_desc = "Erhöhte Volatilität! Der Kurs bricht gerne stark aus. Nichts für schwache Nerven."
                        else:
                            wetter_status = "Extremer Wirbelsturm"
                            wetter_desc = "Extreme Ausschläge! Sehr hohes Risiko, aber auch riesige Chancensprünge."

                        report_text += f"Risiko-Score: {score}/10 ({wetter_status})\n\n"

                        # INTERAKTIVES TACHOMETER-DIAGRAMM (GAUGE CHART)
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=score,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': f"Risiko-Wetter: {wetter_status}", 'font': {'size': 16}},
                            gauge={
                                'axis': {'range': [1, 10], 'tickvals': [1, 3, 6, 8, 10],
                                         'ticktext': ['1', 'Ruhig', 'Normal', 'Sturm', '10']},
                                'bar': {'color': "#2c3e50"},  # Farbe der Nadel / des Balkens
                                'steps': [
                                    {'range': [1, 3], 'color': '#2ecc71'},  # Grün
                                    {'range': [3, 6], 'color': '#f1c40f'},  # Gelb
                                    {'range': [6, 8], 'color': '#e67e22'},  # Orange
                                    {'range': [8, 10], 'color': '#e74c3c'}  # Rot
                                ],
                            }
                        ))
                        # Layout kompakter machen, damit es perfekt in die Spalten passt
                        fig.update_layout(height=220, margin=dict(l=30, r=30, t=50, b=10))

                        # Chart in der entsprechenden Spalte rendern
                        col.plotly_chart(fig, use_container_width=True)
                        col.write(wetter_desc)

                        # Progressive Disclosure für Profis
                        with col.expander("ℹ️ Mathematische Details"):
                            col.write(f"**Exakter Beta-Faktor:** {beta:.2f}")


                    rendere_kompass(ticker_input_1, df_1, info_1, kompass_cols[0])
                    if not df_2.empty:
                        rendere_kompass(ticker_input_2, df_2, info_2, kompass_cols[1])

                    # Spickzettel-Export
                    st.markdown("---")
                    st.markdown("#### 📄 Report mitnehmen")
                    st.download_button(
                        label="Anlage-Zusammenfassung als Text-Report herunterladen",
                        data=report_text,
                        file_name=f"Anlage_Zusammenfassung_{ticker_input_1}.txt",
                        mime="text/plain"
                    )

                # --- TAB 2: KURSVERLAUF & VOLATILITÄTS-LABOR ---
                with tab2:
                    st.subheader("📈 Interaktive Chart-Analyse")
                    st.markdown("**🔬 Volatilitäts-Labor (Zusatzwerkzeuge):**")

                    lab_cols = st.columns(4)
                    show_sma = lab_cols[0].checkbox("30-Tage-Durchschnitt (SMA)",
                                                    value=True) if not normalize else False
                    show_bollinger = lab_cols[1].checkbox("Bollinger Bänder", value=False) if not normalize else False
                    show_drawdown = lab_cols[2].checkbox("Max. Einbruch anzeigen", value=False)
                    show_msci = lab_cols[3].checkbox("Mit Weltmarkt vergleichen (MSCI World)", value=False)

                    chart_data = pd.DataFrame()
                    chart_data[ticker_input_1] = df_1['Close']

                    if show_sma:
                        chart_data[f"{ticker_input_1} (30-Tage SMA)"] = df_1['Close'].rolling(window=30).mean()

                    if show_bollinger and len(df_1) >= 20:
                        sma20 = df_1['Close'].rolling(window=20).mean()
                        std20 = df_1['Close'].rolling(window=20).std()
                        chart_data["Bollinger Oben"] = sma20 + (std20 * 2)
                        chart_data["Bollinger Unten"] = sma20 - (std20 * 2)

                    if not df_2.empty:
                        chart_data[ticker_input_2] = df_2['Close']

                    if show_msci and not df_msci.empty:
                        chart_data["MSCI World Index (Weltmarkt)"] = df_msci['Close']

                    if normalize or show_msci:
                        chart_data = (chart_data / chart_data.iloc[0] - 1) * 100
                        st.line_chart(chart_data)
                    else:
                        st.line_chart(chart_data)

                    if show_drawdown:
                        def calc_max_drawdown(df):
                            roll_max = df['Close'].cummax()
                            drawdown = (df['Close'] - roll_max) / roll_max
                            return drawdown.min() * 100


                        st.info(f"📉 **Maximaler Verlust im gewählten Zeitraum:**\n"
                                f"* **{ticker_input_1}:** {calc_max_drawdown(df_1):.2f}%\n" +
                                (f"* **{ticker_input_2}:** {calc_max_drawdown(df_2):.2f}%" if not df_2.empty else "") +
                                (
                                    f"\n* **MSCI World Index:** {calc_max_drawdown(df_msci):.2f}%" if show_msci and not df_msci.empty else ""))

                # --- TAB 3: FUNDAMENTAL-ANALYSE ---
                with tab3:
                    st.subheader("🔬 Fundamentale Kennzahlen im Vergleich")
                    f_cols = st.columns(2 if not df_2.empty else 1)


                    def zeige_fundamentals(info, col, ticker):
                        col.markdown(f"### **{ticker}**")
                        kgv = info.get('trailingPE')
                        kgv_txt = f"{kgv:.2f}" if kgv else "Nicht verfügbar"
                        col.metric(label="KGV (Kurs-Gewinn-Verhältnis)", value=kgv_txt)

                        div = info.get('dividendYield')
                        div_txt = f"{(div * 100):.2f} %" if div else "0.00 %"
                        col.metric(label="Dividendenrendite", value=div_txt)

                        cap = info.get('marketCap')
                        cap_txt = f"{cap / 1e9:.2f} Mrd. {info.get('currency', 'USD')}" if cap else "Unbekannt"
                        col.write(f"**Gesamtwert (Market Cap):** {cap_txt}")


                    zeige_fundamentals(info_1, f_cols[0], ticker_input_1)
                    if not df_2.empty:
                        zeige_fundamentals(info_2, f_cols[1], ticker_input_2)

                # --- TAB 4: RENDITE-RECHNER & MIXER ---
                with tab4:
                    st.subheader("💰 Interaktiver Rendite-Rechner & Portfolio-Mixer")
                    invest_sum = st.slider("Gesamt-Investitionsbetrag wählen (€):", min_value=100, max_value=10000,
                                           value=1000, step=100)

                    if not df_2.empty:
                        st.markdown("#### ⚖️ Portfolio-Mischung einstellen")
                        weight_1 = st.slider(f"Gewichtung von {ticker_input_1} im Depot (%)", 0, 100, 50, 5)
                        weight_2 = 100 - weight_1

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
                        mix_cols[0].metric(label="Endwert des kombinierten Depots", value=f"{total_end_val:.2f} €",
                                           delta=f"{total_profit:.2f} € ({total_perf_percent:.2f}%)")
                        mix_cols[1].metric(label="Kombiniertes Risiko (Beta)", value=f"{combined_beta:.2f}")
                    else:
                        start_price = df_1['Close'].iloc[0]
                        end_price = df_1['Close'].iloc[-1]
                        end_wert = invest_sum * (end_price / start_price)
                        st.metric(label="Aktueller Wert des Investments", value=f"{end_wert:.2f} €",
                                  delta=f"{(end_wert - invest_sum):.2f} €")

                # --- TAB 5: NEWS & SCHLAGZEILEN ---
                with tab5:
                    st.subheader("📰 Warum bewegt sich der Kurs? Aktuelle News")
                    news_cols = st.columns(2 if not df_2.empty else 1)


                    def zeige_news(data, col, ticker_name):
                        col.markdown(f"### News zu **{ticker_name}**")
                        try:
                            articles = getattr(data, 'news', [])
                            for art in articles[:5]:
                                content_block = art.get('content', {})
                                title = content_block.get('title', art.get('title', 'Kein Titel'))
                                link = content_block.get('canonicalUrl', {}).get('url', art.get('link', '#'))
                                publisher = content_block.get('provider', {}).get('displayName',
                                                                                  art.get('publisher', 'Unbekannt'))
                                col.markdown(f"🔗 **[{title}]({link})**")
                                col.caption(f"Quelle: {publisher}")
                                col.markdown("---")
                        except:
                            col.info("News konnten nicht geladen werden.")


                    zeige_news(data_1, news_cols[0], ticker_input_1)
                    if not df_2.empty:
                        zeige_news(data_2, news_cols[1], ticker_input_2)

                # --- TAB 6: ROHDATEN ---
                with tab6:
                    st.write(f"**Rohdaten für {ticker_input_1}**")
                    st.dataframe(df_1)

        except Exception as e:
            st.error(f"Ein kritischer Fehler ist aufgetreten: {e}")