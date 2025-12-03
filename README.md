
# NIFTY50 3-minute Momentum Screener (Streamlit)

This is a ready-to-deploy Streamlit application that scans NIFTY50 tickers (Yahoo Finance .NS suffix) using 3-minute intraday data and computes short-term and long-term momentum signals.

## Files
- `app.py` — main Streamlit app
- `requirements.txt` — Python dependencies

## Quick Deploy (Streamlit Cloud)
1. Create a free account at https://streamlit.io/cloud
2. Create a new repository on GitHub and push these files (`app.py`, `requirements.txt`, `README.md`).
3. In Streamlit Cloud, click **New app**, connect your GitHub, choose the repo and branch, set `app.py` as the file, and click **Deploy**.
4. Streamlit Cloud will provide a public URL (e.g. `https://your-app-name.streamlit.app`)

## Notes & Limits
- The app uses `yfinance` which has rate limits and may be slow for many tickers. Limit the scan size in the sidebar.
- For a production-grade app, consider caching, background workers, or a paid data provider / websockets.

