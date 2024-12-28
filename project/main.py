import os
import json
from functions.db_setup import initialize_database
from functions.stock_data import fetch_and_save_stock_data

# 設定路徑與參數
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "stocks_data.db")
COMPANIES_TABLE = "companies"
HISTORICAL_DATA_TABLE = "historical_data"
STOCK_LIST_PATH = os.path.join(BASE_DIR, "config", "stock_list.json")

# 初始化資料庫
initialize_database(
    db_path=DB_PATH,
    companies_table=COMPANIES_TABLE,
    historical_data_table=HISTORICAL_DATA_TABLE
)

# 讀取 JSON 名單
with open(STOCK_LIST_PATH, "r") as f:
    stock_list = json.load(f)

# 處理每家公司的數據
for stock in stock_list["stocks"]:
    fetch_and_save_stock_data(
        ticker=stock["ticker"],
        company_name=stock["company_name"],
        db_path=DB_PATH,
        companies_table=COMPANIES_TABLE,
        historical_data_table=HISTORICAL_DATA_TABLE
    )
