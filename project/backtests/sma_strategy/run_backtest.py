import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os
import json

# 設定路徑
DB_PATH = "data/stocks_data.db"
FONT_PATH = "assets/font.ttf"
STOCK_LIST_PATH = "config/stock_list.json"

# 讀取股票列表 JSON 文件


def load_stock_list(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"配置文件未找到：{json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)["stocks"]


stocks = load_stock_list(STOCK_LIST_PATH)

# 計算綜合回測資產曲線


def calculate_combined_returns(stocks, short_window, long_window, db_path=DB_PATH):
    combined_data = pd.DataFrame()

    for stock in stocks:
        ticker = stock["ticker"]

        # 連接資料庫
        conn = sqlite3.connect(db_path)
        query = f"SELECT date, close FROM historical_data WHERE ticker='{ticker}' ORDER BY date"
        df = pd.read_sql(query, conn)
        conn.close()

        # 檢查數據是否存在或無效
        if df.empty or df['close'].isnull().all():
            print(f"跳過股票 '{ticker}'：數據缺失或無效。")
            continue

        # 日期處理
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # 限制數據範圍
        df = df.loc['2005-01-01':'2024-12-31']

        # 計算移動平均線
        df['SMA_short'] = df['close'].rolling(window=short_window).mean()
        df['SMA_long'] = df['close'].rolling(window=long_window).mean()

        # 生成交易信號
        df['signal'] = 0
        df.loc[df['SMA_short'] > df['SMA_long'], 'signal'] = 1
        df.loc[df['SMA_short'] <= df['SMA_long'], 'signal'] = 0
        df['position'] = df['signal'].shift(1)

        # 計算每日收益與資金曲線
        initial_capital = 10000  # 每支股票初始資金
        transaction_cost = 0.001  # 模擬交易成本
        df['daily_return'] = df['close'].pct_change()
        df['strategy_return'] = df['position'] * df['daily_return'] - df['signal'].diff().abs() * transaction_cost
        df['portfolio'] = initial_capital * (1 + df['strategy_return']).cumprod()
        df['benchmark'] = initial_capital * (1 + df['daily_return']).cumprod()

        # 合併到總表
        if combined_data.empty:
            combined_data = df[['portfolio', 'benchmark']].copy()
        else:
            combined_data['portfolio'] += df['portfolio'].reindex(combined_data.index, fill_value=initial_capital)
            combined_data['benchmark'] += df['benchmark'].reindex(combined_data.index, fill_value=initial_capital)

    # 對齊數據起始點
    combined_data = combined_data.loc[combined_data['portfolio'].gt(0).idxmax():]
    return combined_data.reset_index()

# 繪製資產曲線


def plot_combined_results(combined_data, output_dir="project/backtests"):
    if not os.path.exists(FONT_PATH):
        print(f"字體文件未找到：{FONT_PATH}，無法顯示中文。請確保字體文件存在。")
        return
    zh_font = font_manager.FontProperties(fname=FONT_PATH)

    os.makedirs(output_dir, exist_ok=True)

    # 繪製圖表
    plt.figure(figsize=(12, 6))
    plt.plot(combined_data['date'], combined_data['portfolio'], label='策略資產曲線', color='blue')
    plt.plot(combined_data['date'], combined_data['benchmark'], label='基準資產曲線', color='orange')
    plt.title("所有股票綜合回測資產曲線", fontsize=16, fontproperties=zh_font)
    plt.xlabel("日期", fontsize=12, fontproperties=zh_font)
    plt.ylabel("資產價值", fontsize=12, fontproperties=zh_font)
    plt.legend(prop=zh_font)
    plt.grid(alpha=0.3)

    # 保存圖表和數據
    png_path = os.path.join(output_dir, "綜合回測資產曲線.png")
    csv_path = os.path.join(output_dir, "綜合回測資產曲線.csv")
    plt.tight_layout()
    plt.savefig(png_path)
    combined_data.to_csv(csv_path, index=False)
    print(f"圖表已保存至: {png_path}")
    print(f"數據已保存至: {csv_path}")

    plt.show()

# 打印回測指標


def print_combined_metrics(combined_data):
    combined_data = combined_data.dropna()
    initial_portfolio = combined_data['portfolio'].iloc[0]
    final_portfolio = combined_data['portfolio'].iloc[-1]
    portfolio_return = (final_portfolio / initial_portfolio - 1) * 100

    initial_benchmark = combined_data['benchmark'].iloc[0]
    final_benchmark = combined_data['benchmark'].iloc[-1]
    benchmark_return = (final_benchmark / initial_benchmark - 1) * 100

    portfolio_drawdown = (combined_data['portfolio'] / combined_data['portfolio'].cummax() - 1).min() * 100
    benchmark_drawdown = (combined_data['benchmark'] / combined_data['benchmark'].cummax() - 1).min() * 100

    print("\n--- 回測結果 ---")
    print(f"策略總收益率: {portfolio_return:.2f}%")
    print(f"基準總收益率: {benchmark_return:.2f}%")
    print(f"策略最大回撤: {portfolio_drawdown:.2f}%")
    print(f"基準最大回撤: {benchmark_drawdown:.2f}%")
    print(f"策略最終資產: ${final_portfolio:,.2f}")
    print(f"基準最終資產: ${final_benchmark:,.2f}")


# 執行回測
short_window = 50
long_window = 200
output_dir = "project/backtests/combined_results"

print("計算所有股票的綜合資產曲線...")
combined_data = calculate_combined_returns(stocks, short_window, long_window)

print("繪製綜合資產曲線...")
plot_combined_results(combined_data, output_dir)

print("打印回測相關資訊...")
print_combined_metrics(combined_data)
