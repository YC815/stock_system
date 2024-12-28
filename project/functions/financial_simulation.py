import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os
import sys


def backtest_sma_strategy(
    ticker="AAPL",
    initial_capital=10000,
    short_window=50,  # 調整短期均線窗口
    long_window=200,  # 調整長期均線窗口
    trading_cost=0.001,  # 每次交易的手續費（假設 0.1%）
    db_path="/Users/yushunchen/.z/pr/stock_system/data/stocks_data.db",
    font_path="assets/font.ttf"
):
    # 強制設定字體
    if not os.path.exists(font_path):
        print(f"字體文件未找到：{font_path}，無法顯示中文。請確保字體文件存在於指定路徑。")
        sys.exit(1)
    zh_font = font_manager.FontProperties(fname=font_path)

    # 獲取歷史數據，限制日期範圍為 2005-2024
    conn = sqlite3.connect(db_path)
    query = f"""
        SELECT date, close
        FROM historical_data
        WHERE ticker='{ticker}' AND date BETWEEN '2005-01-01' AND '2024-12-31'
        ORDER BY date
    """
    stock_data = pd.read_sql(query, conn)
    conn.close()

    # 確保數據不為空
    if stock_data.empty:
        print(f"找不到股票代號 '{ticker}' 的數據或範圍內沒有數據。")
        return

    # 日期處理
    stock_data['date'] = pd.to_datetime(stock_data['date'])
    stock_data.set_index('date', inplace=True)

    # 計算移動平均線
    stock_data['SMA_short'] = stock_data['close'].rolling(window=short_window).mean()
    stock_data['SMA_long'] = stock_data['close'].rolling(window=long_window).mean()

    # 生成交易信號
    stock_data['signal'] = 0
    stock_data.loc[stock_data['SMA_short'] > stock_data['SMA_long'], 'signal'] = 1  # 買入信號
    stock_data.loc[stock_data['SMA_short'] <= stock_data['SMA_long'], 'signal'] = 0  # 賣出信號
    stock_data['position'] = stock_data['signal'].shift(1)  # 當日執行前一日的信號

    # 計算每日收益
    stock_data['daily_return'] = stock_data['close'].pct_change()
    stock_data['strategy_return'] = stock_data['position'] * stock_data['daily_return']

    # 加入交易成本
    transaction_count = stock_data['signal'].diff().abs()  # 計算交易次數
    stock_data['strategy_return'] -= transaction_count * trading_cost

    # 資金曲線
    stock_data['portfolio'] = initial_capital * (1 + stock_data['strategy_return']).cumprod()

    # 可視化結果
    plt.figure(figsize=(14, 7))
    plt.plot(stock_data['portfolio'], label='策略資產曲線')
    plt.plot(initial_capital * (1 + stock_data['daily_return']).cumprod(), label='基準資產曲線 (買入並持有)')
    plt.title(f"{ticker} SMA 策略回測 (2005-2024)", fontsize=16, fontproperties=zh_font)
    plt.xlabel("日期", fontsize=12, fontproperties=zh_font)
    plt.ylabel("資產價值", fontsize=12, fontproperties=zh_font)
    plt.legend(prop=zh_font)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 輸出總結
    total_return = stock_data['portfolio'].iloc[-1] / initial_capital - 1
    print(f"總收益率: {total_return:.2%}")
    max_drawdown = (stock_data['portfolio'] / stock_data['portfolio'].cummax() - 1).min()
    print(f"最大回撤: {max_drawdown:.2%}")
    print(f"最終資產: ${stock_data['portfolio'].iloc[-1]:.2f}")


# 執行回測
backtest_sma_strategy(
    ticker="AAPL",
    initial_capital=10000,
    short_window=50,  # 調整短期均線
    long_window=200,  # 調整長期均線
    trading_cost=0.001,  # 每次交易成本（0.1%）
    font_path="assets/font.ttf"  # 強制指定字體路徑
)
