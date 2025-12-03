import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="NIFTY50 3-min Momentum Screener", layout="wide")
st.title("📊 NIFTY50 — 3-minute Momentum Screener (Multi-stock)")

# Default NIFTY50 tickers (Yahoo Finance .NS suffix)
TICKERS = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","HINDUNILVR.NS","ICICIBANK.NS","KOTAKBANK.NS",
    "LT.NS","ITC.NS","SBIN.NS","AXISBANK.NS","BHARTIARTL.NS","HCLTECH.NS","ASIANPAINT.NS","BAJAJ-AUTO.NS",
    "MARUTI.NS","SUNPHARMA.NS","NESTLEIND.NS","HDFC.NS","ULTRACEMCO.NS","TITAN.NS","DIVISLAB.NS","POWERGRID.NS",
    "ADANIENT.NS","ONGC.NS","TATAMOTORS.NS","TATASTEEL.NS","WIPRO.NS","BRITANNIA.NS","COALINDIA.NS","BPCL.NS",
    "INDUSINDBK.NS","JSWSTEEL.NS","GRASIM.NS","NTPC.NS","HDFCLIFE.NS","BANDHANBNK.NS","M&M.NS","TECHM.NS",
    "EICHERMOT.NS","SBILIFE.NS","AMBUJACEM.NS","CIPLA.NS","HINDALCO.NS","ADANIPORTS.NS","GAIL.NS","PIDILITIND.NS",
    "UPL.NS","SHREECEM.NS"
]

# Helper functions
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=period, min_periods=period).mean()
    ma_down = down.rolling(window=period, min_periods=period).mean()
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_ticker(ticker):
    out = {"ticker": ticker}
    try:
        # Fetch 3-minute intraday for last 3 days
        df_3m = yf.download(ticker, period="3d", interval="3m", progress=False, threads=False)
        df_1h = yf.download(ticker, period="7d", interval="60m", progress=False, threads=False)
        df_daily = yf.download(ticker, period="60d", interval="1d", progress=False, threads=False)
        
        if df_3m.empty:
            out.update({"error": "no 3m data"})
            return out

        # Short-term indicators (3m)
        close = df_3m["Close"]
        high = df_3m["High"]
        low = df_3m["Low"]
        vol = df_3m["Volume"] if "Volume" in df_3m else None

        EMA20 = ema(close, 20).iloc[-1]
        EMA50 = ema(close, 50).iloc[-1] if len(close) >= 50 else np.nan
        RSI14 = rsi(close, 14).iloc[-1]

        momentum_bullish = (RSI14 > 55) and (close.iloc[-1] > EMA20)
        trend_strong = (EMA20 > EMA50) if not np.isnan(EMA50) else False

        # Rising structure: last 3 highs and lows increasing
        rising_structure = False
        if len(high) >= 3:
            rising_structure = (high.iloc[-3] < high.iloc[-2] < high.iloc[-1]) and (low.iloc[-3] < low.iloc[-2] < low.iloc[-1])

        reversal_unexpected = (RSI14 < 40) or ((close.iloc[-1] < close.iloc[-2]) and (close.iloc[-2] > close.iloc[-3]))

        # Long-term indicators (1h)
        long_ema50 = np.nan
        long_ema200 = np.nan
        rising_structure_long = False
        trend_strong_long = False

        if not df_1h.empty:
            close_1h = df_1h["Close"]
            long_ema50 = ema(close_1h, 50).iloc[-1] if len(close_1h) >= 50 else np.nan
            long_ema200 = ema(close_1h, 200).iloc[-1] if len(close_1h) >= 200 else np.nan

            if len(close_1h) >= 3:
                h = df_1h["High"]
                l = df_1h["Low"]
                rising_structure_long = (h.iloc[-3] < h.iloc[-2] < h.iloc[-1]) and (l.iloc[-3] < l.iloc[-2] < l.iloc[-1])

            if not np.isnan(long_ema50) and not np.isnan(long_ema200):
                trend_strong_long = long_ema50 > long_ema200

        # Compose result
        out.update({
            "last_price": float(close.iloc[-1]),
            "momentum_bullish": bool(momentum_bullish),
            "trend_strong": bool(trend_strong),
            "rising_structure": bool(rising_structure),
            "reversal_unexpected": bool(reversal_unexpected),
            "rsi_14": float(RSI14) if not np.isnan(RSI14) else None,
            "ema20": float(EMA20) if not np.isnan(EMA20) else None,
            "ema50": float(EMA50) if not np.isnan(EMA50) else None,
            "long_rising_structure": bool(rising_structure_long),
            "long_trend_strong": bool(trend_strong_long),
            "long_ema50": float(long_ema50) if not np.isnan(long_ema50) else None,
            "long_ema200": float(long_ema200) if not np.isnan(long_ema200) else None,
            "delivery_pct": None
        })

        return out

    except Exception as e:
        out.update({"error": str(e)})
        return out

# Sidebar
st.sidebar.header("Scanner Settings")
tickers_input = st.sidebar.text_area("Tickers (comma separated). Leave empty for NIFTY50 default.", value="")
tickers = [t.strip() for t in tickers_input.split(",") if t.strip()] if tickers_input.strip() else TICKERS

max_scan = st.sidebar.number_input("Max tickers to scan (for speed)", min_value=1, max_value=len(tickers), value=20)
tickers = tickers[:max_scan]
refresh_button = st.sidebar.button("Run Scan")

st.write(f"Scanning {len(tickers)} tickers. (yfinance limits apply)")

if refresh_button:
    results = []
    with st.spinner("Scanning tickers one-by-one (this may take some time)..."):
        for t in tickers:
            r = analyze_ticker(t)
            results.append(r)

    df = pd.DataFrame(results)

    # Display table
    df_display = df[[
        "ticker","last_price","rsi_14","ema20","ema50",
        "momentum_bullish","trend_strong","rising_structure",
        "reversal_unexpected","long_rising_structure","long_trend_strong"
    ]]
    st.subheader("Results")
    st.dataframe(
        df_display.style.applymap(
            lambda v: 'background-color: #b6f0c2' if v==True else ('background-color: #ffd6d6' if v==False else ''),
            subset=[
                "momentum_bullish","trend_strong","rising_structure",
                "reversal_unexpected","long_rising_structure","long_trend_strong"
            ]
        ),
        height=600
    )

    # Filters
    st.subheader("Filtered: Momentum Bullish & Long Trend Strong")
    filtered = df[(df["momentum_bullish"]==True) & (df["long_trend_strong"]==True)]
    if not filtered.empty:
        st.table(filtered[["ticker","last_price","rsi_14","ema20","long_ema50","long_ema200"]])
    else:
        st.write("No tickers match the filter.")

    # CSV download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download results CSV", data=csv, file_name="nifty_screener_results.csv", mime="text/csv")
else:
    st.info("Click 'Run Scan' in the sidebar to start scanning.")
