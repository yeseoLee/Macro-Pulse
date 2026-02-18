import yfinance as yf
import pandas as pd
import logging
import numpy as np
from cnbc_fetcher import fetch_cnbc_data

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Yahoo Tickers (default)
YF_TICKERS = {
    "indices_domestic": {
        "KOSPI": "^KS11",
        "KOSDAQ": "^KQ11",
    },
    "indices_overseas": {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Euro Stoxx 50": "^STOXX50E",
        "Nikkei 225": "^N225",
        "Hang Seng": "^HSI",  # Added
        "Shanghai Composite": "000001.SS",
    },
    "commodities_rates": {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Copper": "HG=F",
        "US 10Y Treasury": "^TNX",
    },
    "crypto": {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
    },
    "volatility": {
        "VIX": "^VIX",
    },
}

# YF Tickers for Exchange Rates History (Hybrid Approach)
YF_RATES_HISTORY = {
    "USD/KRW": "KRW=X",
    "JPY/KRW": "JPYKRW=X",
    "EUR/KRW": "EURKRW=X",
}

# CNBC Symbols to fetch
CNBC_SYMBOLS = [
    ".KSVKOSPI",  # VKOSPI
    "JP10Y",  # Japan 10Y
    "KR10Y",  # Korea 10Y
    "KRW=",  # USD/KRW
    "JPY=",  # USD/JPY
    "EUR=",  # EUR/USD (Major pair convention)
    "CNY=",  # USD/CNY
]


def fetch_all_data():
    results = {
        "indices_domestic": [],
        "indices_overseas": [],
        "volatility": [],
        "commodities_rates": [],
        "exchange": [],
        "crypto": [],
    }

    # 0. Fetch YF History for Rates (for Trend/Change)
    yf_rates_data = {}
    logging.info("Fetching YF Rates History...")
    for name, ticker in YF_RATES_HISTORY.items():
        try:
            hist = yf.Ticker(ticker).history(period="1mo")
            if not hist.empty:
                yf_rates_data[name] = hist
        except Exception as e:
            logging.error(f"Error fetching YF history for {name}: {e}")

    # 1. Fetch CNBC Data
    logging.info("Fetching CNBC data...")
    cnbc_data = fetch_cnbc_data(CNBC_SYMBOLS)

    # Process Rates from CNBC
    usd_krw = cnbc_data.get("KRW=", {}).get("price")
    usd_jpy = cnbc_data.get("JPY=", {}).get("price")
    eur_usd = cnbc_data.get("EUR=", {}).get("price")
    usd_cny = cnbc_data.get("CNY=", {}).get("price")

    # Helper to create result item
    def create_item(name, price, change, change_pct, history=None, use_blank=False):
        if use_blank:
            change = None
            change_pct = None
            history = []

        sparkline = None  # Handled in report generator
        return {
            "name": name,
            "price": price,
            "change": change,
            "change_pct": change_pct,
            "history": history if history is not None else [price] if price else [],
            "sparkline": sparkline,
        }

    # Exchange Rates Calculation
    if usd_krw:
        # USD/KRW
        # Hybrid: Use CNBC Price, but YF History/Change if available
        yf_hist = yf_rates_data.get("USD/KRW")
        price = usd_krw
        change = cnbc_data["KRW="]["change"]
        change_pct = cnbc_data["KRW="]["change_pct"]
        history = [price]

        if yf_hist is not None and not yf_hist.empty:
            history = yf_hist["Close"].tail(7).tolist()
            prev_close = yf_hist["Close"].iloc[-2] if len(yf_hist) > 1 else price
            change = price - prev_close
            change_pct = (change / prev_close) * 100

        results["exchange"].append(
            create_item("USD/KRW", price, change, change_pct, history)
        )

        # JPY/KRW
        if usd_jpy:
            price_jpykrw = (usd_krw / usd_jpy) * 100  # JPY/KRW (100 Yen)
            # Default CNBC change logic roughly
            change = 0
            change_pct = 0
            history = [price_jpykrw]

            # Hybrid YF
            yf_hist = yf_rates_data.get("JPY/KRW")
            if yf_hist is not None and not yf_hist.empty:
                # Yahoo Finance JPYKRW=X is per 1 JPY (~9.x), but we use per 100 JPY (~9xx).
                # Scale YF history by 100
                history_scaled = yf_hist["Close"] * 100
                history = history_scaled.tail(7).tolist()
                prev_close = (
                    history_scaled.iloc[-2] if len(history_scaled) > 1 else price_jpykrw
                )
                change = price_jpykrw - prev_close
                change_pct = (change / prev_close) * 100

            results["exchange"].append(
                create_item("JPY/KRW", price_jpykrw, change, change_pct, history)
            )

        # EUR/KRW
        if eur_usd:
            price_eurkrw = usd_krw * eur_usd
            change = 0
            change_pct = 0
            history = [price_eurkrw]

            # Hybrid YF
            yf_hist = yf_rates_data.get("EUR/KRW")
            if yf_hist is not None and not yf_hist.empty:
                history = yf_hist["Close"].tail(7).tolist()
                prev_close = (
                    yf_hist["Close"].iloc[-2] if len(yf_hist) > 1 else price_eurkrw
                )
                change = price_eurkrw - prev_close
                change_pct = (change / prev_close) * 100

            results["exchange"].append(
                create_item("EUR/KRW", price_eurkrw, change, change_pct, history)
            )

        # CNY/KRW (Blank Change/Trend)
        if usd_cny:
            price = usd_krw / usd_cny
            results["exchange"].append(
                create_item("CNY/KRW", price, 0, 0, use_blank=True)
            )

    else:
        logging.warning("CNBC Rates failed. Data might be incomplete.")

    # Add other CNBC items (Blank Change/Trend)
    # VKOSPI
    if ".KSVKOSPI" in cnbc_data:
        item = cnbc_data[".KSVKOSPI"]
        results["volatility"].append(
            create_item("VKOSPI", item["price"], 0, 0, use_blank=True)
        )

    # Japan 10Y
    if "JP10Y" in cnbc_data:
        item = cnbc_data["JP10Y"]
        results["commodities_rates"].append(
            create_item("Japan 10Y Treasury", item["price"], 0, 0, use_blank=True)
        )

    # Korea 10Y
    if "KR10Y" in cnbc_data:
        item = cnbc_data["KR10Y"]
        results["commodities_rates"].append(
            create_item("Korea 10Y Treasury", item["price"], 0, 0, use_blank=True)
        )

    # 2. Fetch Yahoo Finance Data
    logging.info("Fetching Yahoo Finance data...")
    for category, items in YF_TICKERS.items():
        for name, ticker in items.items():
            try:
                data = yf.Ticker(ticker).history(period="1mo")
                if data.empty:
                    continue

                last_price = data["Close"].iloc[-1]
                if len(data) > 1:
                    prev_price = data["Close"].iloc[-2]
                    change = last_price - prev_price
                    change_pct = (change / prev_price) * 100
                    history = data["Close"].tail(7).tolist()
                else:
                    change = 0
                    change_pct = 0
                    history = [last_price]

                results[category].append(
                    {
                        "name": name,
                        "ticker": ticker,
                        "price": last_price,
                        "change": change,
                        "change_pct": change_pct,
                        "history": history,
                        "sparkline": None,  # Placeholder
                        "dates": [d.strftime("%m-%d") for d in data.tail(7).index],
                    }
                )

            except Exception as e:
                logging.error(f"Error fetching YF {name}: {e}")

    # Reorder commodities_rates to ensure US 10Y is after Korea 10Y (Group Bonds)
    # Target Order: Japan 10Y, Korea 10Y, US 10Y, others...
    # Actually, let's just find US 10Y and move it to after Korea 10Y if both exist.

    cr_list = results["commodities_rates"]
    us_10y_idx = next(
        (i for i, x in enumerate(cr_list) if x["name"] == "US 10Y Treasury"), None
    )
    korea_10y_idx = next(
        (i for i, x in enumerate(cr_list) if x["name"] == "Korea 10Y Treasury"), None
    )

    if us_10y_idx is not None and korea_10y_idx is not None:
        # Move US 10Y to korea_10y_idx + 1
        item = cr_list.pop(us_10y_idx)
        # Re-calculate index of Korea because pop might have shifted it if US was before (unlikely)
        korea_10y_idx = next(
            (i for i, x in enumerate(cr_list) if x["name"] == "Korea 10Y Treasury"),
            None,
        )
        if korea_10y_idx is not None:
            cr_list.insert(korea_10y_idx + 1, item)
        else:
            cr_list.append(item)  # Fallback

    return results


if __name__ == "__main__":
    data = fetch_all_data()
    print(data)
