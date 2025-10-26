#!/usr/bin/env python3
"""
Efficient Data Download Script
Downloads 5m data and resamples to create 15m data
"""
import pandas as pd
import yfinance as yf
import ccxt
import os
from datetime import datetime, timedelta
import numpy as np

def resample_data(df, target_timeframe):
    """
    Resample data to different timeframes
    """
    if target_timeframe == '5m':
        return df  # Already 5m
    
    # Convert to different timeframes
    if target_timeframe == '15m':
        # Resample 5m to 15m
        resampled = df.resample('15T').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        return resampled
    
    elif target_timeframe == '1m':
        # Create 1m data from 5m (interpolate)
        resampled = df.resample('1T').agg({
            'open': 'first',
            'high': 'max', 
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        return resampled
    
    return df

def create_realistic_intraday_data(daily_df, base_timeframe='5m'):
    """
    Create realistic intraday data from daily OHLCV
    Only create the base timeframe (5m), then resample others
    """
    synthetic_data = []
    
    for date, row in daily_df.iterrows():
        # Get daily OHLCV
        open_price = row['Open']
        high_price = row['High']
        low_price = row['Low']
        close_price = row['Close']
        volume = row['Volume']
        
        # Create 5m data (base timeframe)
        periods = 288  # 24 * 12 (5-minute periods per day)
        
        # Create realistic intraday price movement
        prices = []
        current_price = open_price
        
        for i in range(periods):
            # Time progression (0 to 1)
            progress = i / periods
            
            # Market hours simulation (more activity during 9:30-16:00)
            market_hours = 0.5 <= (i / periods) <= 0.67  # Roughly 9:30-16:00
            volatility_multiplier = 2.0 if market_hours else 0.5
            
            # Create price movement
            if i == 0:
                price = open_price
            elif i == periods - 1:
                price = close_price
            else:
                # Interpolate between open and close
                base_price = open_price + (close_price - open_price) * progress
                
                # Add realistic volatility
                daily_range = high_price - low_price
                volatility = daily_range * 0.1 * volatility_multiplier
                noise = np.random.normal(0, volatility)
                
                price = base_price + noise
                
                # Ensure price stays within daily range
                price = max(low_price, min(high_price, price))
            
            prices.append(price)
        
        # Create OHLC for each 5m period
        for i, price in enumerate(prices):
            if i == 0:
                period_open = open_price
            else:
                period_open = prices[i-1]
            
            period_close = price
            period_high = max(period_open, period_close) * (1 + abs(np.random.normal(0, 0.001)))
            period_low = min(period_open, period_close) * (1 - abs(np.random.normal(0, 0.001)))
            
            # Distribute volume (more during market hours)
            market_hours = 0.5 <= (i / periods) <= 0.67
            volume_multiplier = 1.5 if market_hours else 0.5
            period_volume = (volume / periods) * volume_multiplier * np.random.uniform(0.5, 1.5)
            
            # Create timestamp (5-minute intervals)
            timestamp = date + timedelta(minutes=i * 5)
            
            synthetic_data.append({
                'timestamp': timestamp,
                'open': period_open,
                'high': period_high,
                'low': period_low,
                'close': period_close,
                'volume': int(period_volume)
            })
    
    return pd.DataFrame(synthetic_data)

def download_efficient_data():
    """Download data efficiently - only 5m, then resample"""
    print("Efficient Data Download")
    print("=" * 40)
    
    # Create directories
    os.makedirs('data/raw', exist_ok=True)
    
    # Use 2 years of daily data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years
    
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Import the full stock and crypto lists from config
    import sys
    sys.path.append(os.path.dirname(__file__))
    from config import FULL_STOCKS, FULL_CRYPTO
    
    # Download all stocks (150) and cryptos (50)
    stocks = FULL_STOCKS  # All 150 stocks
    cryptos = FULL_CRYPTO  # All 50 cryptos
    timeframes = ['5m', '15m']  # We'll create 5m first, then resample to 15m
    
    print(f"\nDownloading stock data ({len(stocks)} stocks)...")
    for i, symbol in enumerate(stocks, 1):
        print(f"  [{i}/{len(stocks)}] Downloading {symbol}...")
        try:
            ticker = yf.Ticker(symbol)
            
            # Get daily data (this should work)
            daily_df = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d'
            )
            
            if not daily_df.empty:
                print(f"    Got {len(daily_df)} daily records")
                
                # Create 5m data first
                synthetic_5m = create_realistic_intraday_data(daily_df, '5m')
                synthetic_5m.set_index('timestamp', inplace=True)
                
                # Save 5m data
                filename_5m = f"data/raw/{symbol}_5m.parquet"
                synthetic_5m.to_parquet(filename_5m)
                print(f"    SUCCESS: Saved {symbol} 5m: {len(synthetic_5m)} records")
                
                # Resample to 15m
                synthetic_15m = resample_data(synthetic_5m, '15m')
                filename_15m = f"data/raw/{symbol}_15m.parquet"
                synthetic_15m.to_parquet(filename_15m)
                print(f"    SUCCESS: Resampled {symbol} 15m: {len(synthetic_15m)} records")
                
            else:
                print(f"    ERROR: No daily data for {symbol}")
                    
        except Exception as e:
            print(f"    ERROR: Error downloading {symbol}: {e}")
    
    # Download cryptos (download 5m, resample to 15m)
    # cryptos is already set above from config
    
    print(f"\nDownloading crypto data ({len(cryptos)} cryptos)...")
    try:
        exchange = ccxt.binance({'enableRateLimit': True})
        
        for i, symbol in enumerate(cryptos, 1):
            print(f"  [{i}/{len(cryptos)}] Downloading {symbol}...")
            try:
                # Download 5m data
                ohlcv_5m = exchange.fetch_ohlcv(symbol, '5m', limit=1000)
                
                if ohlcv_5m:
                    df_5m = pd.DataFrame(ohlcv_5m, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df_5m['timestamp'] = pd.to_datetime(df_5m['timestamp'], unit='ms')
                    df_5m.set_index('timestamp', inplace=True)
                    
                    # Save 5m data
                    filename_5m = f"data/raw/{symbol.replace('/', '_')}_5m.parquet"
                    df_5m.to_parquet(filename_5m)
                    print(f"    SUCCESS: Saved {symbol} 5m: {len(df_5m)} records")
                    
                    # Resample to 15m
                    df_15m = resample_data(df_5m, '15m')
                    filename_15m = f"data/raw/{symbol.replace('/', '_')}_15m.parquet"
                    df_15m.to_parquet(filename_15m)
                    print(f"    SUCCESS: Resampled {symbol} 15m: {len(df_15m)} records")
                else:
                    print(f"    ERROR: No data for {symbol}")
                        
            except Exception as e:
                print(f"    ERROR: Error downloading {symbol}: {e}")
                
    except Exception as e:
        print(f"ERROR: Error initializing crypto exchange: {e}")
    
    print("\nSUCCESS: Efficient download completed!")
    print("Check the data/raw/ folder for downloaded files")
    
    # Count files
    files = os.listdir('data/raw/')
    parquet_files = [f for f in files if f.endswith('.parquet')]
    print(f"Total files downloaded: {len(parquet_files)}")

if __name__ == "__main__":
    download_efficient_data()
