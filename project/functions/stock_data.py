import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime


def fetch_and_save_stock_data(
    ticker,
    company_name,
    db_path,
    companies_table,
    historical_data_table
):
    """
    抓取指定股票的歷史資料並存入 SQLite 資料庫。

    Args:
        ticker (str): 股票代號 (例如: 'AAPL')。
        company_name (str): 公司名稱 (例如: 'Apple')。
        db_path (str): SQLite 資料庫檔案路徑。
        companies_table (str): 公司資訊表名稱。
        historical_data_table (str): 歷史數據表名稱。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 插入或更新公司資訊到母表
    cursor.execute(f"""
    INSERT OR IGNORE INTO {companies_table} (ticker, company_name) VALUES (?, ?)
    """, (ticker, company_name))
    conn.commit()

    # 抓取股票的歷史資料
    print(f"Fetching historical data for {ticker} ({company_name})...")
    try:
        data = yf.Ticker(ticker).history(period="max")

        if data.empty:
            raise ValueError(f"No data found for {ticker}. Check the ticker symbol or network connection.")

        data.reset_index(inplace=True)

        if 'Date' in data.columns and pd.api.types.is_datetime64_any_dtype(data['Date']):
            data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
        else:
            raise ValueError("Invalid or missing 'Date' column in data.")

        if 'Adj Close' not in data.columns:
            data['Adj Close'] = None

        data['ticker'] = ticker
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = data[['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'created_at']]
        data.columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'created_at']

        for _, row in data.iterrows():
            cursor.execute(f"""
            INSERT OR IGNORE INTO {historical_data_table} 
            (ticker, date, open, high, low, close, adj_close, volume, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(row))
        conn.commit()

        print(f"Data for {ticker} successfully saved to database.")

    except Exception as e:
        print(f"Failed to fetch or save data for {ticker}: {e}")

    conn.close()
