"""
Data Preprocessing Pipeline
Handles data loading, cleaning, and preparation for ML models
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import os
from typing import Dict, List, Tuple
import joblib

from config import *
from src.indicators import TechnicalIndicators

class DataPreprocessor:
    """Class for preprocessing financial data for ML models"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.indicators = TechnicalIndicators(INDICATORS_CONFIG)
        
    def load_data(self, symbol: str, timeframe: str, data_dir: str) -> pd.DataFrame:
        """
        Load data from parquet files
        
        Args:
            symbol: Stock/crypto symbol
            timeframe: Timeframe (1m, 5m, 15m)
            data_dir: Directory containing data files
            
        Returns:
            DataFrame with OHLCV data
        """
        filepath = os.path.join(data_dir, f"{symbol}_{timeframe}.parquet")
        
        if os.path.exists(filepath):
            df = pd.read_parquet(filepath)
            print(f"Loaded {len(df)} records for {symbol} {timeframe}")
            return df
        else:
            print(f"Data file not found: {filepath}")
            return pd.DataFrame()
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate data
        
        Args:
            df: Raw OHLCV DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Sort by timestamp
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
            df.set_index('timestamp', inplace=True)
        
        # Remove rows with missing critical data
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        df = df.dropna(subset=required_cols)
        
        # Remove rows with zero volume
        df = df[df['volume'] > 0]
        
        # Remove rows with invalid prices
        df = df[(df['open'] > 0) & (df['high'] > 0) & (df['low'] > 0) & (df['close'] > 0)]
        
        # Ensure high >= max(open, close) and low <= min(open, close)
        df = df[df['high'] >= df[['open', 'close']].max(axis=1)]
        df = df[df['low'] <= df[['open', 'close']].min(axis=1)]
        
        return df
    
    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute technical indicators
        
        Args:
            df: Cleaned OHLCV DataFrame
            
        Returns:
            DataFrame with technical indicators
        """
        return self.indicators.compute_all_indicators(df)
    
    def generate_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate supervised learning labels
        
        Args:
            df: DataFrame with technical indicators
            
        Returns:
            DataFrame with labels
        """
        return self.indicators.generate_labels(df, self.config['signal_threshold'])
    
    def create_sequences(self, df: pd.DataFrame, sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM/GRU models
        
        Args:
            df: DataFrame with features and labels
            sequence_length: Length of input sequences
            
        Returns:
            Tuple of (X, y) arrays
        """
        feature_cols = self.config['features']
        available_features = [col for col in feature_cols if col in df.columns]
        
        # Prepare features
        X = df[available_features].values
        y = df['label'].values
        
        # Create sequences
        X_seq, y_seq = [], []
        
        for i in range(sequence_length, len(X)):
            X_seq.append(X[i-sequence_length:i])
            y_seq.append(y[i])
        
        return np.array(X_seq), np.array(y_seq)
    
    def prepare_training_data(self, df: pd.DataFrame) -> Dict:
        """
        Prepare complete training dataset
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with training data components
        """
        # Clean data
        df_clean = self.clean_data(df)
        
        if df_clean.empty:
            return {}
        
        # Compute indicators
        df_indicators = self.compute_indicators(df_clean)
        
        # Generate labels
        df_labeled = self.generate_labels(df_indicators)
        
        # Create sequences
        X, y = self.create_sequences(df_labeled, self.config['sequence_length'])
        
        # Split data
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=1-self.config['train_ratio'], random_state=42, stratify=y
        )
        
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, 
            test_size=self.config['test_ratio']/(self.config['val_ratio'] + self.config['test_ratio']),
            random_state=42, stratify=y_temp
        )
        
        # Scale features and handle NaN/inf values
        X_train_flat = X_train.reshape(-1, X_train.shape[-1])
        X_val_flat = X_val.reshape(-1, X_val.shape[-1])
        X_test_flat = X_test.reshape(-1, X_test.shape[-1])
        
        # Replace infinite values with 0
        X_train_flat = np.nan_to_num(X_train_flat, nan=0.0, posinf=0.0, neginf=0.0)
        X_val_flat = np.nan_to_num(X_val_flat, nan=0.0, posinf=0.0, neginf=0.0)
        X_test_flat = np.nan_to_num(X_test_flat, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train_flat).reshape(X_train.shape)
        X_val_scaled = self.scaler.transform(X_val_flat).reshape(X_val.shape)
        X_test_scaled = self.scaler.transform(X_test_flat).reshape(X_test.shape)
        
        return {
            'X_train': X_train_scaled,
            'X_val': X_val_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_val': y_val,
            'y_test': y_test,
            'feature_names': self.config['features'],
            'scaler': self.scaler
        }
    
    def save_processed_data(self, data: Dict, symbol: str, timeframe: str):
        """
        Save processed data to files
        
        Args:
            data: Processed training data
            symbol: Stock/crypto symbol
            timeframe: Timeframe
        """
        # Create processed data directory if it doesn't exist
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        
        # Save data arrays
        data_file = os.path.join(PROCESSED_DATA_DIR, f"{symbol}_{timeframe}_processed.npz")
        np.savez(data_file, **{k: v for k, v in data.items() if k not in ['scaler', 'feature_names']})
        
        # Save scaler
        scaler_file = os.path.join(PROCESSED_DATA_DIR, f"{symbol}_{timeframe}_scaler.pkl")
        joblib.dump(data['scaler'], scaler_file)
        
        # Save feature names
        features_file = os.path.join(PROCESSED_DATA_DIR, f"{symbol}_{timeframe}_features.pkl")
        joblib.dump(data['feature_names'], features_file)
        
        print(f"Saved processed data for {symbol} {timeframe}")
    
    def load_processed_data(self, symbol: str, timeframe: str) -> Dict:
        """
        Load processed data from files
        
        Args:
            symbol: Stock/crypto symbol
            timeframe: Timeframe
            
        Returns:
            Dictionary with processed data
        """
        data_file = os.path.join(PROCESSED_DATA_DIR, f"{symbol}_{timeframe}_processed.npz")
        scaler_file = os.path.join(PROCESSED_DATA_DIR, f"{symbol}_{timeframe}_scaler.pkl")
        features_file = os.path.join(PROCESSED_DATA_DIR, f"{symbol}_{timeframe}_features.pkl")
        
        if not all(os.path.exists(f) for f in [data_file, scaler_file, features_file]):
            print(f"Processed data not found for {symbol} {timeframe}")
            return {}
        
        # Load data
        data = np.load(data_file)
        scaler = joblib.load(scaler_file)
        feature_names = joblib.load(features_file)
        
        return {
            'X_train': data['X_train'],
            'X_val': data['X_val'],
            'X_test': data['X_test'],
            'y_train': data['y_train'],
            'y_val': data['y_val'],
            'y_test': data['y_test'],
            'scaler': scaler,
            'feature_names': feature_names
        }
