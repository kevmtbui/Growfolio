"""
Technical Indicators Module
Computes various technical indicators for ML feature engineering
"""
import pandas as pd
import numpy as np
import ta
from typing import Dict, List

class TechnicalIndicators:
    """Class for computing technical indicators"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    def compute_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute all technical indicators for a given OHLCV dataframe
        
        Args:
            df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
            
        Returns:
            DataFrame with original data + technical indicators
        """
        df = df.copy()
        
        # Ensure we have the required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")
        
        # Compute indicators
        df = self._compute_momentum_indicators(df)
        df = self._compute_trend_indicators(df)
        df = self._compute_volatility_indicators(df)
        df = self._compute_volume_indicators(df)
        df = self._compute_price_features(df)
        
        return df
    
    def _compute_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute momentum-based indicators"""
        # RSI
        df['rsi_14'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        return df
    
    def _compute_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute trend-based indicators"""
        # EMAs
        for period in self.config['ema_periods']:
            df[f'ema_{period}'] = ta.trend.EMAIndicator(df['close'], window=period).ema_indicator()
        
        # SMA for comparison
        df['sma_20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
        df['sma_50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
        
        return df
    
    def _compute_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute volatility-based indicators"""
        # ATR
        df['atr_14'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_middle'] = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # Rolling volatility
        df['volatility'] = df['close'].pct_change().rolling(window=20).std()
        
        return df
    
    def _compute_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute volume-based indicators"""
        # VWAP (Volume Weighted Average Price) - manual calculation
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
        
        # Volume SMA
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        
        # On Balance Volume
        df['obv'] = ta.volume.OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()
        
        return df
    
    def _compute_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute price-based features"""
        # Price change percentage
        df['price_change_pct'] = df['close'].pct_change()
        
        # High-Low percentage
        df['hl_pct'] = (df['high'] - df['low']) / df['close']
        
        # Close-Open percentage
        df['co_pct'] = (df['close'] - df['open']) / df['open']
        
        # Price position within the day's range
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        # Log returns
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        return df
    
    def generate_labels(self, df: pd.DataFrame, threshold: float = 0.005) -> pd.DataFrame:
        """
        Generate supervised learning labels based on future returns
        
        Args:
            df: DataFrame with price data
            threshold: Threshold for buy/sell signals (default 0.5%)
            
        Returns:
            DataFrame with labels added
        """
        df = df.copy()
        
        # Calculate future returns (next period)
        df['future_return'] = df['close'].shift(-1) / df['close'] - 1
        
        # Generate labels (convert to 0, 1, 2 for PyTorch)
        df['label'] = 1  # Default: Hold (encoded as 1)
        df.loc[df['future_return'] > threshold, 'label'] = 2   # Buy (encoded as 2)
        df.loc[df['future_return'] < -threshold, 'label'] = 0  # Sell (encoded as 0)
        
        # Print label distribution for debugging
        label_counts = df['label'].value_counts().sort_index()
        print(f"Label distribution: Sell={label_counts.get(0, 0)}, Hold={label_counts.get(1, 0)}, Buy={label_counts.get(2, 0)}")
        
        # If too imbalanced, adjust threshold
        total_samples = len(df)
        sell_ratio = label_counts.get(0, 0) / total_samples
        buy_ratio = label_counts.get(2, 0) / total_samples
        
        if sell_ratio < 0.05 or buy_ratio < 0.05:  # Less than 5% for either class
            print(f"Warning: Data is imbalanced! Sell: {sell_ratio:.1%}, Buy: {buy_ratio:.1%}")
            print("Consider adjusting the signal_threshold in config.py")
        
        # Remove the last row (no future return available)
        df = df[:-1]
        
        return df
    
    def get_feature_columns(self) -> List[str]:
        """Get list of feature columns for ML model"""
        return [
            'open', 'high', 'low', 'close', 'volume',
            'rsi_14', 'ema_9', 'ema_21', 'ema_50',
            'macd', 'macd_signal', 'macd_histogram',
            'atr_14', 'vwap', 'price_change_pct', 'volatility',
            'bb_width', 'hl_pct', 'co_pct', 'price_position'
        ]
    
    def prepare_ml_features(self, df: pd.DataFrame, user_features: Dict = None) -> pd.DataFrame:
        """
        Prepare features for ML model training
        
        Args:
            df: DataFrame with technical indicators
            user_features: Dictionary with user-specific features
            
        Returns:
            DataFrame ready for ML training
        """
        # Get feature columns
        feature_cols = self.get_feature_columns()
        
        # Filter available features
        available_features = [col for col in feature_cols if col in df.columns]
        ml_df = df[available_features].copy()
        
        # Add user features if provided
        if user_features:
            for key, value in user_features.items():
                ml_df[key] = value
        
        # Fill NaN values and handle infinite values
        ml_df = ml_df.ffill().fillna(0)
        
        # Replace infinite values with 0
        ml_df = ml_df.replace([np.inf, -np.inf], 0)
        
        # Ensure all values are finite
        ml_df = ml_df.fillna(0)
        
        return ml_df
