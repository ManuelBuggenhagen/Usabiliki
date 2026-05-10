import streamlit as st
import yfinance as yf
import pandas as pd

# Konfiguration der Seite (Breites Layout für bessere Übersicht)
st.set_page_config(page_title="Aktien-Volatilität", layout="wide")

st.title("Aktienmarkt-Volatilität: Usability-Dashboard")

# --- EINSTELLUNGEN (SIDEBAR) ---
st.sidebar.header("⚙️ Einstellungen")

# 4. Freie Ticker-Eingabe (Fehlerverzeihend)
# .upper() sorgt dafür, dass aus "aapl" automatisch "AAPL" wird
ticker_input = st.sidebar.text_input("Aktien-Ticker (z.B. AAPL, TSLA, SAP):", "AAPL").upper()

time_period = st.sidebar.selectbox(
    "Zeitraum auswählen:",
    ("1mo", "3mo", "6mo", "1y", "2y", "5y", "max"),
    index=3
)

# --- DATENABRUF & ERROR HANDLING ---
if ticker_input:
    # Lade-Animation für besseres Nutzer-Feedback
    with st.spinner(f"Lade Daten für {ticker_input}..."):
        ticker_data = yf.Ticker(ticker_input)
        df_history = ticker_data.history(period=time_period)

    # 4. Fehlerbehandlung: Prüfen, ob yfinance überhaupt Daten gefunden hat
    if df_history.empty:
        st.error(
            f"Hoppla! Es konnten keine Daten für '{ticker_input}' gefunden werden. Bitte überprüfe die Schreibweise (z.B. MSFT statt MICROSOFT).")
    else:
        df_history.reset_index(inplace=True)

        # --- DATENAUFBEREITUNG ---
        # 3. Volatilität greifbar machen: 30-Tage Gleitender Durchschnitt
        # (Wird nur berechnet, wenn genug Tage vorhanden sind)
        df_history['30-Tage-Trend'] = df_history['Close'].rolling(window=30).mean()

        # --- 1. AUF EINEN BLICK: KPIs ---
        # Wir greifen die letzten beiden Tage ab, um die Veränderung zu berechnen
        if len(df_history) >= 2:
            heute_close = df_history['Close'].iloc[-1]
            gestern_close = df_history['Close'].iloc[-2]
            differenz_absolut = heute_close - gestern_close
            differenz_prozent = (differenz_absolut / gestern_close) * 100

            st.subheader(f"Aktueller Stand: {ticker_input}")

            # Drei Spalten für eine saubere Anordnung der Metriken
            col1, col2, col3 = st.columns(3)

            # st.metric macht automatisch grüne/rote Pfeile anhand des Vorzeichens der Differenz
            col1.metric("Letzter Schlusskurs", f"${heute_close:.2f}",
                        f"{differenz_absolut:.2f} ({differenz_prozent:.2f}%)")

            # Handelsvolumen hübsch formatieren (Tausendertrennzeichen)
            volumen_heute = int(df_history['Volume'].iloc[-1])
            col2.metric("Heutiges Handelsvolumen", f"{volumen_heute:,}".replace(",", "."))

            # Schwankungsbreite (Maximal- vs. Minimalwert im Zeitraum)
            schwankung = df_history['Close'].max() - df_history['Close'].min()
            col3.metric(f"Schwankungsbreite ({time_period})", f"${schwankung:.2f}")

        st.divider()  # Visuelle Trennlinie

        # --- 2. VISUELLE STRUKTURIERUNG (Tabs) ---
        st.subheader("Detail-Analyse")

        # Wir verpacken die Charts und Tabellen in anklickbare Karteireiter
        tab1, tab2, tab3 = st.tabs(["📊 Kurs & Volatilität", "📉 Handelsvolumen", "📋 Rohdaten"])

        with tab1:
            st.markdown("**Schlusskurs im Vergleich zum 30-Tage-Trend**")
            st.markdown(
                "*Usability-Tipp: Schwankt die blaue Kurs-Linie stark um die rote Trend-Linie, haben wir eine hohe Volatilität.*")
            # Wir übergeben nun eine Liste mit zwei Y-Werten, um beide Linien zu zeichnen
            st.line_chart(df_history, x="Date", y=["Close", "30-Tage-Trend"])

        with tab2:
            st.markdown("**Tägliches Handelsvolumen**")
            st.bar_chart(df_history, x="Date", y="Volume")

        with tab3:
            st.markdown("**Rohe Datentabelle**")
            # Die Tabelle ist nun elegant "versteckt" und stört nicht beim ersten Blick
            st.dataframe(df_history, use_container_width=True)