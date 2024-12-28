import sqlite3
import os


def initialize_database(db_path, companies_table, historical_data_table):
    """
    初始化 SQLite 資料庫，包括創建母表和子表。

    Args:
        db_path (str): SQLite 資料庫檔案路徑。
        companies_table (str): 公司資訊表名稱。
        historical_data_table (str): 歷史數據表名稱。
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 建立母表
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {companies_table} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL UNIQUE,
        company_name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 建立子表
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

    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path} with tables '{companies_table}' and '{historical_data_table}'.")
