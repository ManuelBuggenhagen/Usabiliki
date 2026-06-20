import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

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

            # 2. MSCI World als Benchmark im Hintergrund laden (URTH)
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

                # --- TAB 1: ANLAGE-KOMPASS (Inkl. Feature 1 & Feature 4) ---
                with tab1:
                    st.subheader("💡 Entscheidungshilfe für Gelegenheitsanleger")
                    kompass_cols = st.columns(2 if not df_2.empty else 1)


                    def rendere_kompass(ticker, df, info, col, is_main=True):
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

                        # FEATURE 1: Volatilitäts-Wetterbericht (Risiko-Score)
                        beta = info.get('beta', 1.0)

                        # Berechnung eines verständlichen 1-10 Risiko-Scores basierend auf dem Beta
                        score = int(clip_val := np.clip(round(beta * 5), 1, 10))

                        if score <= 3:
                            wetter_icon = "☀️"
                            wetter_status = "Sonnig & Ruhig"
                            wetter_desc = "Diese Aktie schwankt kaum. Perfekt für risikoarme Anleger zum langfristigen Halten."
                        elif score <= 6:
                            wetter_icon = "⛅"
                            wetter_status = "Leicht Wechselhaft"
                            wetter_desc = "Normale Marktschwankungen. Solides Fundament mit gesundem Risiko-Rendite-Verhältnis."
                        elif score <= 8:
                            wetter_icon = "⚡"
                            wetter_status = "Stürmisch"
                            wetter_desc = "Erhöhte Volatilität! Der Kurs bricht gerne stark aus. Nichts für schwache Nerven."
                        else:
                            wetter_icon = "🌪️"
                            wetter_status = "Extremer Wirbelsturm"
                            wetter_desc = "Extreme Ausschläge! Sehr hohes Risiko, aber auch riesige Chancensprünge."

                        col.markdown(
                            f"#### **Volatilitäts-Wetterbericht:** {wetter_icon} {wetter_status} *(Score: {score}/10)*")
                        col.write(wetter_desc)
                        report_text += f"Risiko-Score: {score}/10 ({wetter_status})\n\n"

                        # Progressive Disclosure: Mathematischer Hintergrund im Expander versteckt
                        with col.expander("ℹ️ Für Profis: Mathematische Details einsehen"):
                            col.write(f"**Exakter Beta-Faktor:** {beta:.2f}")
                            col.write(
                                "Der Beta-Faktor misst die Schwankung im Vergleich zum Gesamtmarkt. Ein Wert von 1.00 bedeutet, dass die Aktie exakt so stark schwankt wie der Marktdurchschnitt.")


                    rendere_kompass(ticker_input_1, df_1, info_1, kompass_cols[0], is_main=True)
                    if not df_2.empty:
                        rendere_kompass(ticker_input_2, df_2, info_2, kompass_cols[1], is_main=False)

                    # FEATURE 4: Spickzettel-Export (Ganz unten platziert)
                    st.markdown("---")
                    st.markdown("#### 📄 Report mitnehmen")
                    st.download_button(
                        label="Anlage-Zusammenfassung als Text-Report herunterladen",
                        data=report_text,
                        file_name=f"Anlage_Zusammenfassung_{ticker_input_1}.txt",
                        mime="text/plain",
                        help="Generiert eine kompakte Notiz-Datei mit allen Signalen und Risiko-Scores für deine Unterlagen."
                    )

                # --- TAB 2: KURSVERLAUF & VOLATILITÄTS-LABOR (Inkl. Feature 3) ---
                with tab2:
                    st.subheader("📈 Interaktive Chart-Analyse")
                    st.markdown("**🔬 Volatilitäts-Labor (Zusatzwerkzeuge):**")

                    lab_cols = st.columns(4)
                    show_sma = lab_cols[0].checkbox("30-Tage-Durchschnitt (SMA)",
                                                    value=True) if not normalize else False
                    show_bollinger = lab_cols[1].checkbox("Bollinger Bänder (Risiko-Kanäle)",
                                                          value=False) if not normalize else False
                    show_drawdown = lab_cols[2].checkbox("Max. Einbruch anzeigen", value=False)

                    # FEATURE 3: Benchmark-Vergleich (MSCI World)
                    show_msci = lab_cols[3].checkbox("Mit Weltmarkt vergleichen (MSCI World)", value=False,
                                                     help="Zeigt die Entwicklung des globalen Aktienmarktes als Orientierungshilfe.")

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

                    # Automatischer Usability-Kniff: Wenn MSCI World gewählt wird, MÜSSEN wir prozentual vergleichen,
                    # da Index-Punkte und Aktien-Preise sonst den Chart skalierungstechnisch zerstören.
                    if normalize or show_msci:
                        chart_data = (chart_data / chart_data.iloc[0] - 1) * 100
                        st.line_chart(chart_data)
                        st.caption(
                            "⚠️ Da ein Benchmark- oder Aktienvergleich aktiv ist, zeigt das Diagramm automatisch die **prozentuale Entwicklung (%)** seit dem Startdatum an.")
                    else:
                        st.line_chart(chart_data)
                        st.caption("Angezeigt werden die absoluten Schlusskurse in Originalwährung.")

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


                    zeige_fundamentals(info_1, f_cols[0], ticker_input_1)
                    if not df_2.empty:
                        zeige_fundamentals(info_2, f_cols[1], ticker_input_2)

                # --- TAB 4: RENDITE-RECHNER & MIXER (Inkl. Feature 2) ---
                with tab4:
                    st.subheader("💰 Interaktiver Rendite-Rechner & Portfolio-Mixer")
                    st.write(
                        "Simuliere historische Szenarien und lerne, wie das Mischen von Aktien dein Risiko verändert.")

                    invest_sum = st.slider("Gesamt-Investitionsbetrag wählen (€):", min_value=100, max_value=10000,
                                           value=1000, step=100)

                    # FEATURE 2: Portfolio-Mixer (Wird nur freigeschaltet, wenn zwei Ticker aktiv sind)
                    if not df_2.empty:
                        st.markdown("#### ⚖️ Portfolio-Mischung einstellen")
                        weight_1 = st.slider(f"Gewichtung von {ticker_input_1} im Depot (%)", 0, 100, 50, 5)
                        weight_2 = 100 - weight_1
                        st.caption(
                            f"Daraus ergibt sich automatisch eine Gewichtung von **{weight_2}%** für **{ticker_input_2}**.")

                        # Berechnungen für Aktie 1
                        start_1, end_1 = df_1['Close'].iloc[0], df_1['Close'].iloc[-1]
                        invest_1 = invest_sum * (weight_1 / 100)
                        end_val_1 = invest_1 * (end_1 / start_1)

                        # Berechnungen für Aktie 2
                        start_2, end_2 = df_2['Close'].iloc[0], df_2['Close'].iloc[-1]
                        invest_2 = invest_sum * (weight_2 / 100)
                        end_val_2 = invest_2 * (end_2 / start_2)

                        # Zusammenführung
                        total_end_val = end_val_1 + end_val_2
                        total_profit = total_end_val - invest_sum
                        total_perf_percent = (total_end_val / invest_sum - 1) * 100

                        # Kombiniertes Risiko (Gewichtetes Beta)
                        beta_1 = info_1.get('beta', 1.0)
                        beta_2 = info_2.get('beta', 1.0)
                        combined_beta = (weight_1 / 100) * beta_1 + (weight_2 / 100) * beta_2

                        st.markdown("---")
                        st.markdown("### 📊 Ergebnis deiner Portfolio-Mischung")
                        mix_cols = st.columns(2)

                        mix_cols[0].metric(label="Endwert des kombinierten Depots", value=f"{total_end_val:.2f} €",
                                           delta=f"{total_profit:.2f} € ({total_perf_percent:.2f}%)")

                        # HCI-Erklärungseffekt für Casual User: Risiko-Reduzierung sichtbar machen
                        if combined_beta > 1.3:
                            status_mix = "🔥 Hoch schwankend"
                        elif combined_beta < 0.8:
                            status_mix = "🛡️ Sehr wertstabil"
                        else:
                            status_mix = "⚖️ Moderates Marktrisiko"

                        mix_cols[1].metric(label="Neues Gesamt-Risiko (Kombiniertes Beta)",
                                           value=f"{combined_beta:.2f}", delta=status_mix, delta_color="off")
                        mix_cols[1].caption(
                            "💡 **UX-Tipp für Einsteiger:** Siehst du, wie das Risiko sinkt, wenn du eine stürmische Aktie mit einer ruhigen Aktie mischt? Das nennt man Diversifikation!")

                    else:
                        # Standard-Rechner für nur eine Aktie
                        st.info(
                            "💡 **Tipp:** Gib oben in der Sidebar einen zweiten Ticker ein, um den interaktiven **Portfolio-Mixer** freizuschalten!")
                        calc_cols = st.columns(1)

                        start_price = df_1['Close'].iloc[0]
                        end_price = df_1['Close'].iloc[-1]
                        performance = (end_price / start_price)
                        end_wert = invest_sum * performance
                        gewinn = end_wert - invest_sum
                        prozent_total = (performance - 1) * 100

                        calc_cols[0].markdown(f"#### Ergebnis für **{ticker_input_1}**")
                        calc_cols[0].metric(label="Aktueller Wert des Investments", value=f"{end_wert:.2f} €",
                                            delta=f"{gewinn:.2f} € ({prozent_total:.2f}%)")
                        calc_cols[0].caption(
                            f"Gekauft zum Kurs von {start_price:.2f} am {df_1.index[0].strftime('%d.%m.%Y')}")

                # --- TAB 5: NEWS & SCHLAGZEILEN ---
                with tab5:
                    st.subheader("📰 Warum bewegt sich der Kurs? Aktuelle News")
                    st.write(
                        "Kursschwankungen entstehen meist durch Nachrichten. Hier sind die aktuellsten Schlagzeilen:")

                    news_cols = st.columns(2 if not df_2.empty else 1)


                    def zeige_news(data, col, ticker_name):
                        col.markdown(f"### News zu **{ticker_name}**")
                        try:
                            articles = getattr(data, 'news', [])
                            if not articles:
                                col.info("Momentan keine aktuellen Nachrichten über Yahoo Finance verfügbar.")
                                return

                            for art in articles[:5]:
                                content_block = art.get('content', {})
                                if content_block:
                                    title = content_block.get('title', 'Kein Titel verfügbar')
                                    link = content_block.get('canonicalUrl', {}).get('url', '#')
                                    publisher = content_block.get('provider', {}).get('displayName', 'Unbekannt')
                                else:
                                    title = art.get('title', 'Kein Titel verfügbar')
                                    link = art.get('link', '#')
                                    publisher = art.get('publisher', 'Unbekannt')

                                col.markdown(f"🔗 **[{title}]({link})**")
                                col.caption(f"Quelle: {publisher}")
                                col.markdown("---")
                        except Exception as e:
                            col.info("News konnten für diesen Ticker temporär nicht geladen werden.")


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