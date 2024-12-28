import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# 設定資料庫路徑
DB_PATH = "data/stocks_data.db"


def plot_stock_prices(ticker, db_path=DB_PATH):
    """
    繪製指定股票的價格折線圖。

    Args:
        ticker (str): 股票代號 (例如: 'AAPL')。
        db_path (str): SQLite 資料庫檔案路徑。
    """
    # 連接資料庫
    conn = sqlite3.connect(db_path)

    # 查詢該股票的歷史數據
    query = f"SELECT date, open, high, low, close FROM historical_data WHERE ticker='{ticker}' ORDER BY date"
    df = pd.read_sql(query, conn)

    # 關閉資料庫連接
    conn.close()

    # 檢查是否有數據
    if df.empty:
        print(f"No data found for ticker '{ticker}'.")
        return

    # 將日期欄位轉為 datetime 格式
    df['date'] = pd.to_datetime(df['date'])

    # 繪製折線圖
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['open'], label='Open Price', linestyle='-', alpha=0.7)
    plt.plot(df['date'], df['close'], label='Close Price', linestyle='-', alpha=0.7)
    plt.plot(df['date'], df['high'], label='High Price', linestyle='-', alpha=0.7)
    plt.plot(df['date'], df['low'], label='Low Price', linestyle='-', alpha=0.7)

    # 添加標題與圖例
    plt.title(f"Stock Prices for {ticker}", fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Price", fontsize=12)
    plt.legend()
    plt.grid(alpha=0.3)

    # 顯示圖表
    plt.tight_layout()
    plt.show()


# 更改這個變數以指定股票代號
ticker = "AAPL"

# 繪製圖表
plot_stock_prices(ticker)
