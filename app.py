import streamlit as st
import yfinance as yf
import pandas as pd

# Konfiguration der Seite
st.set_page_config(page_title="Aktien-Volatilität", layout="wide")
st.title("Aktienmarkt Dashboard")

# --- EINSTELLUNGEN (SIDEBAR) ---
st.sidebar.header("⚙️ Einstellungen")

ticker_input_1 = st.sidebar.text_input("1. Aktien-Ticker (Hauptaktie, z.B. AAPL):", "AAPL").upper()
ticker_input_2 = st.sidebar.text_input("2. Aktien-Ticker (Vergleich, z.B. MSFT):", "").upper()

time_period = st.sidebar.selectbox(
    "Zeitraum auswählen:",
    ("1mo", "3mo", "6mo", "1y", "2y", "5y", "max"),
    index=3
)

# Checkbox für Normalisierung (nur anzeigen, wenn 2. Aktie existiert)
normalize = False
if ticker_input_2:
    normalize = st.sidebar.checkbox("Performance vergleichen (%)", value=True,
                                    help="Setzt den Startwert beider Aktien auf 0%, um die Entwicklung besser vergleichen zu können.")

# --- DATENABRUF & ERROR HANDLING ---
if ticker_input_1:
    with st.spinner("Lade Marktdaten und Analysten-Stimmen..."):
        try:
            # Daten für Aktie 1 abrufen
            data_1 = yf.Ticker(ticker_input_1)
            df_1 = data_1.history(period=time_period)

            # Wichtig für Phase 2: Stammdaten/Analystendaten abrufen
            # Wir nutzen .get(), falls yfinance für ein Symbol mal keine Daten liefert
            try:
                info_1 = data_1.info
            except:
                info_1 = {}

            if df_1.empty:
                st.error(f"Keine Daten für {ticker_input_1} gefunden.")
            else:
                # Daten für Aktie 2 abrufen (falls eingegeben)
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
                        col.metric(label=f"Letzter Schlusskurs: {ticker}",
                                   value=f"{aktueller_kurs:.2f}",
                                   delta=f"{differenz:.2f} ({prozent:.2f}%)")


                zeige_kpis(df_1, ticker_input_1, cols[0])
                if not df_2.empty:
                    zeige_kpis(df_2, ticker_input_2, cols[1])

                st.markdown("---")

                # --- 2. TABS (Anlage-Kompass jetzt ganz vorne für beste UX!) ---
                tab1, tab2, tab3, tab4 = st.tabs([
                    "🔮 Anlage-Kompass",
                    "📈 Kursverlauf",
                    "📊 Handelsvolumen",
                    "📋 Rohdaten"
                ])

                # --- TAB 1: ANLAGE-KOMPASS (NEU!) ---
                with tab1:
                    st.subheader("💡 Entscheidungshilfe für Gelegenheitsanleger")
                    st.write("Basierend auf dem aktuellen Trend, Analystenmeinungen und dem Risiko-Profil.")

                    kompass_cols = st.columns(2 if not df_2.empty else 1)


                    def rendere_kompass(ticker, df, info, col):
                        col.markdown(f"### **{ticker}**")

                        # A. Ampel-Logik (Trend + Analysten-Key)
                        current_price = df['Close'].iloc[-1]
                        sma_30 = df['Close'].rolling(window=30).mean().iloc[-1] if len(df) >= 30 else current_price
                        rec_key = info.get('recommendationKey', 'none').lower()

                        if "buy" in rec_key or current_price > (sma_30 * 1.03):
                            col.success(
                                "🟢 **Kauf-Signal / Nachkaufen**\n\nDie Aktie zeigt einen starken Aufwärtstrend oder wird von Analysten klar zum Kauf empfohlen. Potenzial für Einstiege ist vorhanden.")
                        elif "sell" in rec_key or current_price < (sma_30 * 0.97):
                            col.error(
                                "🔴 **Verkaufs-Signal / Vorsicht**\n\nDer Kurs hat den gleitenden Durchschnitt nach unten durchbrochen oder Analysten raten zum Ausstieg. Risiko für weitere Verluste.")
                        else:
                            col.warning(
                                "🟡 **Halte-Signal / Abwarten**\n\nKein eindeutiger Trend erkennbar. Der Kurs pendelt stabil. Bestehende Aktien sollten gehalten, neue Käufe abgewartet werden.")

                        # B. Analysten-Kursziel
                        target = info.get('targetMeanPrice')
                        if target:
                            potential = ((target / current_price) - 1) * 100
                            col.metric(label="Mittleres Kursziel der Experten",
                                       value=f"{target:.2f} {info.get('currency', 'USD')}",
                                       delta=f"{potential:.2f}% Potential")
                        else:
                            col.info("ℹ️ Kein konkretes Kursziel von Analysten hinterlegt.")

                        # C. Risiko-Profil (Beta-Wert übersetzt für Laien)
                        beta = info.get('beta')
                        if beta:
                            if beta > 1.3:
                                risiko_status = "🔥 **Hoch** (Schwankt deutlich stärker als der Markt. Nichts für schwache Nerven!)"
                            elif beta < 0.8:
                                risiko_status = "🛡️ **Niedrig** (Ein echter Ruheanker. Schwankt kaum und läuft sehr stabil.)"
                            else:
                                risiko_status = "⚖️ **Moderat** (Schwankt im gesunden Durchschnitt des Marktes.)"
                            col.write(f"**Risiko-Profil:** {risiko_status} *(Beta-Wert: {beta:.2f})*")
                        else:
                            col.write("**Risiko-Profil:** Keine Volatilitätsdaten zur Einstufung vorhanden.")


                    # Kompass für Aktie 1 anzeigen
                    rendere_kompass(ticker_input_1, df_1, info_1, kompass_cols[0])

                    # Kompass für Aktie 2 anzeigen (falls vorhanden)
                    if not df_2.empty:
                        rendere_kompass(ticker_input_2, df_2, info_2, kompass_cols[1])

                # --- TAB 2: KURSVERLAUF ---
                with tab2:
                    chart_data = pd.DataFrame()
                    chart_data[ticker_input_1] = df_1['Close']

                    if not normalize:
                        chart_data[f"{ticker_input_1} (30-Tage SMA)"] = df_1['Close'].rolling(window=30).mean()

                    if not df_2.empty:
                        chart_data[ticker_input_2] = df_2['Close']
                        if normalize:
                            chart_data = (chart_data / chart_data.iloc[0] - 1) * 100
                            st.line_chart(chart_data)
                            st.caption("Angezeigt wird die prozentuale Entwicklung im gewählten Zeitraum.")
                        else:
                            st.line_chart(chart_data)
                            st.caption("Angezeigt werden die absoluten Schlusskurse.")
                    else:
                        st.line_chart(chart_data)
                        st.caption("Angezeigt werden die absoluten Schlusskurse inklusive 30-Tage-Durchschnitt.")

                # --- TAB 3: HANDELSVOLUMEN ---
                with tab3:
                    vol_data = pd.DataFrame()
                    vol_data[ticker_input_1] = df_1['Volume']
                    if not df_2.empty:
                        vol_data[ticker_input_2] = df_2['Volume']
                    st.bar_chart(vol_data)

                # --- TAB 4: ROHDATEN ---
                with tab4:
                    st.write(f"**Rohdaten für {ticker_input_1}**")
                    st.dataframe(df_1)
                    if not df_2.empty:
                        st.write(f"**Rohdaten für {ticker_input_2}**")
                        st.dataframe(df_2)

        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")