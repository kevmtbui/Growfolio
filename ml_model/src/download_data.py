"""
Data Download Script
Downloads historical OHLCV data for stocks and cryptocurrencies
"""
import pandas as pd
import numpy as np
import yfinance as yf
import ccxt
import os
from datetime import datetime, timedelta
import time
from typing import List, Dict
import logging

from config import *

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataDownloader:
    """Class for downloading market data from various sources"""
    
    def __init__(self):
        self.binance = ccxt.binance({
            'enableRateLimit': True,
            'sandbox': False  # Set to True for testing
        })
        
    def download_stock_data(self, symbol: str, timeframe: str, 
                           start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        Download stock data using yfinance
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            timeframe: Timeframe ('1m', '5m', '15m')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to today
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Convert timeframe to yfinance format
            interval_map = {
                '1m': '1m',
                '5m': '5m', 
                '15m': '15m'
            }
            
            interval = interval_map.get(timeframe, '5m')
            
            # Download data
            df = ticker.history(
                start=start_date,
                end=end_date or datetime.now().strftime('%Y-%m-%d'),
                interval=interval,
                auto_adjust=True,
                prepost=True
            )
            
            if df.empty:
                logger.warning(f"No data found for {symbol} {timeframe}")
                return pd.DataFrame()
            
            # Clean column names
            df.columns = [col.lower() for col in df.columns]
            
            # Add timestamp column
            df.reset_index(inplace=True)
            df.rename(columns={'Datetime': 'timestamp'}, inplace=True)
            
            logger.info(f"Downloaded {len(df)} records for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            logger.error(f"Error downloading {symbol} {timeframe}: {e}")
            return pd.DataFrame()
    
    def download_crypto_data(self, symbol: str, timeframe: str,
                            start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        Download cryptocurrency data using Binance API
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC/USDT')
            timeframe: Timeframe ('1m', '5m', '15m')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to today
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Convert timeframe to Binance format
            timeframe_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m'
            }
            
            binance_timeframe = timeframe_map.get(timeframe, '5m')
            
            # Convert dates to timestamps
            start_ts = int(pd.to_datetime(start_date).timestamp() * 1000)
            end_ts = int(pd.to_datetime(end_date or datetime.now()).timestamp() * 1000)
            
            # Download OHLCV data
            ohlcv = self.binance.fetch_ohlcv(
                symbol, 
                binance_timeframe, 
                since=start_ts,
                limit=1000
            )
            
            if not ohlcv:
                logger.warning(f"No data found for {symbol} {timeframe}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"Downloaded {len(df)} records for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            logger.error(f"Error downloading {symbol} {timeframe}: {e}")
            return pd.DataFrame()
    
    def download_multiple_stocks(self, symbols: List[str], timeframes: List[str],
                                start_date: str, end_date: str = None) -> Dict:
        """
        Download data for multiple stock symbols
        
        Args:
            symbols: List of stock symbols
            timeframes: List of timeframes
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with downloaded data
        """
        all_data = {}
        
        for symbol in symbols:
            logger.info(f"Downloading data for {symbol}")
            symbol_data = {}
            
            for timeframe in timeframes:
                df = self.download_stock_data(symbol, timeframe, start_date, end_date)
                
                if not df.empty:
                    symbol_data[timeframe] = df
                    logger.info(f"Successfully downloaded {symbol} {timeframe}")
                else:
                    logger.warning(f"Failed to download {symbol} {timeframe}")
                
                # Rate limiting
                time.sleep(0.1)
            
            if symbol_data:
                all_data[symbol] = symbol_data
        
        return all_data
    
    def download_multiple_crypto(self, symbols: List[str], timeframes: List[str],
                                start_date: str, end_date: str = None) -> Dict:
        """
        Download data for multiple cryptocurrency symbols
        
        Args:
            symbols: List of crypto symbols
            timeframes: List of timeframes
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with downloaded data
        """
        all_data = {}
        
        for symbol in symbols:
            logger.info(f"Downloading data for {symbol}")
            symbol_data = {}
            
            for timeframe in timeframes:
                df = self.download_crypto_data(symbol, timeframe, start_date, end_date)
                
                if not df.empty:
                    symbol_data[timeframe] = df
                    logger.info(f"Successfully downloaded {symbol} {timeframe}")
                else:
                    logger.warning(f"Failed to download {symbol} {timeframe}")
                
                # Rate limiting
                time.sleep(0.1)
            
            if symbol_data:
                all_data[symbol] = symbol_data
        
        return all_data
    
    def save_data(self, data: Dict, data_dir: str, asset_type: str):
        """
        Save downloaded data to parquet files
        
        Args:
            data: Dictionary with downloaded data
            data_dir: Directory to save data
            asset_type: 'stocks' or 'crypto'
        """
        os.makedirs(data_dir, exist_ok=True)
        
        for symbol, timeframes in data.items():
            for timeframe, df in timeframes.items():
                filename = f"{symbol}_{timeframe}.parquet"
                filepath = os.path.join(data_dir, filename)
                df.to_parquet(filepath)
                logger.info(f"Saved {symbol} {timeframe} to {filepath}")

def download_sample_data():
    """Download sample data for testing"""
    downloader = DataDownloader()
    
    # Create directories
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    # Download sample stock data
    logger.info("Downloading sample stock data...")
    stock_data = downloader.download_multiple_stocks(
        SAMPLE_STOCKS[:3],  # First 3 stocks
        ['5m', '15m'],       # Sample timeframes
        '2023-01-01',
        '2024-01-01'
    )
    
    # Save stock data
    downloader.save_data(stock_data, RAW_DATA_DIR, 'stocks')
    
    # Download sample crypto data
    logger.info("Downloading sample crypto data...")
    crypto_data = downloader.download_multiple_crypto(
        SAMPLE_CRYPTO[:3],   # First 3 cryptos
        ['5m', '15m'],       # Sample timeframes
        '2023-01-01',
        '2024-01-01'
    )
    
    # Save crypto data
    downloader.save_data(crypto_data, RAW_DATA_DIR, 'crypto')
    
    logger.info("Sample data download completed!")

def download_full_dataset():
    """Download full dataset for production - 150 stocks + 50 cryptos"""
    downloader = DataDownloader()
    
    # Create directories
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    # Download all stock data (150 stocks)
    logger.info(f"Downloading full stock dataset ({len(FULL_STOCKS)} stocks)...")
    stock_data = downloader.download_multiple_stocks(
        FULL_STOCKS,    # All 150 stocks
        TIMEFRAMES,     # All timeframes (1m, 5m, 15m)
        '2022-01-01',   # 2 years of data
        '2024-01-01'
    )
    
    # Save stock data
    downloader.save_data(stock_data, RAW_DATA_DIR, 'stocks')
    
    # Download all crypto data (50 cryptos)
    logger.info(f"Downloading full crypto dataset ({len(FULL_CRYPTO)} cryptos)...")
    crypto_data = downloader.download_multiple_crypto(
        FULL_CRYPTO,    # All 50 cryptos
        TIMEFRAMES,     # All timeframes (1m, 5m, 15m)
        '2022-01-01',   # 2 years of data
        '2024-01-01'
    )
    
    # Save crypto data
    downloader.save_data(crypto_data, RAW_DATA_DIR, 'crypto')
    
    logger.info("Full dataset download completed!")
    logger.info(f"Total symbols: {len(FULL_STOCKS)} stocks + {len(FULL_CRYPTO)} cryptos = {len(FULL_STOCKS) + len(FULL_CRYPTO)} symbols")
    logger.info(f"Total timeframes: {len(TIMEFRAMES)}")
    logger.info(f"Total files: {(len(FULL_STOCKS) + len(FULL_CRYPTO)) * len(TIMEFRAMES)} parquet files")

def main():
    """Main function to run data download"""
    print("ML Trading Bot - Data Downloader")
    print("=" * 50)
    
    choice = input("Choose download option:\n1. Sample data (3 symbols, 2 timeframes)\n2. Full dataset (all symbols, all timeframes)\nEnter choice (1 or 2): ")
    
    if choice == "1":
        print("Downloading sample data...")
        download_sample_data()
    elif choice == "2":
        print("Downloading full dataset...")
        download_full_dataset()
    else:
        print("Invalid choice. Downloading sample data...")
        download_sample_data()
    
    print("Data download completed!")

if __name__ == "__main__":
    main()
