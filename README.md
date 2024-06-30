# BTC-Trade-Tracker

BTC-Trade-Tracker analyzes Bitcoin trading signals using yfinance and Plotly. It fetches 7 days of BTC-USD data at 5-minute intervals, calculates buy/sell signals, and evaluates trade profit/loss. It visualizes results with interactive charts and logs trades to a file, helping traders backtest and visualize strategies.

## Features

- Fetches recent Bitcoin price data (BTC-USD) from Yahoo Finance.
- Calculates buy and sell signals using a custom trading algorithm.
- Analyzes profit and loss from identified trades.
- Visualizes Bitcoin price with signals on an interactive chart.
- Logs trade details to a text file.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/BTC-Trade-Tracker.git
   ```

2. Navigate to the project directory:
   ```bash
   cd BTC-Trade-Tracker
   ```
3. Install the required libraries
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main script to start the analysis and visualization:
```bash
python main.py
```

## Requirements

* Python 3.7 or higher
* pandas
* plotly
* yfinance

## License
This project is licensed under the MIT License. See the LICENSE file for more details.