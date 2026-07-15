import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime


def fetch_and_save_stock_data(ticker, company_name, db_path, companies_table, historical_data_table):
    """
    抓取指定股票的歷史資料並存入 SQLite 資料庫。
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

        # 確保 'Adj Close' 欄位存在，否則填充為 None
        if 'Adj Close' not in data.columns:
            data['Adj Close'] = None

        data['Date'] = data['Date'].dt.strftime('%Y-%m-%d')
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


def fetch_and_save_fundamentals(ticker, db_path, fundamentals_table):
    """
    抓取股票基本面數據並存入 SQLite 資料庫。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Fetching fundamentals for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        fundamentals_data = {
            "ticker": ticker,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        cursor.execute(f"""
        INSERT OR REPLACE INTO {fundamentals_table} (ticker, market_cap, pe_ratio, eps, dividend_yield, created_at)
        VALUES (:ticker, :market_cap, :pe_ratio, :eps, :dividend_yield, :created_at)
        """, fundamentals_data)

        conn.commit()
        print(f"Fundamentals for {ticker} saved successfully.")

    except Exception as e:
        print(f"Failed to fetch fundamentals for {ticker}: {e}")

    conn.close()


def fetch_and_save_recommendations(ticker, db_path, recommendations_table):
    """
    抓取股票的推薦評級數據並存入 SQLite 資料庫。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Fetching recommendations for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations

        if recommendations is not None and not recommendations.empty:
            recommendations = recommendations.reset_index()

            # 動態檢查需要的欄位是否存在
            required_columns = ['To Grade', 'rating']
            for col in required_columns:
                if col not in recommendations.columns:
                    print(f"Column '{col}' missing in recommendations for {ticker}. Skipping...")
                    return

            recommendations["ticker"] = ticker
            recommendations["created_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for _, row in recommendations.iterrows():
                cursor.execute(f"""
                INSERT OR IGNORE INTO {recommendations_table} (ticker, recommendation, rating, created_at)
                VALUES (?, ?, ?, ?)
                """, (ticker, row["To Grade"], row.get("rating", None), row["created_at"]))

            conn.commit()
            print(f"Recommendations for {ticker} saved successfully.")

        else:
            print(f"No recommendations data available for {ticker}.")

    except Exception as e:
        print(f"Failed to fetch recommendations for {ticker}: {e}")

    conn.close()
    """
    抓取股票的推薦評級數據並存入 SQLite 資料庫。
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Fetching recommendations for {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations

        if recommendations is not None and not recommendations.empty:
            recommendations = recommendations.reset_index()

            # 檢查是否存在 'To Grade' 欄位
            if 'To Grade' not in recommendations.columns:
                print(f"No 'To Grade' column in recommendations for {ticker}. Skipping...")
                return

            recommendations["ticker"] = ticker
            recommendations["created_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for _, row in recommendations.iterrows():
                cursor.execute(f"""
                INSERT OR IGNORE INTO {recommendations_table} (ticker, recommendation, rating, created_at)
                VALUES (?, ?, ?, ?)
                """, (ticker, row["To Grade"], row.get("rating", None), row["created_at"]))

            conn.commit()
            print(f"Recommendations for {ticker} saved successfully.")

        else:
            print(f"No recommendations data available for {ticker}.")

    except Exception as e:
        print(f"Failed to fetch recommendations for {ticker}: {e}")

    conn.close()
