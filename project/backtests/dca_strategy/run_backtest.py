import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

# 設定路徑
DB_PATH = "data/stocks_data.db"
FONT_PATH = "assets/font.ttf"


def backtest_dca_strategy(ticker, initial_capital, monthly_investment, db_path, start_date, end_date):
    """
    定期買入策略回測。

    Args:
        ticker (str): 股票代號。
        initial_capital (float): 初始資金。
        monthly_investment (float): 每月定期投入金額。
        db_path (str): SQLite 資料庫路徑。
        start_date (str): 回測開始日期，格式 "YYYY-MM-DD"。
        end_date (str): 回測結束日期，格式 "YYYY-MM-DD"。

    Returns:
        pd.DataFrame: 包含策略和基準資產曲線的數據表。
    """
    # 連接資料庫
    conn = sqlite3.connect(db_path)
    query = f"""
        SELECT date, close 
        FROM historical_data 
        WHERE ticker='{ticker}' AND date BETWEEN '{start_date}' AND '{end_date}' 
        ORDER BY date
    """
    df = pd.read_sql(query, conn)
    conn.close()

    # 日期處理
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # 初始化資金和資產曲線
    capital = initial_capital  # 剩餘現金
    shares_held = 0  # 持有股數
    strategy_capital = []  # 策略資產曲線
    benchmark_capital = [initial_capital]  # 基準資產曲線
    benchmark_position = initial_capital / df['close'].iloc[0]  # 基準持倉

    # 計算每月定期投資的日期
    investment_dates = df.resample('M').last().index  # 每月最後一個交易日

    for current_date in df.index:
        price = df.loc[current_date, 'close']

        # 檢查是否為定期投資日期
        if current_date in investment_dates:
            # 買入股票
            shares_to_buy = monthly_investment // price
            cost = shares_to_buy * price
            if shares_to_buy > 0 and capital >= cost:
                capital -= cost
                shares_held += shares_to_buy

        # 計算策略資產價值
        total_strategy_value = capital + shares_held * price
        strategy_capital.append(total_strategy_value)

        # 計算基準資產價值
        total_benchmark_value = benchmark_position * price
        benchmark_capital.append(total_benchmark_value)

    # 結果處理
    df['strategy'] = pd.Series(strategy_capital, index=df.index)
    df['benchmark'] = pd.Series(benchmark_capital[:-1], index=df.index)

    return df.reset_index()


def plot_dca_results(results_df, output_dir="project/backtests/dca_strategy"):
    """
    繪製定期買入策略資產曲線與基準資產曲線。

    Args:
        results_df (pd.DataFrame): 包含策略和基準資產曲線的數據表。
        output_dir (str): 保存圖表的目錄。
    """
    if not os.path.exists(FONT_PATH):
        print(f"字體文件未找到：{FONT_PATH}，無法顯示中文。請確保字體文件存在。")
        return
    zh_font = font_manager.FontProperties(fname=FONT_PATH)

    os.makedirs(output_dir, exist_ok=True)

    # 繪製圖表
    plt.figure(figsize=(12, 6))
    plt.plot(results_df['date'], results_df['strategy'], label='策略資產曲線', color='blue')
    plt.plot(results_df['date'], results_df['benchmark'], label='基準資產曲線', color='orange')

    plt.title("定期買入策略與基準資產曲線", fontsize=16, fontproperties=zh_font)
    plt.xlabel("日期", fontsize=12, fontproperties=zh_font)
    plt.ylabel("資金價值", fontsize=12, fontproperties=zh_font)
    plt.legend(prop=zh_font)
    plt.grid(alpha=0.3)

    # 保存圖表和數據
    png_path = os.path.join(output_dir, f"dca_{results_df['date'].iloc[0].date()}_to_{results_df['date'].iloc[-1].date()}_curve.png")
    csv_path = os.path.join(output_dir, "dca_with_benchmark.csv")
    plt.tight_layout()
    plt.savefig(png_path)
    results_df.to_csv(csv_path, index=False)
    print(f"圖表已保存至: {png_path}")
    print(f"數據已保存至: {csv_path}")

    plt.show()


def print_combined_metrics(results_df):
    """
    計算並打印策略與基準的回測指標。

    Args:
        results_df (pd.DataFrame): 包含策略與基準資產曲線的數據表。
    """
    results_df = results_df.dropna(subset=['strategy', 'benchmark'])

    # 計算初始與最終資產
    initial_strategy = results_df['strategy'].iloc[0]
    final_strategy = results_df['strategy'].iloc[-1]
    strategy_return = (final_strategy / initial_strategy - 1) * 100

    initial_benchmark = results_df['benchmark'].iloc[0]
    final_benchmark = results_df['benchmark'].iloc[-1]
    benchmark_return = (final_benchmark / initial_benchmark - 1) * 100

    # 最大回撤計算
    strategy_drawdown = (results_df['strategy'] / results_df['strategy'].cummax() - 1).min() * 100
    benchmark_drawdown = (results_df['benchmark'] / results_df['benchmark'].cummax() - 1).min() * 100

    # 打印結果
    print("\n--- 定期買入策略回測結果 ---")
    print(f"策略總收益率: {strategy_return:.2f}%")
    print(f"基準總收益率: {benchmark_return:.2f}%")
    print(f"策略最大回撤: {strategy_drawdown:.2f}%")
    print(f"基準最大回撤: {benchmark_drawdown:.2f}%")
    print(f"策略最終資產: ${final_strategy:,.2f}")
    print(f"基準最終資產: ${final_benchmark:,.2f}")


# 執行定期買入策略回測
ticker = "AAPL"
initial_capital = 1000
monthly_investment = 500
start_date = "2010-01-01"
end_date = "2024-12-31"

print(f"執行定期買入策略回測: {ticker}")
results_df = backtest_dca_strategy(ticker, initial_capital, monthly_investment, DB_PATH, start_date, end_date)

print("繪製資產曲線...")
plot_dca_results(results_df)

print("打印回測指標...")
print_combined_metrics(results_df)
