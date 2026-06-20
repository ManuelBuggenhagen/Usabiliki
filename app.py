import streamlit as st
import yfinance as yf
import pandas as pd

# Konfiguration der Seite
st.set_page_config(page_title="Aktien-Volatilität", layout="wide")
st.title("Aktienmarkt Dashboard")

# --- EINSTELLUNGEN (SIDEBAR) ---
st.sidebar.header("⚙️ Einstellungen")

# 1. Aktie (Fehlerverzeihende Freitexteingabe)
ticker_input_1 = st.sidebar.text_input("1. Aktien-Ticker (Hauptaktie, z.B. AAPL):", "AAPL").upper()
# 2. Aktie (Optional für Vergleich)
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
    with st.spinner("Lade Daten..."):
        try:
            # Daten für Aktie 1
            data_1 = yf.Ticker(ticker_input_1)
            df_1 = data_1.history(period=time_period)

            if df_1.empty:
                st.error(f"Keine Daten für {ticker_input_1} gefunden.")
            else:
                # Daten für Aktie 2 abrufen (falls eingegeben)
                df_2 = pd.DataFrame()
                if ticker_input_2:
                    data_2 = yf.Ticker(ticker_input_2)
                    df_2 = data_2.history(period=time_period)
                    if df_2.empty:
                        st.sidebar.warning(f"Keine Daten für {ticker_input_2} gefunden.")

                # --- 1. ZENTRALE KPIs ("Auf einen Blick") ---
                # Dynamische Spalten: 2 Spalten wenn Vergleichsaktie da, sonst 1
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

                st.markdown("---")  # Optischer Trennstrich

                # --- 2. VISUELLE STRUKTUR (TABS) ---
                tab1, tab2, tab3 = st.tabs(["📈 Kursverlauf", "📊 Handelsvolumen", "📋 Rohdaten"])

                with tab1:
                    # Basis-Datenframe für den Chart
                    chart_data = pd.DataFrame()
                    chart_data[ticker_input_1] = df_1['Close']

                    # 30-Tage-Durchschnitt für die Hauptaktie (Volatilität greifbar machen)
                    # (Wir blenden ihn der Übersicht halber aus, wenn wir % vergleichen)
                    if not normalize:
                        chart_data[f"{ticker_input_1} (30-Tage SMA)"] = df_1['Close'].rolling(window=30).mean()

                    # Vergleichsaktie hinzufügen, falls vorhanden
                    if not df_2.empty:
                        chart_data[ticker_input_2] = df_2['Close']

                        if normalize:
                            # Prozentuale Umrechnung
                            chart_data = (chart_data / chart_data.iloc[0] - 1) * 100
                            st.line_chart(chart_data)
                            st.caption("Angezeigt wird die prozentuale Entwicklung im gewählten Zeitraum.")
                        else:
                            st.line_chart(chart_data)
                            st.caption("Angezeigt werden die absoluten Schlusskurse.")
                    else:
                        st.line_chart(chart_data)
                        st.caption("Angezeigt werden die absoluten Schlusskurse inklusive 30-Tage-Durchschnitt.")

                with tab2:
                    # Volumen-Vergleich als Bar-Chart
                    vol_data = pd.DataFrame()
                    vol_data[ticker_input_1] = df_1['Volume']
                    if not df_2.empty:
                        vol_data[ticker_input_2] = df_2['Volume']
                    st.bar_chart(vol_data)

                with tab3:
                    # Rohtabellen (versteckt im letzten Tab)
                    st.write(f"**Rohdaten für {ticker_input_1}**")
                    st.dataframe(df_1)
                    if not df_2.empty:
                        st.write(f"**Rohdaten für {ticker_input_2}**")
                        st.dataframe(df_2)

        except Exception as e:
            st.error(f"Ein Fehler ist aufgetreten: {e}")