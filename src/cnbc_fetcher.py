import os
import logging
from cnbc import APIWrapper, Endpoints

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Manual mapping for symbols that fail translation or to speed up
MANUAL_ISSUE_IDS = {
    "KR10Y": "6328006",
    "JP10Y": "5767339",
    "JP10Y-JP": "5767339",
    ".KSVKOSPI": "18105291",
    "KRW=": "611656",  # USD/KRW
    "JPY=": "616660",  # USD/JPY
    "EUR=": "617254",  # EUR/USD
    "CNY=": "612178",  # USD/CNY
    # Note: If translate works, this overrides. Prioritize manual map for reliability.
}


def fetch_cnbc_data(symbols):
    """
    Fetches data from CNBC via RapidAPI.
    symbols: list of ticker strings (e.g., [".KSVKOSPI", "KRW=", ...])
    Returns: dict {symbol: {'price': float, 'change': float, 'change_pct': float, 'name': str}}
    """
    api_key = os.environ.get("RAPIDAPI_CNBC_KEY")
    if not api_key:
        logging.warning("RAPIDAPI_CNBC_KEY not found. Skipping CNBC data fetch.")
        return {}

    results = {}
    issue_ids = {}
    symbols_to_translate = []

    # 1. Resolve Issue IDs (Manual + Translate)
    for symbol in symbols:
        if symbol in MANUAL_ISSUE_IDS:
            issue_ids[symbol] = MANUAL_ISSUE_IDS[symbol]
        else:
            symbols_to_translate.append(symbol)

    if symbols_to_translate:
        try:
            translate_api = APIWrapper(api_key, Endpoints.TRANSLATE)

            for symbol in symbols_to_translate:
                try:
                    # logging.info(f"Translating {symbol}...")
                    translate_api.params["symbol"] = symbol
                    data = translate_api.request()

                    if data and isinstance(data, list) and len(data) > 0:
                        issue_ids[symbol] = data[0].get("issueId")
                    elif data and isinstance(data, dict):
                        issue_ids[symbol] = data.get("issueId")
                    else:
                        logging.warning(f"No translation found for {symbol}")

                except Exception as e:
                    logging.error(f"Error translating {symbol}: {e}")

        except Exception as e:
            logging.error(f"CNBC Translate Error: {e}")

    if not issue_ids:
        return {}

    # 2. Get Summary for Issue IDs
    try:
        # Endpoints.GET_SUMMARY takes 'issueIds'
        ids_list = [str(iid) for iid in issue_ids.values() if iid]
        if not ids_list:
            return {}

        summary_api = APIWrapper(api_key, Endpoints.GET_SUMMARY)
        summary_api.params["issueIds"] = ",".join(ids_list)

        summary_data = summary_api.request()

        if isinstance(summary_data, dict) and "ITVQuoteResult" in summary_data:
            summary_data = summary_data["ITVQuoteResult"].get("ITVQuote", [])

        # If single item, it might be a dict, not list?
        if isinstance(summary_data, dict):
            summary_data = [summary_data]

        # 3. Parse Summary Data
        # Response is list of dicts.
        # Create issueId -> symbol map (handling many-to-one if any?)

        # Create a lookup from issueId to data
        data_by_id = {}
        if isinstance(summary_data, list):
            for item in summary_data:
                # API returns 'issue_id' (snake), translate returned 'issueId' (camel)
                iid = str(item.get("issue_id") or item.get("issueId"))
                if iid:
                    data_by_id[iid] = item

        for symbol, iid in issue_ids.items():
            iid = str(iid)
            if iid in data_by_id:
                item = data_by_id[iid]
                try:
                    # Helper to clean string numbers
                    def clean_num(val):
                        if isinstance(val, str):
                            if val.strip().upper() == "UNCH":
                                return 0.0
                            val = val.replace("%", "").replace(",", "")
                        return float(val)

                    price = clean_num(item.get("last", 0))
                    change = clean_num(item.get("change", 0))
                    change_pct = clean_num(
                        item.get("change_pct") or item.get("changePct") or 0
                    )

                    # Normalized to %?
                    # If string was "1.40%", clean_num makes it 1.40.
                    # If Yahoo uses 1.40 for 1.40%, then it's consistent.
                    # Verify yahoo: change_pct: -1.44 (which is -1.44%).
                    # So 1.40 is correct.
                    # But if API returns raw 0.014...
                    # Step 353 log: "change_pct": "-1.40%". So cleaning gives -1.40. Perfect.
                    # What if no % sign? "change_pct" field name implies %.

                    name = item.get("name") or item.get("symbol") or symbol

                    results[symbol] = {
                        "price": price,
                        "change": change,
                        "change_pct": change_pct,
                        "name": name,
                    }
                except (ValueError, TypeError) as e:
                    logging.warning(f"Error parsing item for {symbol}: {e}")
                    pass

    except Exception as e:
        logging.error(f"CNBC Summary API Error: {e}")

    return results
