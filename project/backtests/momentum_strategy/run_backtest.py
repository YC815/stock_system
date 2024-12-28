import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

# 設定路徑
DB_PATH = "data/stocks_data.db"
FONT_PATH = "assets/font.ttf"


def backtest_momentum_strategy(ticker, initial_capital, db_path, start_date, end_date, momentum_window=50):
    """
    動能投資策略回測。

    Args:
        ticker (str): 股票代號。
        initial_capital (float): 初始資金。
        db_path (str): SQLite 資料庫路徑。
        start_date (str): 回測開始日期，格式 "YYYY-MM-DD"。
        end_date (str): 回測結束日期，格式 "YYYY-MM-DD"。
        momentum_window (int): 動能計算窗口大小（以天數為單位）。

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

    # 計算動能指標（移動平均線）
    df['momentum'] = df['close'] - df['close'].shift(momentum_window)

    # 初始化資金和資產曲線
    capital = initial_capital
    position = 0  # 持倉股數
    strategy_capital = []
    benchmark_capital = [initial_capital]
    benchmark_position = initial_capital / df['close'].iloc[0]

    buy_signals = []  # 紀錄買入日期
    sell_signals = []  # 紀錄賣出日期

    for i in range(len(df)):
        price = df['close'].iloc[i]
        momentum = df['momentum'].iloc[i]

        # 策略操作
        if momentum > 0:  # 動能為正（買入信號）
            if position == 0:  # 確保沒有持倉才買入
                shares_to_buy = capital // price
                if shares_to_buy > 0:
                    capital -= shares_to_buy * price
                    position += shares_to_buy
                    buy_signals.append(df.index[i])  # 記錄買入日期
        elif momentum < 0:  # 動能為負（賣出信號）
            if position > 0:  # 確保有持倉才賣出
                capital += position * price
                position = 0
                sell_signals.append(df.index[i])  # 記錄賣出日期

        # 計算資產曲線
        strategy_capital.append(capital + position * price)
        benchmark_capital.append(benchmark_position * price)

    # 結果處理
    df['strategy'] = pd.Series(strategy_capital, index=df.index)
    df['benchmark'] = pd.Series(benchmark_capital[:-1], index=df.index)

    return df.reset_index(), buy_signals, sell_signals


def plot_momentum_results(results_df, buy_signals, sell_signals, output_dir="project/backtests/momentum_strategy"):
    """
    繪製動能策略資產曲線與基準資產曲線，並標記買入和賣出點。

    Args:
        results_df (pd.DataFrame): 包含策略和基準資產曲線的數據表。
        buy_signals (list): 買入信號日期列表。
        sell_signals (list): 賣出信號日期列表。
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

    # 標記買入和賣出信號
    for buy_date in buy_signals:
        plt.axvline(x=buy_date, color='green', linestyle='--', alpha=0.5, label='買入信號' if '買入信號' not in plt.gca().get_legend_handles_labels()[1] else "")
    for sell_date in sell_signals:
        plt.axvline(x=sell_date, color='red', linestyle='--', alpha=0.5, label='賣出信號' if '賣出信號' not in plt.gca().get_legend_handles_labels()[1] else "")

    plt.title("動能投資策略與基準資產曲線", fontsize=16, fontproperties=zh_font)
    plt.xlabel("日期", fontsize=12, fontproperties=zh_font)
    plt.ylabel("資金價值", fontsize=12, fontproperties=zh_font)
    plt.legend(prop=zh_font)
    plt.grid(alpha=0.3)

    # 保存圖表和數據
    png_path = os.path.join(output_dir, f"momentum_{results_df['date'].iloc[0].date()}_to_{results_df['date'].iloc[-1].date()}_curve.png")
    csv_path = os.path.join(output_dir, "momentum_with_benchmark.csv")
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
    print("\n--- 動能策略回測結果 ---")
    print(f"策略總收益率: {strategy_return:.2f}%")
    print(f"基準總收益率: {benchmark_return:.2f}%")
    print(f"策略最大回撤: {strategy_drawdown:.2f}%")
    print(f"基準最大回撤: {benchmark_drawdown:.2f}%")
    print(f"策略最終資產: ${final_strategy:,.2f}")
    print(f"基準最終資產: ${final_benchmark:,.2f}")


# 整合到主回測流程
ticker = "AAPL"
initial_capital = 10000
start_date = "2010-01-01"
end_date = "2024-12-31"
momentum_window = 100  # 動能窗口大小

# 執行回測
print(f"執行動能投資策略回測: {ticker}")
results_df, buy_signals, sell_signals = backtest_momentum_strategy(
    ticker, initial_capital, DB_PATH, start_date, end_date, momentum_window
)

# 繪製資產曲線
print("繪製資產曲線...")
plot_momentum_results(results_df, buy_signals, sell_signals)

# 打印回測指標
print_combined_metrics(results_df)
