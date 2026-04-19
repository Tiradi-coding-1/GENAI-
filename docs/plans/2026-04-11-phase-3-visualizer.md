# Phase 3: K 線圖繪製 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** 使用 mplfinance 繪製 K 線圖，輸出 PNG 檔案

**Tech Stack:** Python 3.12+, mplfinance, pandas

---

## Task 1: 建立 visualizer.py 測試檔案

**Files:**
- Create: `tests/test_visualizer.py`

**Step 1: 寫入測試檔案**

```python
import pytest
import pandas as pd
from src.visualizer import ChartVisualizer


def test_visualizer_initialization():
    viz = ChartVisualizer()
    assert viz is not None


def test_load_csv_data():
    viz = ChartVisualizer()
    df = viz.load_csv("data/wafer_foundry.csv")
    assert not df.empty
    assert 'Date' in df.columns
```


**Step 2: 執行測試確認失敗（因為 visualizer.py 尚未建立）**

Expected: FAIL - module not found

---

## Task 2: 建立 visualizer.py

**Files:**
- Create: `src/visualizer.py`

**Step 1: 實作 ChartVisualizer 類別**

```python
"""K 線圖繪製模組

使用 mplfinance 繪製台股 K 線圖
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib


logger = logging.getLogger(__name__)


matplotlib.rcParams['font.sans-serif'] = ['PingFang TC', 'Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False


class ChartVisualizer:
    """K 線圖視覺化器"""
    
    STOCK_NAMES = {
        "2330.TW": "台積電",
        "2303.TW": "聯電",
        "3711.TW": "日月光投控",
        "3037.TW": "欣興",
        "6239.TW": "力成",
        "2317.TW": "鴻海",
        "2382.TW": "廣達",
        "3231.TW": "緯創",
        "6669.TW": "緯穎",
        "2356.TW": "英業達",
        "3017.TW": "奇鋐",
        "3324.TW": "雙鴻",
        "2308.TW": "台達電",
        "2421.TW": "建準",
        "2301.TW": "光寶科"
    }
    
    GROUP_NAMES = {
        "wafer_foundry": "晶圓代工與先進封裝",
        "ai_server": "AI 伺服器與 ODM 代工",
        "ai_cooling": "AI 散熱與電源管理"
    }
    
    def __init__(self, dpi: int = 150):
        """初始化
        
        Args:
            dpi: 圖片解析度
        """
        self.dpi = dpi
        
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """讀取 CSV 資料
        
        Args:
            filepath: CSV 檔案路徑
            
        Returns:
            DataFrame
        """
        df = pd.read_csv(filepath)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    
    def get_stock_data(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """取得單一股票數據
        
        Args:
            df: 完整 DataFrame
            symbol: 股票代號
            
        Returns:
            該股票數據
        """
        stock_df = df[df['Stock_ID'] == symbol].copy()
        stock_df = stock_df.set_index('Date')
        stock_df = stock_df[['Open', 'High', 'Low', 'Close', 'Volume']]
        return stock_df
    
    def add_moving_averages(self, df: pd.DataFrame, ma5: int = 5, ma20: int = 20) -> list:
        """新增均線
        
        Args:
            df: 股票數據
            ma5: MA5 天數
            ma20: MA20 天數
            
        Returns:
            mpf style 列表
        """
        ma5_col = df['Close'].rolling(window=ma5).mean()
        ma20_col = df['Close'].rolling(window=ma20).mean()
        
        return [
            mpf.make_addplot(ma5_col, color='#FF6B00', width=1, label='MA5'),
            mpf.make_addplot(ma20_col, color='#0066CC', width=1, label='MA20')
        ]
    
    def plot_stock_candlestick(self, df: pd.DataFrame, symbol: str, 
                                title: str, save_path: Optional[str] = None,
                                panel_ratio: float = 0.2) -> None:
        """繪製單一股票 K 線圖
        
        Args:
            df: 股票數據
            symbol: 股票代號
            title: 圖表標題
            save_path: 儲存路徑
            panel_ratio: 成交量面板比例
        """
        stock_name = self.STOCK_NAMES.get(symbol, symbol)
        full_title = f"{symbol} {stock_name}"
        
        mc = mpf.make_marketcolors(
            up='#FF0000',
            down='#00AA00',
            edge='inherit',
            wick='inherit',
            volume='in'
        )
        
        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='-',
            gridcolor='#E0E0E0',
            figcolor='white',
            y_on_right=True
        )
        
        apds = self.add_moving_averages(df)
        
        fig, axes = mpf.plot(
            df,
            type='candle',
            style=s,
            title=full_title,
            ylabel='價格',
            ylabel_lower='成交量',
            volume=True,
            addplot=apds,
            figsize=(12, 8),
            panel_ratios=(1, panel_ratio),
            tight_layout=True,
            returnfig=True
        )
        
        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"已儲存: {save_path}")
            
        plt.close(fig)
    
    def plot_group_charts(self, csv_path: str, group_key: str, output_dir: str = "charts") -> None:
        """繪製族群全部股票 K 線圖
        
        Args:
            csv_path: CSV 檔案路徑
            group_key: 族群鍵值
            output_dir: 輸出目錄
        """
        df = self.load_csv(csv_path)
        symbols = df['Stock_ID'].unique().tolist()
        group_name = self.GROUP_NAMES.get(group_key, group_key)
        
        n_stocks = len(symbols)
        fig_height = 3 * n_stocks
        
        fig, axes = plt.subplots(n_stocks, 1, figsize=(14, fig_height))
        
        if n_stocks == 1:
            axes = [axes]
        
        for idx, symbol in enumerate(symbols):
            stock_df = self.get_stock_data(df, symbol)
            stock_name = self.STOCK_NAMES.get(symbol, symbol)
            
            mc = mpf.make_marketcolors(
                up='#FF0000',
                down='#00AA00',
                edge='inherit',
                wick='inherit'
            )
            
            s = mpf.make_mpf_style(
                marketcolors=mc,
                gridstyle='-',
                gridcolor='#E0E0E0',
                y_on_right=True
            )
            
            apds = self.add_moving_averages(stock_df)
            
            mpf.plot(
                stock_df,
                type='candle',
                style=s,
                title=f"{symbol} {stock_name}",
                ylabel='價格',
                volume=True,
                addplot=apds,
                ax=axes[idx],
                panel_ratios=(1, 0.2),
                tight_layout=True
            )
        
        fig.suptitle(f"[{group_name}] K線圖分析", fontsize=16, fontweight='bold', y=0.995)
        
        output_path = Path(output_dir) / f"{group_key}.png"
        fig.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        logger.info(f"已儲存: {output_path}")
        
        plt.close(fig)
    
    def run(self, data_dir: str = "data", output_dir: str = "charts") -> dict:
        """執行全部繪圖
        
        Args:
            data_dir: 資料目錄
            output_dir: 輸出目錄
            
        Returns:
            結果摘要
        """
        results = {}
        
        for group_key in ["wafer_foundry", "ai_server", "ai_cooling"]:
            csv_path = f"{data_dir}/{group_key}.csv"
            
            if not Path(csv_path).exists():
                logger.warning(f"檔案不存在: {csv_path}")
                results[group_key] = {"status": "skipped", "reason": "file not found"}
                continue
                
            try:
                self.plot_group_charts(csv_path, group_key, output_dir)
                results[group_key] = {"status": "success"}
            except Exception as e:
                logger.error(f"繪圖失敗 {group_key}: {e}")
                results[group_key] = {"status": "failed", "error": str(e)}
                
        return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    viz = ChartVisualizer()
    results = viz.run()
    print("\n=== 結果摘要 ===")
    for key, result in results.items():
        print(f"{key}: {result}")
```

**Step 2: 執行測試確認通過**

```bash
python -m pytest tests/test_visualizer.py -v
```

Expected: PASS

---

## Task 3: 執行 K 線圖繪製

**Step 1: 執行 visualizer**

```bash
cd E:/01_PROJECTS/CURRENT/taiwan_stock_vibe_blueprint
python -m src.visualizer
```

Expected: 產出 3 個 PNG 檔案

**Step 2: 驗證 PNG 存在**

```bash
ls -la charts/
```

Expected: 3 個 PNG 檔案

**Step 3: Commit**

```bash
git add src/visualizer.py tests/test_visualizer.py charts/ && git commit -m "feat: 完成 Phase 3 - mplfinance K線圖繪製"
```

---

## Task 4: 驗收檢查

1. charts/ 資料夾內有 3 張 PNG 圖片
2. 每張圖包含該族群所有股票的 subplot
3. K 線顏色：紅漲綠跌
4. 每個 subplot 疊加 MA5（橘色）、MA20（藍色）均線
5. 每個 subplot 下方有成交量副圖
6. 圖表標題顯示繁體中文
7. 圖片解析度 dpi >= 150