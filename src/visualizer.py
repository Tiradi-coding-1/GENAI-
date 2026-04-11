"""
K線圖繪製模組

使用 mplfinance 繪製台灣股票 K 線圖，包含均線與成交量副圖。
"""

import os
import glob
from typing import List

import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime


STOCK_NAMES = {
    "2330.TW": "台積電",
    "2303.TW": "聯電",
    "3711.TW": "日月投控",
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
    "2301.TW": "光寶科",
}

STOCK_GROUPS = {
    "wafer_foundry": ["2330.TW", "2303.TW", "3711.TW", "3037.TW", "6239.TW"],
    "ai_server": ["2317.TW", "2382.TW", "3231.TW", "6669.TW", "2356.TW"],
    "ai_cooling": ["3017.TW", "3324.TW", "2308.TW", "2421.TW", "2301.TW"],
}

DATA_DIR = "data"
OUTPUT_DIR = "charts"


def load_stock_data(csv_path: str, stock_id: str) -> pd.DataFrame:
    """
    載入單一股票的 K 線資料

    Args:
        csv_path: CSV 檔案路徑
        stock_id: 股票代號

    Returns:
        處理後的 DataFrame，含 Date, Open, High, Low, Close, Volume 欄位
    """
    df = pd.read_csv(csv_path)
    df = df[df["Stock_ID"] == stock_id].copy()
    if df.empty:
        raise ValueError(f"No data for {stock_id}")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    df = df.sort_index()

    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df = df[required_cols]
    return df


def calculate_ma(df: pd.DataFrame, windows: List[int] = [5, 20]) -> pd.DataFrame:
    """
    計算移動平均線

    Args:
        df: 股價資料 DataFrame
        windows: 均線週期列表

    Returns:
        新增 MA 欄位後的 DataFrame
    """
    for window in windows:
        df[f"MA{window}"] = df["Close"].rolling(window=window).mean()
    return df


def plot_stock_candle(ax, volume_ax, df: pd.DataFrame, title: str) -> None:
    """
    在指定的 axes 上繪製 K 線圖

    Args:
        ax: K 線圖 axes
        volume_ax: 成交量 axes
        df: 股價資料（含 MA5, MA20）
        title: 圖表標題
    """
    up_color = "#E60012"
    down_color = "#009944"

    mc = mpf.make_marketcolors(
        up=up_color,
        down=down_color,
        edge="inherit",
        wick="inherit",
        volume="in",
    )

    s = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle="-",
        gridcolor="#EEEEEE",
    )

    mpf.plot(
        df,
        type="candle",
        style=s,
        ax=ax,
        volume=volume_ax,
        show_nontrading=False,
        returnfig=False,
    )

    ax.set_title(title, fontsize=10, pad=5)

    ma5_color = "#FF8800"
    ma20_color = "#0066CC"

    if "MA5" in df.columns:
        ax.plot(df.index, df["MA5"], color=ma5_color, linewidth=1, label="MA5")
    if "MA20" in df.columns:
        ax.plot(df.index, df["MA20"], color=ma20_color, linewidth=1, label="MA20")

    ax.legend(loc="upper left", fontsize=8)


def plot_group_chart(group_name: str, stock_ids: List[str]) -> None:
    """
    繪製單一族群的 K 線圖（垂直排列多個股票的子圖）

    Args:
        group_name: 族群名稱
        stock_ids: 該族群的股票代號列表
    """
    csv_files = glob.glob(os.path.join(DATA_DIR, f"{group_name}.csv"))
    if not csv_files:
        print(f"找不到資料檔案: {group_name}.csv")
        return

    csv_path = csv_files[0]

    stock_data_dict = {}
    for stock_id in stock_ids:
        try:
            df = load_stock_data(csv_path, stock_id)
            if df.empty or len(df) < 20:
                print(f"跳過 {stock_id}: 資料不足")
                continue
            df = calculate_ma(df, windows=[5, 20])
            stock_data_dict[stock_id] = df
        except Exception as e:
            print(f"載入 {stock_id} 失敗: {e}")
            continue

    if not stock_data_dict:
        print(f"沒有有效的股票資料: {group_name}")
        return

    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"

    n_stocks = len(stock_data_dict)
    valid_stocks = list(stock_data_dict.keys())

    fig = plt.figure(figsize=(14, 5 * n_stocks), dpi=150)
    gs = gridspec.GridSpec(n_stocks * 2, 1, figure=fig, hspace=0.1)

    fig.suptitle(
        f"[{group_name}] K線圖分析",
        fontsize=14,
        fontweight="bold",
        y=0.98,
    )

    for idx, stock_id in enumerate(valid_stocks):
        df = stock_data_dict[stock_id]
        stock_name = STOCK_NAMES.get(stock_id, stock_id)
        title = f"[{stock_id}] {stock_name}"

        ax = fig.add_subplot(gs[2 * idx, 0])
        volume_ax = fig.add_subplot(gs[2 * idx + 1, 0])

        plot_stock_candle(ax, volume_ax, df, title)

        if idx < n_stocks - 1:
            ax.set_xticklabels([])

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    output_path = os.path.join(OUTPUT_DIR, f"{group_name}.png")
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"已產出: {output_path}")


def plot_all_groups() -> None:
    """
    繪製所有族群的 K 線圖

    依序處理 wafer_foundry、ai_server、ai_cooling 三個族群，
    分別輸出對應的 PNG 圖檔。
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for group_name, stock_ids in STOCK_GROUPS.items():
        plot_group_chart(group_name, stock_ids)


def main():
    """主函式：繪製所有族群的 K 線圖"""
    plot_all_groups()


if __name__ == "__main__":
    main()