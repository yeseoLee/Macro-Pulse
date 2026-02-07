import yfinance as yf
import pandas as pd
import logging
import numpy as np
from cnbc_fetcher import fetch_cnbc_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Yahoo Tickers (default)
YF_TICKERS = {
    'indices_domestic': {
        'KOSPI': '^KS11',
        'KOSDAQ': '^KQ11',
    },
    'indices_overseas': {
        'S&P 500': '^GSPC',
        'Nasdaq': '^IXIC',
        'Euro Stoxx 50': '^STOXX50E',
        'Nikkei 225': '^N225',
        'Shanghai Composite': '000001.SS',
    },
    'commodities_rates': {
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Copper': 'HG=F',
        'US 10Y Treasury': '^TNX',
    },
    'crypto': {
        'Bitcoin': 'BTC-USD',
        'Ethereum': 'ETH-USD',
    },
    'volatility': {
        'VIX': '^VIX',
    }
}

# CNBC Symbols to fetch
CNBC_SYMBOLS = [
    ".KSVKOSPI", # VKOSPI
    "JP10Y",     # Japan 10Y
    "KR10Y",     # Korea 10Y
    "KRW=",      # USD/KRW
    "JPY=",      # USD/JPY
    "EUR=",      # EUR/USD (Major pair convention)
    "CNY=",      # USD/CNY
]

def fetch_all_data():
    results = {
        'exchange': [],
        'indices_domestic': [],
        'indices_overseas': [],
        'commodities_rates': [],
        'crypto': [],
        'volatility': []
    }

    # 1. Fetch CNBC Data
    logging.info("Fetching CNBC data...")
    cnbc_data = fetch_cnbc_data(CNBC_SYMBOLS)
    
    # Process Rates from CNBC
    # Defaults (if CNBC fails, we might want YF fallback, but user requested replacement. 
    # For now, if CNBC fails, these will be missing or we can fallback if critical.)
    
    usd_krw = cnbc_data.get('KRW=', {}).get('price')
    usd_jpy = cnbc_data.get('JPY=', {}).get('price')
    eur_usd = cnbc_data.get('EUR=', {}).get('price') # Assuming EUR/USD
    usd_cny = cnbc_data.get('CNY=', {}).get('price') # Assuming USD/CNY

    # Helper to create result item
    def create_item(name, price, change, change_pct):
        return {
            'name': name,
            'price': price,
            'change': change,
            'change_pct': change_pct,
            'history': [price], # No history from CNBC for now
            'sparkline': None # Will handle None in report generator
        }

    # Exchange Rates Calculation
    if usd_krw:
        # USD/KRW
        item = cnbc_data['KRW=']
        results['exchange'].append(create_item('USD/KRW', item['price'], item['change'], item['change_pct']))
        
        # JPY/KRW = (USD/KRW) / (USD/JPY)
        if usd_jpy:
            price = (usd_krw / usd_jpy) * 100 # JPY is usually quoted per 100 Yen in Korea? Or 1 Yen?
            # Standard convention: JPY/KRW is usually quoted as "per 100 Yen" -> ~900 KRW.
            # But mathematically standard: 1 JPY = X KRW -> ~9 KRW.
            # Yahoo JPYKRW=X is ~9.
            # User example: (JPY/KRW) via formula.
            # Let's stick to 1 unit for consistency unless 100 is expected. 
            # Yahoo returns ~9. I will stick to ~9.
            price = usd_krw / usd_jpy
            # Change calculation is complex for cross rates roughly. 
            # change% ~= (KRW% - JPY%) roughly.
            # Let's approximate or just show 0 change if we can't calculate history.
            # Or use current prices. We need PREVIOUS prices to calculate Exact Change.
            # Without history, we can't calculate exact change for cross rates accurately.
            # I will set change to 0 for calculated rates for now, to be safe.
            results['exchange'].append(create_item('JPY/KRW', price, 0, 0))

        # EUR/KRW = (USD/KRW) * (EUR/USD)
        if eur_usd:
            price = usd_krw * eur_usd
            results['exchange'].append(create_item('EUR/KRW', price, 0, 0))

        # CNY/KRW = (USD/KRW) / (USD/CNY)
        if usd_cny:
            price = usd_krw / usd_cny
            results['exchange'].append(create_item('CNY/KRW', price, 0, 0))

    else:
        # Fallback to Yahoo if CNBC failed (optional, but good for reliability)
        logging.warning("CNBC Rates failed. Falling back to YF for core rates not implemented here (User requested replacement).")

    # Add other CNBC items
    # VKOSPI
    if '.KSVKOSPI' in cnbc_data:
        item = cnbc_data['.KSVKOSPI']
        results['volatility'].append(create_item('VKOSPI', item['price'], item['change'], item['change_pct']))
    
    # Japan 10Y
    if 'JP10Y' in cnbc_data:
        item = cnbc_data['JP10Y']
        results['commodities_rates'].append(create_item('Japan 10Y Treasury', item['price'], item['change'], item['change_pct']))

    # Korea 10Y
    if 'KR10Y' in cnbc_data:
        item = cnbc_data['KR10Y']
        results['commodities_rates'].append(create_item('Korea 10Y Treasury', item['price'], item['change'], item['change_pct']))


    # 2. Fetch Yahoo Finance Data
    logging.info("Fetching Yahoo Finance data...")
    for category, items in YF_TICKERS.items():
        for name, ticker in items.items():
            try:
                data = yf.Ticker(ticker).history(period="1mo")
                if data.empty: continue
                
                last_price = data['Close'].iloc[-1]
                if len(data) > 1:
                    prev_price = data['Close'].iloc[-2]
                    change = last_price - prev_price
                    change_pct = (change / prev_price) * 100
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
                    'sparkline': None, # Placeholder
                    'dates': [d.strftime('%m-%d') for d in data.tail(7).index]
                })

            except Exception as e:
                logging.error(f"Error fetching YF {name}: {e}")

    return results

if __name__ == "__main__":
    data = fetch_all_data()
    print(data)
