import math
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd


sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from macro_pulse.data import market_data
from macro_pulse.domain.models import TickerDefinition


def make_history(values):
    index = pd.date_range("2026-08-01", periods=len(values), freq="D")
    return pd.DataFrame({"Close": values}, index=index)


class YahooSnapshotNanTests(unittest.TestCase):
    @patch.dict(
        market_data.YF_TICKERS,
        {"indices_domestic": (TickerDefinition("KOSPI", "^KS11"),)},
        clear=True,
    )
    @patch("macro_pulse.data.market_data.yf.Ticker")
    def test_trailing_nan_close_falls_back_to_last_valid_price(self, mock_ticker):
        # Yahoo Finance sometimes returns a not-yet-populated bar for the
        # current session, which previously produced "nan" in the report.
        history = make_history([2600.0, 2610.0, 2605.0, math.nan])

        ticker = MagicMock()
        ticker.history.return_value = history
        mock_ticker.return_value = ticker

        results = market_data._empty_report_dataset()
        market_data._append_yahoo_snapshots(results)

        self.assertEqual(len(results["indices_domestic"]), 1)
        snapshot = results["indices_domestic"][0]

        self.assertEqual(snapshot.name, "KOSPI")
        self.assertAlmostEqual(snapshot.price, 2605.0)
        self.assertAlmostEqual(snapshot.change, -5.0)
        self.assertAlmostEqual(snapshot.change_pct, (-5.0 / 2610.0) * 100)
        self.assertNotIn(math.nan, snapshot.history)

    @patch.dict(
        market_data.YF_TICKERS,
        {"indices_domestic": (TickerDefinition("KOSPI", "^KS11"),)},
        clear=True,
    )
    @patch("macro_pulse.data.market_data.yf.Ticker")
    def test_all_nan_history_is_skipped(self, mock_ticker):
        history = make_history([math.nan, math.nan])

        ticker = MagicMock()
        ticker.history.return_value = history
        mock_ticker.return_value = ticker

        results = market_data._empty_report_dataset()
        market_data._append_yahoo_snapshots(results)

        self.assertEqual(results["indices_domestic"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
