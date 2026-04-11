"""
視覺化模組測試

測試 K 線圖繪製功能。
"""

import os
import sys
import glob
import tempfile

import pytest
import pandas as pd
import numpy as np


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.visualizer import (
    STOCK_NAMES,
    STOCK_GROUPS,
    load_stock_data,
    calculate_ma,
    plot_group_chart,
    plot_all_groups,
)


class TestStockNames:
    """股票名稱對照測試"""

    def test_wafer_foundry_stocks(self):
        """驗證晶圓代工族群股票代號"""
        expected = ["2330.TW", "2303.TW", "3711.TW", "3037.TW", "6239.TW"]
        assert STOCK_GROUPS["wafer_foundry"] == expected

    def test_ai_server_stocks(self):
        """驗證 AI 伺服器族群股票代號"""
        expected = ["2317.TW", "2382.TW", "3231.TW", "6669.TW", "2356.TW"]
        assert STOCK_GROUPS["ai_server"] == expected

    def test_ai_cooling_stocks(self):
        """驗證 AI 散熱族群股票代號"""
        expected = ["3017.TW", "3324.TW", "2308.TW", "2421.TW", "2301.TW"]
        assert STOCK_GROUPS["ai_cooling"] == expected

    def test_all_stocks_have_names(self):
        """驗證所有股票代號都有對應名稱"""
        all_stocks = []
        for stocks in STOCK_GROUPS.values():
            all_stocks.extend(stocks)
        for stock_id in all_stocks:
            assert stock_id in STOCK_NAMES, f"Missing name for {stock_id}"


class TestLoadStockData:
    """資料載入測試"""

    def test_load_wafer_foundry_csv(self):
        """驗證可以載入晶圓代工 CSV"""
        csv_path = "data/wafer_foundry.csv"
        assert os.path.exists(csv_path), f"Missing {csv_path}"

    def test_load_ai_server_csv(self):
        """驗證可以載入 AI 伺服器 CSV"""
        csv_path = "data/ai_server.csv"
        assert os.path.exists(csv_path), f"Missing {csv_path}"

    def test_load_ai_cooling_csv(self):
        """驗證可以載入 AI 散熱 CSV"""
        csv_path = "data/ai_cooling.csv"
        assert os.path.exists(csv_path), f"Missing {csv_path}"

    def test_load_tsmc_data(self):
        """驗證可以載入台積電資料"""
        csv_path = "data/wafer_foundry.csv"
        df = load_stock_data(csv_path, "2330.TW")
        assert not df.empty, "Should load TSMc data"
        assert "Close" in df.columns
        assert "Volume" in df.columns


class TestCalculateMA:
    """均線計算測試"""

    def test_calculate_ma5(self):
        """驗證 MA5 計算"""
        df = pd.DataFrame({
            "Open": [100.0] * 10,
            "High": [105.0] * 10,
            "Low": [95.0] * 10,
            "Close": list(range(100, 110)),
            "Volume": [1000] * 10,
        })
        df = calculate_ma(df, windows=[5])
        assert "MA5" in df.columns
        assert pd.isna(df["MA5"].iloc[0])
        assert not pd.isna(df["MA5"].iloc[-1])

    def test_calculate_ma20(self):
        """驗證 MA20 計算"""
        df = pd.DataFrame({
            "Open": [100.0] * 25,
            "High": [105.0] * 25,
            "Low": [95.0] * 25,
            "Close": list(range(100, 125)),
            "Volume": [1000] * 25,
        })
        df = calculate_ma(df, windows=[20])
        assert "MA20" in df.columns


class TestPlotGroupCharts:
    """繪圖功能測試"""

    def test_output_directory_exists(self):
        """驗證輸出目錄存在"""
        assert os.path.exists("charts"), "charts directory should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])