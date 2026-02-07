import yfinance as yf
import pandas as pd

tickers = {
    'USD/KRW': 'KRW=X',
    'JPY/KRW': 'JPYKRW=X',
    'S&P 500': '^GSPC',
    'Nikkei 225': '^N225',
    'Shanghai Composite': '000001.SS',
    'KOSPI': '^KS11',
    'KOSDAQ': '^KQ11',
    'Gold': 'GC=F',
    'US 10Y': '^TNX',
    'Japan 10Y': 'JP10Y', # Testing without ^
    'Bitcoin': 'BTC-USD',
    'VIX': '^VIX',
    'VKOSPI': 'KSVKOSPI' # Testing this from search
}

print("Testing tickers...")
for name, ticker in tickers.items():
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            print(f"[OK] {name} ({ticker}): {data['Close'].iloc[-1]}")
        else:
            print(f"[FAIL] {name} ({ticker}): No data")
    except Exception as e:
        print(f"[ERROR] {name} ({ticker}): {e}")
