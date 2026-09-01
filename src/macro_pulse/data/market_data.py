import os
import tempfile

import yfinance as yf

from ..core.logging import get_logger
from ..domain.models import (
    ReportDataset,
    TickerDefinition,
    ValueFormat,
    coerce_cnbc_quote,
)
from .exchange_rates import build_exchange_snapshots
from .providers.cnbc import CNBC_FX_SYMBOLS, CNBC_MARKET_SYMBOLS, fetch_cnbc_data
from .snapshots import build_snapshot


logger = get_logger(__name__)


YF_TICKERS = {
    "indices_domestic": (
        TickerDefinition("KOSPI", "^KS11"),
        TickerDefinition("KOSDAQ", "^KQ11"),
    ),
    "indices_overseas": (
        TickerDefinition("S&P 500", "^GSPC"),
        TickerDefinition("Nasdaq", "^IXIC"),
        TickerDefinition("Euro Stoxx 50", "^STOXX50E"),
        TickerDefinition("Nikkei 225", "^N225"),
        TickerDefinition("Hang Seng", "^HSI"),
        TickerDefinition("Shanghai Composite", "000001.SS"),
    ),
    "commodities_rates": (
        TickerDefinition("Gold", "GC=F"),
        TickerDefinition("Silver", "SI=F"),
        TickerDefinition("Copper", "HG=F"),
        TickerDefinition("US 10Y Treasury", "^TNX", value_format=ValueFormat.YIELD_3),
    ),
    "crypto": (
        TickerDefinition("Bitcoin", "BTC-USD"),
        TickerDefinition("Ethereum", "ETH-USD"),
    ),
    "volatility": (TickerDefinition("VIX", "^VIX"),),
}

YF_RATES_HISTORY = {
    "USD/KRW": "KRW=X",
    "JPY/KRW": "JPYKRW=X",
    "EUR/KRW": "EURKRW=X",
}


def fetch_all_data() -> ReportDataset:
    _configure_runtime_cache()
    results = _empty_report_dataset()

    yf_rates_data = _fetch_rate_histories()

    logger.info("Fetching CNBC data...")
    cnbc_data = fetch_cnbc_data([*CNBC_MARKET_SYMBOLS, *CNBC_FX_SYMBOLS])
    results["exchange"].extend(build_exchange_snapshots(cnbc_data, yf_rates_data))
    _append_cnbc_market_snapshots(results, cnbc_data)

    logger.info("Fetching Yahoo Finance data...")
    _append_yahoo_snapshots(results)
    _reorder_bond_snapshots(results["commodities_rates"])

    logger.info(
        "Completed fetch cycle with %s populated categories",
        sum(1 for items in results.values() if items),
    )

    return results


def _empty_report_dataset() -> ReportDataset:
    return {
        "indices_domestic": [],
        "indices_overseas": [],
        "volatility": [],
        "commodities_rates": [],
        "exchange": [],
        "crypto": [],
    }


def _fetch_rate_histories():
    histories = {}
    logger.info("Fetching YF rates history...")
    for name, ticker in YF_RATES_HISTORY.items():
        try:
            history = yf.Ticker(ticker).history(period="1mo")
            if not history.empty:
                histories[name] = history
        except Exception as exc:
            logger.error("Error fetching YF history for %s: %s", name, exc)
    return histories


def _append_cnbc_market_snapshots(results: ReportDataset, cnbc_data) -> None:
    for symbol, category, value_format in (
        (".KSVKOSPI", "volatility", ValueFormat.STANDARD_2),
        ("JP10Y", "commodities_rates", ValueFormat.YIELD_3),
        ("KR10Y", "commodities_rates", ValueFormat.YIELD_3),
    ):
        quote = cnbc_data.get(symbol)
        if quote is None:
            continue

        item = coerce_cnbc_quote(quote)
        results[category].append(
            build_snapshot(
                item.name,
                item.price,
                item.change,
                item.change_pct,
                value_format=value_format,
            )
        )


def _append_yahoo_snapshots(results: ReportDataset) -> None:
    for category, definitions in YF_TICKERS.items():
        for definition in definitions:
            try:
                data = yf.Ticker(definition.symbol).history(period="1mo")
                closes = data["Close"].dropna()
                if closes.empty:
                    logger.warning(
                        "Yahoo Finance returned no valid close prices for %s (%s)",
                        definition.name,
                        definition.symbol,
                    )
                    continue

                last_price = float(closes.iloc[-1])
                if len(closes) > 1:
                    previous_price = float(closes.iloc[-2])
                    change = last_price - previous_price
                    change_pct = (change / previous_price) * 100
                else:
                    change = 0.0
                    change_pct = 0.0

                results[category].append(
                    build_snapshot(
                        definition.name,
                        last_price,
                        change,
                        change_pct,
                        history=closes.tail(7).tolist(),
                        ticker=definition.symbol,
                        dates=[date.strftime("%m-%d") for date in closes.tail(7).index],
                        value_format=definition.value_format,
                    )
                )
            except Exception as exc:
                logger.error("Error fetching YF %s: %s", definition.name, exc)


def _reorder_bond_snapshots(commodities_rates) -> None:
    us_10y_index = next(
        (
            index
            for index, item in enumerate(commodities_rates)
            if item.name == "US 10Y Treasury"
        ),
        None,
    )
    korea_10y_index = next(
        (
            index
            for index, item in enumerate(commodities_rates)
            if item.name == "Korea 10Y Treasury"
        ),
        None,
    )

    if us_10y_index is None or korea_10y_index is None:
        return

    us_10y_snapshot = commodities_rates.pop(us_10y_index)
    korea_10y_index = next(
        (
            index
            for index, item in enumerate(commodities_rates)
            if item.name == "Korea 10Y Treasury"
        ),
        None,
    )
    if korea_10y_index is None:
        commodities_rates.append(us_10y_snapshot)
        return

    commodities_rates.insert(korea_10y_index + 1, us_10y_snapshot)


def _configure_runtime_cache() -> None:
    cache_dir = os.environ.get(
        "YFINANCE_CACHE_DIR",
        os.path.join(tempfile.gettempdir(), "macro-pulse-yfinance"),
    )
    os.makedirs(cache_dir, exist_ok=True)
    if hasattr(yf, "set_tz_cache_location"):
        yf.set_tz_cache_location(cache_dir)
