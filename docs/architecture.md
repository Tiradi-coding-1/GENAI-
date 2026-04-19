# 系統架構文件

> 版本：1.0
> 更新日期：2026年4月

---

## 1. 系統總覽

本系統為一套台股趨勢分析工具，採用 Python 模組化架構，涵蓋「數據抓取 → 資料儲存 → K 線圖繪製 → 趨勢分析」四個階段。全程使用 Vibe Coding 方法論，由多個 AI 工具協作完成。

```
┌─────────────────────────────────────────────────────┐
│                    使用者 (CLI)                      │
│              python -m src.data_fetcher              │
│              python -m src.visualizer                │
└────────────┬───────────────────────┬────────────────┘
             │                       │
             ▼                       ▼
┌────────────────────┐   ┌────────────────────────┐
│  data_fetcher.py   │   │    visualizer.py        │
│  ─────────────     │   │    ──────────           │
│  • yfinance API    │   │  • mplfinance K 線圖    │
│  • retry 機制      │──▶│  • MA5/MA20 均線        │
│  • CSV 輸出        │   │  • 成交量副圖           │
└────────┬───────────┘   └────────┬───────────────┘
         │                        │
         ▼                        ▼
┌────────────────────┐   ┌────────────────────────┐
│    data/*.csv      │   │    charts/*.png         │
│  ─────────────     │   │    ──────────           │
│  wafer_foundry.csv │   │  wafer_foundry.png      │
│  ai_server.csv     │   │  ai_server.png          │
│  ai_cooling.csv    │   │  ai_cooling.png         │
└────────────────────┘   └────────────────────────┘
```

---

## 2. 模組設計

### 2.1 data_fetcher.py — 數據抓取模組

**職責**：透過 yfinance API 抓取台股 OHLCV 歷史數據，輸出為 CSV。

| 函式 | 說明 |
|------|------|
| `fetch_stock_data(ticker, days, max_retries, retry_delay)` | 抓取單一股票 OHLCV，支援自動 retry |
| `fetch_group_data(tickers, output_file)` | 抓取一組股票並合併輸出 CSV |
| `main()` | 主程式入口，依序抓取三個族群 |

**設計決策**：
- **長表格式 (Long Format)**：每列代表一檔股票一天的數據，便於後續 groupby 操作
- **retry + sleep 機制**：最多重試 3 次，每次 API 請求後 sleep 1.5 秒，避免被限流
- **容錯設計**：單一股票抓取失敗不會中斷整個族群的抓取

**資料欄位規格**：

| 欄位 | 型別 | 說明 |
|------|------|------|
| Date | string (YYYY-MM-DD) | 交易日期 |
| Stock_ID | string | 台股代號 (如 2330.TW) |
| Open | float | 開盤價 |
| High | float | 最高價 |
| Low | float | 最低價 |
| Close | float | 收盤價 |
| Volume | int | 成交量 |

### 2.2 visualizer.py — K 線圖繪製模組

**職責**：讀取 CSV 數據，使用 mplfinance 繪製含均線與成交量的 K 線圖。

| 函式 | 說明 |
|------|------|
| `load_stock_data(csv_path, stock_id)` | 從 CSV 載入單一股票並轉為 DatetimeIndex |
| `calculate_ma(df, windows)` | 計算移動平均線 (預設 MA5, MA20) |
| `plot_stock_candle(ax, volume_ax, df, title)` | 在指定 axes 上繪製 K 線圖 |
| `plot_group_chart(group_name, stock_ids)` | 繪製族群多股 subplot 大圖 |
| `plot_all_groups()` | 繪製全部三個族群 |

**設計決策**：
- **台灣配色慣例**：上漲紅色 (#E60012)、下跌綠色 (#009944)
- **均線顏色**：MA5 橘色 (#FF8800)、MA20 藍色 (#0066CC)
- **中文字體 fallback**：依序嘗試 Adobe Fan Heiti Std → Microsoft JhengHei → SimHei → Arial Unicode MS
- **GridSpec 排版**：每個股票佔 2 個 grid row (K 線 + 成交量)，垂直堆疊

---

## 3. 資料流程 (Data Flow)

```
Phase 1                Phase 2                Phase 3              Phase 4
────────              ────────               ────────             ────────
股票族群研究     ──▶   yfinance API     ──▶   mplfinance    ──▶   Gemini 3 Pro
(Google Search)        抓取 OHLCV             繪製 K 線圖          視覺分析
                       │                      │                    │
                       ▼                      ▼                    ▼
                  data/*.csv             charts/*.png         docs/analysis.md
                  (3 族群 CSV)           (3 族群 PNG)         (趨勢分析報告)
```

### 3.1 數據抓取流程

```
開始
 │
 ├── 族群一：晶圓代工 (5 檔) ──▶ wafer_foundry.csv
 │     ├── 2330.TW 台積電
 │     ├── 2303.TW 聯電
 │     ├── 3711.TW 日月光投控
 │     ├── 3037.TW 欣興
 │     └── 6239.TW 力成
 │
 ├── 族群二：AI 伺服器 (5 檔) ──▶ ai_server.csv
 │     ├── 2317.TW 鴻海
 │     ├── 2382.TW 廣達
 │     ├── 3231.TW 緯創
 │     ├── 6669.TW 緯穎
 │     └── 2356.TW 英業達
 │
 └── 族群三：散熱電源 (5 檔) ──▶ ai_cooling.csv
       ├── 3017.TW 奇鋐
       ├── 3324.TW 雙鴻
       ├── 2308.TW 台達電
       ├── 2421.TW 建準
       └── 2301.TW 光寶科
```

---

## 4. 技術棧

| 類別 | 技術 | 用途 |
|------|------|------|
| 語言 | Python 3.12+ | 主要開發語言 |
| 數據來源 | yfinance | Yahoo Finance API 封裝 |
| 數據處理 | pandas | DataFrame 操作與 CSV I/O |
| 數值運算 | numpy | 數值計算支援 |
| K 線圖 | mplfinance | 專業股票圖表繪製 |
| 圖表引擎 | matplotlib | 底層圖表繪製與中文字體設定 |
| 測試框架 | pytest | 單元測試與 mock |
| 版本控制 | Git + GitHub | 程式碼管理 |

---

## 5. 測試架構

```
tests/
├── test_data_fetcher.py    # 數據抓取測試
│   ├── TestConstants       # 常數定義驗證
│   ├── TestFetchStockData  # 單一股票抓取 (mock yfinance)
│   └── TestFetchGroupData  # 族群抓取與 CSV 輸出
│
└── test_visualizer.py      # 視覺化測試
    ├── TestStockNames      # 股票名稱對照驗證
    ├── TestLoadStockData   # CSV 載入驗證
    ├── TestCalculateMA     # 均線計算正確性
    └── TestPlotGroupCharts # 輸出目錄驗證
```

**測試策略**：
- 使用 `unittest.mock.patch` mock yfinance API，避免測試依賴網路
- 常數驗證確保股票清單完整且格式正確
- 均線計算驗證 NaN 邊界條件

---

## 6. 目錄結構

```
taiwan-stock-analysis/
├── src/
│   ├── data_fetcher.py          # 數據抓取模組
│   └── visualizer.py            # K 線圖繪製模組
├── data/                        # OHLCV 數據 CSV (gitignore)
│   ├── wafer_foundry.csv
│   ├── ai_server.csv
│   └── ai_cooling.csv
├── charts/                      # K 線圖 PNG
│   ├── wafer_foundry.png
│   ├── ai_server.png
│   └── ai_cooling.png
├── tests/
│   ├── test_data_fetcher.py
│   └── test_visualizer.py
├── docs/
│   ├── architecture.md          # 本文件
│   ├── vibe-coding-methodology.md  # Vibe Coding 方法論
│   ├── analysis.md              # K 線圖趨勢分析報告
│   └── plans/                   # 各 Phase 實現計劃
├── requirements.txt
├── .gitignore
└── README.md
```
