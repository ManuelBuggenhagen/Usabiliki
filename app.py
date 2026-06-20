import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Konfiguration der Seite
st.set_page_config(page_title="Aktien-Volatilität & Analyse", layout="wide")
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
    with st.spinner("Lade Markdaten, Kennzahlen und News..."):
        try:
            # Daten für Aktie 1
            data_1 = yf.Ticker(ticker_input_1)
            df_1 = data_1.history(period=time_period)
            try:
                info_1 = data_1.info
            except:
                info_1 = {}

            if df_1.empty:
                st.error(f"Keine Daten für {ticker_input_1} gefunden.")
            else:
                # Daten für Aktie 2 (falls vorhanden)
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

                # --- 1. ZENTRALE KPIs ("Auf einen Blick") ---
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

                # --- 2. ERWEITERTE TABS (Progressive Disclosure) ---
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "🔮 Anlage-Kompass",
                    "📈 Kursverlauf & Labor",
                    "🔬 Fundamental-Analyse",
                    "💰 Rendite-Rechner",
                    "📰 News & Schlagzeilen",
                    "📋 Rohdaten"
                ])

                # --- TAB 1: ANLAGE-KOMPASS ---
                with tab1:
                    st.subheader("💡 Entscheidungshilfe für Gelegenheitsanleger")
                    kompass_cols = st.columns(2 if not df_2.empty else 1)


                    def rendere_kompass(ticker, df, info, col):
                        col.markdown(f"### **{ticker}**")
                        current_price = df['Close'].iloc[-1]
                        sma_30 = df['Close'].rolling(window=30).mean().iloc[-1] if len(df) >= 30 else current_price
                        rec_key = info.get('recommendationKey', 'none').lower()

                        if "buy" in rec_key or current_price > (sma_30 * 1.03):
                            col.success(
                                "🟢 **Kauf-Signal / Nachkaufen**\n\nStarker Aufwärtstrend oder klare Kaufempfehlung der Analysten.")
                        elif "sell" in rec_key or current_price < (sma_30 * 0.97):
                            col.error(
                                "🔴 **Verkaufs-Signal / Vorsicht**\n\nAbwärtstrend oder Analysten raten zum Ausstieg.")
                        else:
                            col.warning(
                                "🟡 **Halte-Signal / Abwarten**\n\nKein eindeutiger Trend. Bestehende Positionen halten.")

                        target = info.get('targetMeanPrice')
                        if target:
                            potential = ((target / current_price) - 1) * 100
                            col.metric(label="Mittleres Analysten-Kursziel", value=f"{target:.2f}",
                                       delta=f"{potential:.2f}% Potenzial")

                        beta = info.get('beta')
                        if beta:
                            if beta > 1.3:
                                status = "🔥 **Hoch** (Schwankt stärker als der Markt)"
                            elif beta < 0.8:
                                status = "🛡️ **Niedrig** (Sehr wertstabil & ruhig)"
                            else:
                                status = "⚖️ **Moderat** (Marktdurchschnitt)"
                            col.write(f"**Risiko-Profil:** {status} *(Beta: {beta:.2f})*")


                    rendere_kompass(ticker_input_1, df_1, info_1, kompass_cols[0])
                    if not df_2.empty:
                        rendere_kompass(ticker_input_2, df_2, info_2, kompass_cols[1])

                # --- TAB 2: KURSVERLAUF & VOLATILITÄTS-LABOR ---
                with tab2:
                    st.subheader("📈 Interaktive Chart-Analyse")

                    # Labor-Steuerung (Nur sinnvoll im absoluten Modus oder für Hauptaktie)
                    st.markdown("**🔬 Volatilitäts-Labor (Zusatzwerkzeuge für Hauptaktie):**")
                    lab_cols = st.columns(3)
                    show_sma = lab_cols.checkbox("30-Tage-Durchschnitt (SMA)", value=True) if not normalize else False
                    show_bollinger = lab_cols.checkbox("Bollinger Bänder (Volatilitäts-Kanäle)",
                                                       value=False) if not normalize else False
                    show_drawdown = lab_cols.checkbox("Maximalen historischen Einbruch anzeigen", value=False)

                    chart_data = pd.DataFrame()
                    chart_data[ticker_input_1] = df_1['Close']

                    if show_sma:
                        chart_data[f"{ticker_input_1} (30-Tage SMA)"] = df_1['Close'].rolling(window=30).mean()

                    if show_bollinger and len(df_1) >= 20:
                        sma20 = df_1['Close'].rolling(window=20).mean()
                        std20 = df_1['Close'].rolling(window=20).std()
                        chart_data["Bollinger Oben (Max Schwankung)"] = sma20 + (std20 * 2)
                        chart_data["Bollinger Unten (Min Schwankung)"] = sma20 - (std20 * 2)

                    if not df_2.empty:
                        chart_data[ticker_input_2] = df_2['Close']
                        if normalize:
                            chart_data = (chart_data / chart_data.iloc[0] - 1) * 100

                    st.line_chart(chart_data)

                    if show_drawdown:
                        # Max Drawdown Berechnung
                        def calc_max_drawdown(df):
                            roll_max = df['Close'].cummax()
                            drawdown = (df['Close'] - roll_max) / roll_max
                            return drawdown.min() * 100


                        st.info(f"📉 **Maximaler Verlust im gewählten Zeitraum:**\n"
                                f"* **{ticker_input_1}:** {calc_max_drawdown(df_1):.2f}%\n" +
                                (f"* **{ticker_input_2}:** {calc_max_drawdown(df_2):.2f}%" if not df_2.empty else ""))

                # --- TAB 3: FUNDAMENTAL-ANALYSE ---
                with tab3:
                    st.subheader("🔬 Fundamentale Kennzahlen im Vergleich")
                    st.write("Erfahrene Anleger nutzen diese Werte, um den fairen Wert einer Firma zu schätzen.")

                    f_cols = st.columns(2 if not df_2.empty else 1)


                    def zeige_fundamentals(info, col, ticker):
                        col.markdown(f"### **{ticker}**")

                        kgv = info.get('trailingPE')
                        kgv_txt = f"{kgv:.2f}" if kgv else "Nicht verfügbar"
                        col.metric(label="KGV (Kurs-Gewinn-Verhältnis)", value=kgv_txt,
                                   help="Ein niedriges KGV kann bedeuten, dass die Aktie günstig ist. Historischer Schnitt liegt oft bei 15-20.")

                        div = info.get('dividendYield')
                        div_txt = f"{(div * 100):.2f} %" if div else "0.00 %"
                        col.metric(label="Dividendenrendite", value=div_txt,
                                   help="Die jährliche Ausschüttung des Gewichts an dich als Aktionär in Prozent des aktuellen Kurses.")

                        cap = info.get('marketCap')
                        cap_txt = f"{cap / 1e9:.2f} Mrd. {info.get('currency', 'USD')}" if cap else "Unbekannt"
                        col.write(f"**Gesamtwert des Unternehmens (Market Cap):** {cap_txt}")

                        debt = info.get('debtToEquity')
                        debt_txt = f"{debt:.2f}%" if debt else "Keine Daten"
                        col.write(
                            f"**Verschuldungsgrad (Debt-to-Equity):** {debt_txt} *(Über 100% bedeutet mehr Schulden als Eigenkapital)*")


                    zeige_fundamentals(info_1, f_cols[0], ticker_input_1)
                    if not df_2.empty:
                        zeige_fundamentals(info_2, f_cols[1], ticker_input_2)

                # --- TAB 4: RENDITE-RECHNER ---
                with tab4:
                    st.subheader("💰 Was-wäre-wenn? Szenario-Simulation")
                    st.write(
                        "Finde heraus, was aus deinem Geld geworden wäre, hättest du am Anfang des gewählten Zeitraums investiert.")

                    invest_sum = st.slider("Investitionsbetrag wählen (€):", min_value=100, max_value=10000, value=1000,
                                           step=100)

                    calc_cols = st.columns(2 if not df_2.empty else 1)


                    def berechne_rendite(df, ticker, col):
                        start_price = df['Close'].iloc[0]
                        end_price = df['Close'].iloc[-1]
                        performance = (end_price / start_price)
                        end_wert = invest_sum * performance
                        gewinn = end_wert - invest_sum
                        prozent_total = (performance - 1) * 100

                        col.markdown(f"#### Ergebnis für **{ticker}**")
                        col.metric(label="Aktueller Wert des Investments", value=f"{end_wert:.2f} €",
                                   delta=f"{gewinn:.2f} € ({prozent_total:.2f}%)")
                        col.caption(f"Gekauft zum Kurs von {start_price:.2f} am {df.index[0].strftime('%d.%m.%Y')}")


                    berechne_rendite(df_1, ticker_input_1, calc_cols[0])
                    if not df_2.empty:
                        berechne_rendite(df_2, ticker_input_2, calc_cols[1])

                # --- TAB 5: NEWS & SCHLAGZEILEN ---
                with tab5:
                    st.subheader("📰 Warum bewegt sich der Kurs? Aktuelle News")
                    st.write(
                        "Kursschwankungen entstehen meist durch Nachrichten. Hier sind die aktuellsten Schlagzeilen:")

                    news_cols = st.columns(2 if not df_2.empty else 1)


                    def zeige_news(data, col, ticker):
                        col.markdown(f"### News zu **{ticker}**")
                        try:
                            articles = data.news[:5]
                            if not articles:
                                col.info("Keine aktuellen Nachrichten für dieses Symbol gefunden.")
                            for art in articles:
                                col.markdown(f"🔗 **[{art['title']}]({art['link']})**")
                                col.caption(f"Quelle: {art.get('publisher', 'Unbekannt')}")
                                col.markdown("")
                        except:
                            col.error("News-Feed konnte nicht geladen werden.")


                    zeige_news(data_1, news_cols[0], ticker_input_1)
                    if not df_2.empty:
                        zeige_news(data_2, news_cols[1], ticker_input_2)

                # --- TAB 6: ROHDATEN ---
                with tab6:
                    st.write(f"**Rohdaten für {ticker_input_1}**")
                    st.dataframe(df_1)
                    if not df_2.empty:
                        st.write(f"**Rohdaten für {ticker_input_2}**")
                        st.dataframe(df_2)

        except Exception as e:
            st.error(f"Ein kritischer Fehler ist aufgetreten: {e}")