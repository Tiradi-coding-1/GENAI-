"""
data_fetcher 測試檔
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_fetcher import (
    AI_COOLING,
    AI_SERVER,
    DATA_DIR,
    HISTORY_DAYS,
    MAX_RETRIES,
    WAFER_FOUNDRY,
    fetch_group_data,
    fetch_stock_data,
)


class TestConstants:
    """測試常數定義"""

    def test_stock_groups_not_empty(self):
        assert len(WAFER_FOUNDRY) == 5
        assert len(AI_SERVER) == 5
        assert len(AI_COOLING) == 5

    def test_ticker_format(self):
        for ticker in WAFER_FOUNDRY + AI_SERVER + AI_COOLING:
            assert ticker.endswith(".TW")

    def test_data_dir_exists(self):
        assert DATA_DIR.exists()


class TestFetchStockData:
    """測試 fetch_stock_data 函式"""

    @patch("data_fetcher.yf.Ticker")
    def test_fetch_stock_data_success(self, mock_ticker):
        mock_df = pd.DataFrame({
            "Date": pd.to_datetime(["2024-10-01", "2024-10-02"]),
            "Open": [980.0, 985.0],
            "High": [995.0, 1000.0],
            "Low": [975.0, 980.0],
            "Close": [990.0, 995.0],
            "Volume": [25000000, 23000000],
        })
        mock_stock = MagicMock()
        mock_stock.history.return_value = mock_df
        mock_ticker.return_value = mock_stock

        result = fetch_stock_data("2330.TW", days=10)

        assert result is not None
        assert "Stock_ID" in result.columns
        assert result["Stock_ID"].iloc[0] == "2330.TW"

    @patch("data_fetcher.yf.Ticker")
    def test_fetch_stock_data_empty(self, mock_ticker):
        mock_stock = MagicMock()
        mock_stock.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_stock

        result = fetch_stock_data("9999.TW")

        assert result is None


class TestFetchGroupData:
    """測試 fetch_group_data 函式"""

    @patch("data_fetcher.fetch_stock_data")
    @patch("data_fetcher.time.sleep")
    def test_fetch_group_data(self, mock_sleep, mock_fetch):
        mock_df = pd.DataFrame({
            "Date": ["2024-10-01"],
            "Stock_ID": ["2330.TW"],
            "Open": [980.0],
            "High": [995.0],
            "Low": [975.0],
            "Close": [990.0],
            "Volume": [25000000],
        })
        mock_fetch.return_value = mock_df

        output_path = DATA_DIR / "test_group.csv"
        result = fetch_group_data(["2330.TW"], output_path)

        assert output_path.exists()
        assert len(result) > 0
        output_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])