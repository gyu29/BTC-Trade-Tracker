import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def fetch_bitcoin_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)  # Fetch 7 days of data
    btc = yf.Ticker("BTC-USD")
    data = btc.history(start=start_date, end=end_date, interval="5m")
    return data

def calculate_signals(data):
    periods = 30
    multiplier = 2.0
    
    data['TR'] = pd.concat([data['High'] - data['Low'],
                            abs(data['High'] - data['Close'].shift()),
                            abs(data['Low'] - data['Close'].shift())], axis=1).max(axis=1)
    
    data['ATR'] = data['TR'].rolling(window=periods).mean()
    data['SRC'] = (data['High'] + data['Low']) / 2
    
    data['up'] = data['SRC'] - multiplier * data['ATR']
    data['dn'] = data['SRC'] + multiplier * data['ATR']
    
    data['trend'] = 0
    data['signal'] = ''
    
    for i in range(1, len(data)):
        if data.iloc[i-1]['Close'] > data.iloc[i-1]['up']:
            data.loc[data.index[i], 'up'] = max(data.iloc[i]['up'], data.iloc[i-1]['up'])
        else:
            data.loc[data.index[i], 'up'] = data.iloc[i]['up']
        
        if data.iloc[i-1]['Close'] < data.iloc[i-1]['dn']:
            data.loc[data.index[i], 'dn'] = min(data.iloc[i]['dn'], data.iloc[i-1]['dn'])
        else:
            data.loc[data.index[i], 'dn'] = data.iloc[i]['dn']
        
        if data.iloc[i-1]['trend'] == -1 and data.iloc[i]['Close'] > data.iloc[i-1]['dn']:
            data.loc[data.index[i], 'trend'] = 1
        elif data.iloc[i-1]['trend'] == 1 and data.iloc[i]['Close'] < data.iloc[i-1]['up']:
            data.loc[data.index[i], 'trend'] = -1
        else:
            data.loc[data.index[i], 'trend'] = data.iloc[i-1]['trend']
    
    # Apply 3-candle consistency rule for entry signals
    for i in range(3, len(data)):
        if (data.iloc[i]['trend'] == 1 and 
            data.iloc[i-1]['trend'] == 1 and 
            data.iloc[i-2]['trend'] == 1 and 
            data.iloc[i-3]['trend'] == -1):
            data.loc[data.index[i], 'signal'] = 'BUY'
        elif (data.iloc[i]['trend'] == -1 and 
              data.iloc[i-1]['trend'] == -1 and 
              data.iloc[i-2]['trend'] == -1 and 
              data.iloc[i-3]['trend'] == 1):
            data.loc[data.index[i], 'signal'] = 'SELL'
        elif data.iloc[i]['trend'] != data.iloc[i-1]['trend']:
            data.loc[data.index[i], 'signal'] = 'WAIT'
    
    return data

def calculate_profit_loss(data):
    position = 0
    entry_price = 0
    trades = []
    
    for i in range(len(data)):
        if data.iloc[i]['signal'] == 'BUY' and position == 0:
            position = 1
            entry_price = data.iloc[i]['Close']
        elif data.iloc[i]['signal'] == 'SELL':
            if position == 1:
                exit_price = data.iloc[i]['Close']
                profit_loss = (exit_price - entry_price) / entry_price * 100
                trades.append({
                    'entry_time': data.index[i-1],
                    'entry_price': entry_price,
                    'exit_time': data.index[i],
                    'exit_price': exit_price,
                    'profit_loss': profit_loss
                })
            position = 0
            entry_price = 0
    
    return trades

def create_chart(data):
    fig = make_subplots(rows=1, cols=2, column_widths=[0.8, 0.2], 
                        specs=[[{"type": "candlestick"}, {"type": "table"}]])
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name="BTC-USD"),
                  row=1, col=1)
    
    # Add buy signals
    buy_signals = data[data['signal'] == 'BUY']
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Low'],
                             mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'),
                             name='Buy Signal'),
                  row=1, col=1)
    
    # Add sell signals
    sell_signals = data[data['signal'] == 'SELL']
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['High'],
                             mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'),
                             name='Sell Signal'),
                  row=1, col=1)
    
    # Signal table
    signals = data[data['signal'] != ''].iloc[-20:]  # Show last 20 signals
    fig.add_trace(go.Table(
        header=dict(values=['Time', 'Signal'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[signals.index.strftime('%Y-%m-%d %H:%M'), signals['signal']],
                   fill_color='lavender',
                   align='left')),
        row=1, col=2)
    
    fig.update_layout(title='Bitcoin Price with Buy/Sell Signals (5-minute timeframe)',
                      xaxis_title='Date',
                      yaxis_title='Price (USD)',
                      height=800)
    
    return fig

def log_trades(trades):
    with open('log.txt', 'w') as f:
        f.write("Trade Log:\n")
        f.write("=" * 80 + "\n")
        for trade in trades:
            f.write(f"Entry Time: {trade['entry_time']}\n")
            f.write(f"Entry Price: ${trade['entry_price']:.2f}\n")
            f.write(f"Exit Time: {trade['exit_time']}\n")
            f.write(f"Exit Price: ${trade['exit_price']:.2f}\n")
            f.write(f"Profit/Loss: {trade['profit_loss']:.2f}%\n")
            f.write("-" * 40 + "\n")
        
        total_profit_loss = sum(trade['profit_loss'] for trade in trades)
        f.write(f"\nTotal Profit/Loss: {total_profit_loss:.2f}%\n")
        f.write(f"Number of Trades: {len(trades)}\n")

def main():
    data = fetch_bitcoin_data()
    data_with_signals = calculate_signals(data)
    trades = calculate_profit_loss(data_with_signals)
    log_trades(trades)
    chart = create_chart(data_with_signals)
    chart.show()

if __name__ == "__main__":
    main()
