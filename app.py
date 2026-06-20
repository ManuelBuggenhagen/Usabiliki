import streamlit as st
import yfinance as yf
import pandas as pd

# Konfiguration der Seite (Breites Layout für bessere Übersicht)
st.set_page_config(page_title="Aktien-Volatilität", layout="wide")
st.title("Aktienmarkt Dashboard")

# --- EINSTELLUNGEN (SIDEBAR) ---
st.sidebar.header("⚙️ Einstellungen")

# 1. Aktie (Hauptaktie)
ticker_input_1 = st.sidebar.text_input("1. Aktien-Ticker (Hauptaktie, z.B. AAPL):", "AAPL").upper()

# 2. Aktie (Optional für Vergleich)
ticker_input_2 = st.sidebar.text_input("2. Aktien-Ticker (Vergleich, z.B. MSFT):", "").upper()

time_period = st.sidebar.selectbox(
    "Zeitraum auswählen:",
    ("1mo", "3mo", "6mo", "1y", "2y", "5y", "max"),
    index=3
)

# Optionale Usability-Verbesserung: Prozentualer Vergleich
normalize = False
if ticker_input_2:
    normalize = st.sidebar.checkbox("Performance vergleichen (%)", value=True,
                                    help="Setzt den Startwert beider Aktien auf 0%, um die Entwicklung besser vergleichen zu können.")

# --- DATENABRUF & ERROR HANDLING ---
if ticker_input_1:
    with st.spinner("Lade Daten..."):
        try:
            # Daten für Aktie 1 abrufen
            ticker_data_1 = yf.Ticker(ticker_input_1)
            df_history_1 = ticker_data_1.history(period=time_period)

            if df_history_1.empty:
                st.error(f"Keine Daten für {ticker_input_1} gefunden. Bitte überprüfe den Ticker.")
            else:
                # Basis-DataFrame für den Chart vorbereiten
                chart_data = pd.DataFrame()
                chart_data[ticker_input_1] = df_history_1['Close']

                # Wenn ein zweiter Ticker eingegeben wurde, Daten holen und hinzufügen
                if ticker_input_2:
                    ticker_data_2 = yf.Ticker(ticker_input_2)
                    df_history_2 = ticker_data_2.history(period=time_period)

                    if not df_history_2.empty:
                        # Wir stellen sicher, dass die Indizes (Daten) übereinstimmen
                        chart_data[ticker_input_2] = df_history_2['Close']
                    else:
                        st.sidebar.warning(f"Keine Daten für Vergleichsaktie {ticker_input_2} gefunden.")

                # --- VISUALISIERUNG ---
                st.subheader("Kursverlauf")

                # Wenn normalisiert werden soll (und eine zweite Aktie da ist)
                if normalize and ticker_input_2:
                    # Prozentuale Veränderung vom ersten Tag an berechnen
                    # (Aktueller Wert / Startwert - 1) * 100
                    chart_data_norm = (chart_data / chart_data.iloc[0] - 1) * 100
                    st.line_chart(chart_data_norm)
                    st.caption("Angezeigt wird die prozentuale Entwicklung im gewählten Zeitraum.")
                else:
                    st.line_chart(chart_data)
                    st.caption("Angezeigt werden die absoluten Schlusskurse in der jeweiligen Währung.")

                # Hier können später die KPIs und Rohtabellen wieder eingefügt werden.
                # Für den Moment fokussieren wir uns auf den sauberen Chart-Vergleich.

        except Exception as e:
            st.error(f"Ein Fehler beim Abrufen der Daten ist aufgetreten: {e}")