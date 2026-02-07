import yfinance as yf

tickers = {
    'USD/KRW': 'KRW=X',
    'JPY/KRW': 'JPYKRW=X',
    'S&P 500': '^GSPC',
    'Nasdaq': '^IXIC',
    'Nikkei 225': '^N225',
    'Euro Stoxx 50': '^STOXX50E', # Added
    'Shanghai Composite': '000001.SS',
    'KOSPI': '^KS11',
    'KOSDAQ': '^KQ11',
    'Gold': 'GC=F',
    'US 10Y': '^TNX',
    'Bitcoin': 'BTC-USD',
    'VIX': '^VIX',
    # Problematic tickers (kept for reference)
    # 'Japan 10Y': 'JP10YT=XX', 
    # 'Korea 10Y': 'KR10YT=RR', 
    # 'VKOSPI': '^VKOSPI' 
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
