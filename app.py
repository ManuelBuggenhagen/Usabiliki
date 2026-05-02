import streamlit as st
import yfinance as yf
import pandas as pd

# Titel des Dashboards (Simpel & Funktional)
st.title("Aktienmarkt-Volatilität: Baseline Prototyp")

# Hardcodierter Ticker für Phase 1 (Apple)
ticker_symbol = "AAPL"
st.write(f"Lade historische Daten für: **{ticker_symbol}** (Zeitraum: Letztes Jahr)")

# --- DATENABRUF ---
# Ticker-Objekt erstellen und historische Daten für 1 Jahr ("1y") abrufen
ticker_data = yf.Ticker(ticker_symbol)
df_history = ticker_data.history(period="1y")

# Das Datum ist bei yfinance standardmäßig der Index.
# Wir setzen den Index zurück, damit 'Date' eine normale Spalte wird,
# was die Handhabung in Streamlit-Tabellen und -Charts oft vereinfacht.
df_history.reset_index(inplace=True)

# --- VISUALISIERUNG (DATA DUMP) ---

# 1. Rohtabelle anzeigen
st.subheader("Rohdaten (Tabelle)")
# st.dataframe zeigt die Daten interaktiv (sortierbar, scrollbar) an
st.dataframe(df_history)

# 2. Simpler Line-Chart für den Schlusskurs (Close)
st.subheader("Schlusskurs-Verlauf")
# Streamlit bringt st.line_chart mit, ideal für schnelle Prototypen
st.line_chart(df_history, x="Date", y="Close")

# 3. Simpler Bar-Chart für das Handelsvolumen (Volume)
st.subheader("Handelsvolumen")
st.bar_chart(df_history, x="Date", y="Volume")