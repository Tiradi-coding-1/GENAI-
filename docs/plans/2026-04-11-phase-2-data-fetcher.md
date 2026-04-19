# Phase 2: 數據獲取 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 使用 yfinance 抓取台股 OHLCV 數據，存成 CSV 檔案

**Architecture:** 模組化設計 - data_fetcher.py 負責數據抓取

**Tech Stack:** Python 3.12+, yfinance, pandas

---

## 股票清單（來自 Phase 1 研究）

### 族群一：晶圓代工與先進封裝
- 2330.TW（台積電）
- 2303.TW（聯電）
- 3711.TW（日月光投控）
- 3037.TW（欣興）
- 6239.TW（力成）

### 族群二：AI 伺服器與 ODM 代工
- 2317.TW（鴻海）
- 2382.TW（廣達）
- 3231.TW（緯創）
- 6669.TW（緯穎）
- 2356.TW（英業達）

### 族群三：AI 散熱與電源管理
- 3017.TW（奇鋐）
- 3324.TW（雙鴻）
- 2308.TW（台達電）
- 2421.TW（建準）
- 2301.TW（光寶科）

---

## Task 1: 建立 data_fetcher.py 測試檔案

**Files:**
- Create: `tests/test_data_fetcher.py`

**Step 1: 寫入測試檔案**

```python
import pytest
import pandas as pd
from src.data_fetcher import StockDataFetcher


def test_fetcher_initialization():
    fetcher = StockDataFetcher()
    assert fetcher is not None


def test_validate_stock_symbol():
    fetcher = StockDataFetcher()
    # 2330.TW should be valid (TSMC)
    result = fetcher.validate_stock_symbol("2330.TW")
    assert result is True
```


**Step 2: 執行測試確認失敗（因為 data_fetcher.py 尚未建立）**

Expected: FAIL - module not found

---

## Task 2: 建立 data_fetcher.py

**Files:**
- Create: `src/data_fetcher.py`

**Step 1: 實作 StockDataFetcher 類別**

```python
"""台股 OHLCV 數據抓取模組

使用 yfinance 抓取台灣上市股票的歷史數據
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Optional

import yfinance as yf
import pandas as pd


logger = logging.getLogger(__name__)


class StockDataFetcher:
    """台股數據抓取器"""
    
    STOCK_GROUPS = {
        "wafer_foundry": {
            "name": "晶圓代工與先進封裝",
            "stocks": ["2330.TW", "2303.TW", "3711.TW", "3037.TW", "6239.TW"]
        },
        "ai_server": {
            "name": "AI 伺服器與 ODM 代工",
            "stocks": ["2317.TW", "2382.TW", "3231.TW", "6669.TW", "2356.TW"]
        },
        "ai_cooling": {
            "name": "AI 散熱與電源管理",
            "stocks": ["3017.TW", "3324.TW", "2308.TW", "2421.TW", "2301.TW"]
        }
    }
    
    def __init__(self, days: int = 180, retry: int = 3, sleep: float = 1.5):
        """初始化
        
        Args:
            days: 抓取天數（預設 180 天）
            retry: 網路錯誤重試次數
            sleep: 每次請求間隔秒數
        """
        self.days = days
        self.retry = retry
        self.sleep = sleep
        
    def validate_stock_symbol(self, symbol: str) -> bool:
        """驗證股票代號是否存在
        
        Args:
            symbol: 股票代號（如 2330.TW）
            
        Returns:
            True if valid, False otherwise
        """
        for attempt in range(self.retry):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                return bool(info and 'symbol' in info)
            except Exception:
                if attempt < self.retry - 1:
                    time.sleep(1)
                    continue
                return False
        return False
    
    def fetch_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """抓取單一股票數據
        
        Args:
            symbol: 股票代號
            
        Returns:
            DataFrame 或 None（失敗時）
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days)
        
        for attempt in range(self.retry):
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date.strftime('%Y-%m-%d'),
                                   end=end_date.strftime('%Y-%m-%d'))
                
                if df.empty:
                    logger.warning(f"無數據: {symbol}")
                    return None
                    
                df = df.reset_index()
                df['Stock_ID'] = symbol
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                df = df.rename(columns={
                    'Open': 'Open',
                    'High': 'High', 
                    'Low': 'Low',
                    'Close': 'Close',
                    'Volume': 'Volume'
                })
                df = df[['Date', 'Stock_ID', 'Open', 'High', 'Low', 'Close', 'Volume']]
                
                return df
                
            except Exception as e:
                logger.warning(f"抓取失敗 {symbol}: {e}")
                if attempt < self.retry - 1:
                    time.sleep(2)
                    continue
                return None
                
        return None
    
    def fetch_group_data(self, group_key: str) -> pd.DataFrame:
        """抓取族群全部股票數據
        
        Args:
            group_key: 族群鍵值（如 'wafer_foundry'）
            
        Returns:
            合併後的 DataFrame
        """
        group = self.STOCK_GROUPS[group_key]
        all_data = []
        
        for symbol in group['stocks']:
            logger.info(f"抓取 {symbol}...")
            df = self.fetch_stock_data(symbol)
            if df is not None and not df.empty:
                all_data.append(df)
            time.sleep(self.sleep)
            
        if not all_data:
            return pd.DataFrame()
            
        return pd.concat(all_data, ignore_index=True)
    
    def save_to_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """儲存至 CSV
        
        Args:
            df: DataFrame
            filename: 檔案名稱
            
        Returns:
            True 成功, False 失敗
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"已儲存: {filename}")
            return True
        except Exception as e:
            logger.error(f"儲存失敗 {filename}: {e}")
            return False
    
    def run(self, output_dir: str = "data") -> dict:
        """執行全部抓取
        
        Args:
            output_dir: 輸出目錄
            
        Returns:
            結果摘要 dict
        """
        results = {}
        
        for group_key in self.STOCK_GROUPS:
            group = self.STOCK_GROUPS[group_key]
            logger.info(f"開始抓取族群: {group['name']}")
            
            df = self.fetch_group_data(group_key)
            
            if df.empty:
                logger.warning(f"族群 {group_key} 無數據")
                results[group_key] = {"status": "failed", "rows": 0}
                continue
                
            filename = f"{output_dir}/{group_key}.csv"
            success = self.save_to_csv(df, filename)
            
            results[group_key] = {
                "status": "success" if success else "failed",
                "rows": len(df),
                "stocks": df['Stock_ID'].unique().tolist()
            }
            
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetcher = StockDataFetcher()
    results = fetcher.run()
    print("\n=== 結果摘要 ===")
    for key, result in results.items():
        print(f"{key}: {result}")
```

**Step 2: 執行測試確認通過**

```bash
python -m pytest tests/test_data_fetcher.py -v
```

Expected: PASS

---

## Task 3: 執行數據抓取

**Step 1: 執行 data_fetcher**

```bash
cd E:/01_PROJECTS/CURRENT/taiwan_stock_vibe_blueprint
python -m src.data_fetcher
```

Expected: 產出 3 個 CSV 檔案

**Step 2: 驗證 CSV 內容**

```bash
python -c "import pandas as pd; df = pd.read_csv('data/wafer_foundry.csv'); print(df.head())"
```

Expected: 顯示 OHLCV 欄位正確

**Step 3: Commit**

```bash
git add src/data_fetcher.py tests/test_data_fetcher.py data/ && git commit -m "feat: 完成 Phase 2 - yfinance 台股 OHLCV 數據抓取"
```

---

## Task 4: 驗收檢查

1. data/ 資料夾內有 3 個 CSV 檔案
2. 每個 CSV 包含欄位：Date, Stock_ID, Open, High, Low, Close, Volume
3. 日期範圍正確（今天往回推 180 天）
4. 用 pandas 讀取不報錯
5. 執行時間不超過 60 秒