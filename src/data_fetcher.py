import yfinance as yf
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TICKERS = {
    'exchange': {
        'USD/KRW': 'KRW=X',
        'JPY/KRW': 'JPYKRW=X',
        'EUR/KRW': 'EURKRW=X',
        'CNY/KRW': 'CNYKRW=X',
    },
    'indices_domestic': {
        'KOSPI': '^KS11',
        'KOSDAQ': '^KQ11',
    },
    'indices_overseas': {
        'S&P 500': '^GSPC',
        'Nasdaq': '^IXIC',
        'Euro Stoxx 50': '^STOXX50E', # Added
        'Nikkei 225': '^N225',
        'Shanghai Composite': '000001.SS',
        # 'Dow Jones': '^DJI', # Removed as requested
    },
    'commodities_rates': {
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Copper': 'HG=F',
        'US 10Y Treasury': '^TNX',
        # 'Japan 10Y Treasury': 'JP10YT=XX', # Not available on Yahoo Finance API
        # 'Korea 10Y Treasury': 'KR10YT=RR', # Not available on Yahoo Finance API
    },
    'crypto': {
        'Bitcoin': 'BTC-USD',
        'Ethereum': 'ETH-USD',
    },
    'volatility': {
        'VIX': '^VIX',
        # 'VKOSPI': '^VKOSPI', # Not available on Yahoo Finance API
    }
}

def fetch_all_data():
    """
    Fetches data for all defined tickers.
    Returns a dictionary structured by category, with dataframes for each ticker.
    Each dataframe will contain history for sparklines (e.g., 5 days) and current info.
    """
    results = {}
    
    for category, items in TICKERS.items():
        results[category] = []
        for name, ticker in items.items():
            try:
                # Fetch history for 5 days for sparklines and calculation
                # We fetch a bit more (7d) to ensure we have enough trading days
                data = yf.Ticker(ticker).history(period="1mo")
                
                if data.empty:
                    logging.warning(f"No data found for {name} ({ticker})")
                    continue
                
                # Calculate change
                last_price = data['Close'].iloc[-1]
                if len(data) > 1:
                    prev_price = data['Close'].iloc[-2]
                    change = last_price - prev_price
                    change_pct = (change / prev_price) * 100
                    
                    # Store 7 days of closing prices for the graph
                    history = data['Close'].tail(7).tolist()
                else:
                    change = 0
                    change_pct = 0
                    history = [last_price]

                results[category].append({
                    'name': name,
                    'ticker': ticker,
                    'price': last_price,
                    'change': change,
                    'change_pct': change_pct,
                    'history': history,
                    'dates': [d.strftime('%m-%d') for d in data.tail(7).index]
                })
                logging.info(f"Fetched {name}: {last_price:.2f}")

            except Exception as e:
                logging.error(f"Error fetching {name} ({ticker}): {e}")
                
    return results

if __name__ == "__main__":
    data = fetch_all_data()
    print(data)
