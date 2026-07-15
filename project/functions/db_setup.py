import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime
import os


def initialize_database(db_path, companies_table, historical_data_table, fundamentals_table, recommendations_table):
    """
    初始化 SQLite 資料庫，包括創建母表、子表、基本面數據表和推薦數據表。
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 公司基本資料表
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {companies_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL UNIQUE,
        company_name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 歷史數據表
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {historical_data_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        date DATE NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        adj_close REAL,
        volume INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker, date)
    )
    """)

    # 基本面數據表
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {fundamentals_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        market_cap REAL,
        pe_ratio REAL,
        eps REAL,
        dividend_yield REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ticker)
    )
    """)

    # 推薦數據表
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {recommendations_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        recommendation TEXT,
        rating INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized with tables: {companies_table}, {historical_data_table}, {fundamentals_table}, {recommendations_table}.")
