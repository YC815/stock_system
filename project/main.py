import os
import json
from functions.db_setup import initialize_database
from functions.stock_data import fetch_and_save_stock_data, fetch_and_save_fundamentals, fetch_and_save_recommendations

# 設定路徑與參數
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "stocks_data.db")
COMPANIES_TABLE = "companies"
HISTORICAL_DATA_TABLE = "historical_data"
FUNDAMENTALS_TABLE = "fundamentals"
RECOMMENDATIONS_TABLE = "recommendations"
STOCK_LIST_PATH = os.path.join(BASE_DIR, "config", "stock_list.json")

# 初始化資料庫
initialize_database(
    db_path=DB_PATH,
    companies_table=COMPANIES_TABLE,
    historical_data_table=HISTORICAL_DATA_TABLE,
    fundamentals_table=FUNDAMENTALS_TABLE,
    recommendations_table=RECOMMENDATIONS_TABLE
)

# 讀取 JSON 名單
with open(STOCK_LIST_PATH, "r") as f:
    stock_list = json.load(f)

# 處理每家公司的數據
for stock in stock_list["stocks"]:
    ticker = stock["ticker"]
    company_name = stock["company_name"]

    print(f"Processing data for {ticker} ({company_name})...")

    # 抓取歷史數據
    fetch_and_save_stock_data(
        ticker=ticker,
        company_name=company_name,
        db_path=DB_PATH,
        companies_table=COMPANIES_TABLE,
        historical_data_table=HISTORICAL_DATA_TABLE
    )

    # 抓取基本面數據
    fetch_and_save_fundamentals(
        ticker=ticker,
        db_path=DB_PATH,
        fundamentals_table=FUNDAMENTALS_TABLE
    )

    # 抓取推薦數據
    fetch_and_save_recommendations(
        ticker=ticker,
        db_path=DB_PATH,
        recommendations_table=RECOMMENDATIONS_TABLE
    )

print("All data processing complete.")
print(recommendations.head()
