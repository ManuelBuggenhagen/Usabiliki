import streamlit as st
import yfinance as yf
import pandas as pd

# Titel des Dashboards (Simpel & Funktional)
st.title("Aktienmarkt-Volatilität: Baseline Prototyp")

# --- BENUTZEREINGABEN (NEU) ---
st.subheader("Einstellungen")

# Dropdown für die Aktienauswahl
ticker_symbol = st.selectbox(
    "Wähle eine Aktie:",
    ("AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "SAP")
)

# Dropdown für den Zeitraum
# yfinance akzeptiert bestimmte Strings, diese geben wir hier als Auswahlmöglichkeiten vor
time_period = st.selectbox(
    "Wähle den Zeitraum:",
    ("1mo", "3mo", "6mo", "1y", "2y", "5y", "max"),
    index=3 # Standardmäßig ist "1y" (das 4. Element, Index 3) ausgewählt
)

st.write(f"Lade historische Daten für: **{ticker_symbol}** (Zeitraum: {time_period})")

# --- DATENABRUF ---
# Die hardcodierten Werte wurden durch die Variablen aus den Dropdowns ersetzt
ticker_data = yf.Ticker(ticker_symbol)
df_history = ticker_data.history(period=time_period)

# Index zurücksetzen für sauberere Tabellen/Charts
df_history.reset_index(inplace=True)

# --- VISUALISIERUNG (DATA DUMP) ---

# 1. Rohtabelle anzeigen
st.subheader("Rohdaten (Tabelle)")
st.dataframe(df_history)

# 2. Simpler Line-Chart für den Schlusskurs (Close)
st.subheader("Schlusskurs-Verlauf")
st.line_chart(df_history, x="Date", y="Close")

# 3. Simpler Bar-Chart für das Handelsvolumen (Volume)
st.subheader("Handelsvolumen")
st.bar_chart(df_history, x="Date", y="Volume")