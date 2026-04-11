"""
台灣股市 OHLCV 數據抓取模組

使用 yfinance 抓取台股數據並輸出為 CSV 檔案
"""

import time
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

WAFER_FOUNDRY = ["2330.TW", "2303.TW", "3711.TW", "3037.TW", "6239.TW"]
AI_SERVER = ["2317.TW", "2382.TW", "3231.TW", "6669.TW", "2356.TW"]
AI_COOLING = ["3017.TW", "3324.TW", "2308.TW", "2421.TW", "2301.TW"]

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 3
RETRY_DELAY = 1.5
HISTORY_DAYS = 180


def fetch_stock_data(
    ticker: str,
    days: int = HISTORY_DAYS,
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY,
) -> Optional[pd.DataFrame]:
    """
    抓取單一股票 OHLCV 數據

    Args:
        ticker: 台股代碼 (如 2330.TW)
        days: 抓取天數
        max_retries: 網路錯誤重試次數
        retry_delay: 重試間隔秒數

    Returns:
        DataFrame 含 Date, Open, High, Low, Close, Volume 或 None
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days + 30)

    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

            if df.empty:
                print(f"[警告] {ticker} 無數據")
                return None

            df = df.reset_index()
            dates = df["Date"].dt.strftime("%Y-%m-%d").tolist()
            result = pd.DataFrame({
                "Date": dates,
                "Open": df["Open"].tolist(),
                "High": df["High"].tolist(),
                "Low": df["Low"].tolist(),
                "Close": df["Close"].tolist(),
                "Volume": df["Volume"].tolist(),
                "Stock_ID": ticker,
            })
            return result

        except Exception as e:
            print(f"[警告] {ticker} 第 {attempt + 1} 次嘗試失敗: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    print(f"[錯誤] {ticker} 抓取失敗 (已重試 {max_retries} 次)")
    return None


def fetch_group_data(
    tickers: list[str],
    output_file: Path,
) -> pd.DataFrame:
    """
    抓取一組股票數據並輸出 CSV

    Args:
        tickers: 股票代碼列表
        output_file: 輸出 CSV 檔案路徑

    Returns:
        合併後的 DataFrame
    """
    all_data = []

    for ticker in tickers:
        df = fetch_stock_data(ticker)
        if df is not None:
            all_data.append(df)
        time.sleep(RETRY_DELAY)

    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        cols = ["Date", "Stock_ID", "Open", "High", "Low", "Close", "Volume"]
        result = result[cols].copy()
        result.to_csv(output_file, index=False)
        print(f"已寫入 {output_file} ({len(result)} 列)")
        return result
    else:
        result = pd.DataFrame(columns=["Date", "Stock_ID", "Open", "High", "Low", "Close", "Volume"])
        result.to_csv(output_file, index=False)
        print(f"[警告] {output_file} 無數據")
        return result


def main():
    """主程式：抓取所有族群數據"""
    print("開始抓取台股數據...")
    print(f"數據範圍：過去 {HISTORY_DAYS} 天")
    print("-" * 40)

    print("\n[族群一] 晶圓代工與先進封裝")
    fetch_group_data(WAFER_FOUNDRY, DATA_DIR / "wafer_foundry.csv")

    print("\n[族群二] AI 伺服器與 ODM 代工")
    fetch_group_data(AI_SERVER, DATA_DIR / "ai_server.csv")

    print("\n[族群三] AI 散熱與電源管理")
    fetch_group_data(AI_COOLING, DATA_DIR / "ai_cooling.csv")

    print("\n" + "-" * 40)
    print("數據抓取完成!")


if __name__ == "__main__":
    main()