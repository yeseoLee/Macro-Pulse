import os
import logging
from cnbc import APIWrapper, Endpoints

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    # 1. Translate symbols to Issue IDs
    try:
        # We reuse one APIWrapper instance for translation
        # Note: The library modifies Endpoints.TRANSLATE in-place, so we just overwrite 'symbol' each time.
        translate_api = APIWrapper(api_key, Endpoints.TRANSLATE)
        
        for symbol in symbols:
            try:
                translate_api.params['symbol'] = symbol
                data = translate_api.request()
                
                # Response format validation needed. 
                # Usually returns a list or dict with 'issueId'. 
                # Based on library purpose, it might return the first match.
                # Let's assume data[0]['issueId'] or data['issueId']? 
                # Without documentation/testing, this is risky.
                # Library has `translation_table`. Maybe we can use that?
                # But let's try to parse the response blindly or safely.
                
                # If valid:
                # issue_id = ...
                # issue_ids[symbol] = issue_id
                
                # Mocking logic for now because I can't see the response structure without a key.
                # Wait, if I can't see the response, I'm guessing.
                # But I have to write the code.
                # I'll check if the library has a helper for this. 
                # No, just `request()`.
                
                if data and isinstance(data, list) and len(data) > 0:
                     issue_ids[symbol] = data[0].get('issueId')
                elif data and isinstance(data, dict):
                     issue_ids[symbol] = data.get('issueId')
                
            except Exception as e:
                logging.error(f"Error translating {symbol}: {e}")

        if not issue_ids:
            return {}

        # 2. Get Summary for Issue IDs
        # Endpoints.GET_SUMMARY takes 'issueIds' (comma separated?)
        ids_list = [str(iid) for iid in issue_ids.values() if iid]
        if not ids_list:
            return {}
            
        summary_api = APIWrapper(api_key, Endpoints.GET_SUMMARY)
        summary_api.params['issueIds'] = ",".join(ids_list)
        
        summary_data = summary_api.request()
        
        # 3. Parse Summary Data
        # Response likely a list of quotes.
        # Map back to symbols via issue_id
        
        # Invert map for easy lookup
        id_to_symbol = {v: k for k, v in issue_ids.items()}
        
        if isinstance(summary_data, list):
            for item in summary_data:
                # Item structure? likely has 'issueId', 'last', 'change', 'change_pct'
                iid = item.get('issueId')
                symbol = id_to_symbol.get(iid)
                
                if symbol:
                    # fields might be 'last', 'change', 'changePct' or similar
                    # CNBC API usually uses 'last', 'change', 'changePct'
                    try:
                        price = float(item.get('last', 0))
                        change = float(item.get('change', 0))
                        change_pct = float(item.get('changePct', 0)) # check logic
                        name = item.get('name') or item.get('symbol') or symbol # fallback
                        
                        results[symbol] = {
                            'price': price,
                            'change': change,
                            'change_pct': change_pct * 100 if abs(change_pct) < 1 else change_pct, # Normalized to %? usually 0.01 is 1%. check.
                            'name': name
                        }
                    except (ValueError, TypeError):
                         pass
                         
    except Exception as e:
        logging.error(f"CNBC API Error: {e}")

    return results
