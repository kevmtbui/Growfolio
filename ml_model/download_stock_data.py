# download_stock_data.py
import yfinance as yf
import os

# Define tickers by category
sector_tickers = {
    "tech": ["AAPL", "MSFT", "NVDA", "GOOG", "META"],
    "finance": ["JPM", "BAC", "GS", "MS", "C"],
    "energy": ["XOM", "CVX", "BP", "SHEL"],
    "healthcare": ["PFE", "JNJ", "MRK", "UNH"],
    "consumer": ["AMZN", "WMT", "COST", "TGT"],
    "hospitality": ["MCD", "DIS", "MAR", "NCLH"],
    "industrials": ["CAT", "GE", "BA", "HON"],
    "real_estate": ["AMT", "PLD", "O", "DHI"],
    "utilities": ["DUK", "NEE", "SO", "AEP"],
    "index_funds": ["SPY", "QQQ", "DIA", "IWM"]
}

# Create folders if not exist
for sector in sector_tickers:
    os.makedirs(f"data/{sector}", exist_ok=True)

# Download data
for sector, tickers in sector_tickers.items():
    for ticker in tickers:
        print(f"📥 Downloading {ticker} ({sector}) ...")
        df = yf.download(ticker, start="2015-01-01", end="2025-01-01")
        save_path = f"data/{sector}/{ticker}.csv"
        df.to_csv(save_path)
        print(f"✅ Saved to {save_path}\n")

print("🎉 All stock data downloaded successfully!")
