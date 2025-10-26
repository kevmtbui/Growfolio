"""
Live Prediction Script
Real-time trading signal prediction using trained models
"""
import torch
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Tuple

from config import *
from src.models import ModelFactory, ModelTrainer, TradingDataset
from src.preprocess_data import DataPreprocessor
from src.indicators import TechnicalIndicators

class LivePredictor:
    """Class for live trading signal prediction"""
    
    def __init__(self, model_type: str = 'lstm', device: str = None):
        self.model_type = model_type
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.preprocessor = DataPreprocessor(MODEL_CONFIG)
        self.indicators = TechnicalIndicators(INDICATORS_CONFIG)
        self.models = {}  # Cache for loaded models
        self.scalers = {}  # Cache for loaded scalers
        
    def load_model(self, symbol: str, timeframe: str) -> bool:
        """
        Load trained model for a specific symbol and timeframe
        
        Args:
            symbol: Stock/crypto symbol
            timeframe: Timeframe
            
        Returns:
            True if model loaded successfully
        """
        model_path = os.path.join(MODELS_DIR, f"{symbol}_{timeframe}_{self.model_type}.pth")
        scaler_path = os.path.join(PROCESSED_DATA_DIR, f"{symbol}_{timeframe}_scaler.pkl")
        
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            print(f"Model or scaler not found for {symbol} {timeframe}")
            return False
        
        try:
            # Load model
            checkpoint = torch.load(model_path, map_location=self.device)
            input_size = len(MODEL_CONFIG['features'])
            model = ModelFactory.create_model(self.model_type, input_size, MODEL_CONFIG)
            model.load_state_dict(checkpoint['model_state_dict'])
            model.eval()
            
            # Load scaler
            import joblib
            scaler = joblib.load(scaler_path)
            
            # Cache model and scaler
            model_key = f"{symbol}_{timeframe}"
            self.models[model_key] = model
            self.scalers[model_key] = scaler
            
            print(f"Model loaded for {symbol} {timeframe}")
            return True
            
        except Exception as e:
            print(f"Error loading model for {symbol} {timeframe}: {e}")
            return False
    
    def prepare_live_features(self, df: pd.DataFrame, symbol: str, timeframe: str) -> np.ndarray:
        """
        Prepare features for live prediction
        
        Args:
            df: DataFrame with recent OHLCV data
            symbol: Stock/crypto symbol
            timeframe: Timeframe
            
        Returns:
            Prepared features array
        """
        # Compute indicators
        df_with_indicators = self.indicators.compute_all_indicators(df)
        
        # Prepare ML features
        feature_cols = MODEL_CONFIG['features']
        available_features = [col for col in feature_cols if col in df_with_indicators.columns]
        
        # Get the last sequence_length rows
        sequence_length = MODEL_CONFIG['sequence_length']
        if len(df_with_indicators) < sequence_length:
            print(f"Not enough data for prediction. Need {sequence_length}, got {len(df_with_indicators)}")
            return None
        
        # Extract features
        features = df_with_indicators[available_features].tail(sequence_length).values
        
        # Scale features
        model_key = f"{symbol}_{timeframe}"
        if model_key in self.scalers:
            features_scaled = self.scalers[model_key].transform(features)
        else:
            print(f"Scaler not found for {symbol} {timeframe}")
            return None
        
        # Reshape for model input (batch_size=1, sequence_length, features)
        features_scaled = features_scaled.reshape(1, sequence_length, -1)
        
        return features_scaled
    
    def predict_signal(self, df: pd.DataFrame, symbol: str, timeframe: str, 
                      user_features: Dict = None) -> Dict:
        """
        Predict trading signal for given data
        
        Args:
            df: DataFrame with recent OHLCV data
            symbol: Stock/crypto symbol
            timeframe: Timeframe
            user_features: User-specific features (risk tolerance, etc.)
            
        Returns:
            Dictionary with prediction results
        """
        model_key = f"{symbol}_{timeframe}"
        
        if model_key not in self.models:
            if not self.load_model(symbol, timeframe):
                return {'error': 'Model not available'}
        
        try:
            # Prepare features
            features = self.prepare_live_features(df, symbol, timeframe)
            if features is None:
                return {'error': 'Insufficient data for prediction'}
            
            # Make prediction
            model = self.models[model_key]
            features_tensor = torch.FloatTensor(features).to(self.device)
            
            with torch.no_grad():
                outputs = model(features_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                predicted_class = torch.argmax(outputs, dim=1).item()
                confidence = torch.max(probabilities, dim=1)[0].item()
            
            # Convert prediction to action (0=Sell, 1=Hold, 2=Buy)
            action_map = {0: 'Sell', 1: 'Hold', 2: 'Buy'}
            action = action_map[predicted_class]
            
            # Get probability distribution
            prob_dist = probabilities.cpu().numpy()[0]
            
            # Apply risk adjustment
            risk_adjusted_action = self._apply_risk_adjustment(
                action, confidence, user_features or USER_CONFIG
            )
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'risk_adjusted_action': risk_adjusted_action,
                'confidence': confidence,
                'probabilities': {
                    'sell': float(prob_dist[0]),  # Class 0
                    'hold': float(prob_dist[1]),  # Class 1
                    'buy': float(prob_dist[2])    # Class 2
                },
                'user_features': user_features
            }
            
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}
    
    def _apply_risk_adjustment(self, action: str, confidence: float, 
                              user_features: Dict) -> str:
        """
        Apply risk-based adjustments to the prediction
        
        Args:
            action: Original predicted action
            confidence: Model confidence
            user_features: User risk preferences
            
        Returns:
            Risk-adjusted action
        """
        risk_tolerance = user_features.get('risk_tolerance', 5)
        confidence_threshold = 0.5 + (risk_tolerance - 5) * 0.05  # 0.3 to 0.7
        
        # If confidence is below threshold, default to Hold
        if confidence < confidence_threshold:
            return 'Hold'
        
        # If risk tolerance is low and action is Buy/Sell, be more conservative
        if risk_tolerance < 4 and action in ['Buy', 'Sell']:
            return 'Hold'
        
        return action
    
    def batch_predict(self, data_dict: Dict[str, pd.DataFrame], 
                     user_features: Dict = None) -> List[Dict]:
        """
        Make predictions for multiple symbols/timeframes
        
        Args:
            data_dict: Dictionary with (symbol, timeframe) as keys
            user_features: User risk preferences
            
        Returns:
            List of prediction results
        """
        predictions = []
        
        for (symbol, timeframe), df in data_dict.items():
            result = self.predict_signal(df, symbol, timeframe, user_features)
            predictions.append(result)
        
        return predictions
    
    def save_predictions(self, predictions: List[Dict], filename: str = None):
        """
        Save predictions to file
        
        Args:
            predictions: List of prediction results
            filename: Output filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"predictions_{timestamp}.json"
        
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump(predictions, f, indent=2)
        
        print(f"Predictions saved to {filepath}")

def main():
    """Example usage of live predictor"""
    predictor = LivePredictor(model_type='lstm')
    
    # Example: Load sample data and make prediction
    # This would typically come from live data feeds
    sample_data = {
        'AAPL_5m': pd.DataFrame({
            'open': np.random.randn(100) * 0.01 + 150,
            'high': np.random.randn(100) * 0.01 + 151,
            'low': np.random.randn(100) * 0.01 + 149,
            'close': np.random.randn(100) * 0.01 + 150,
            'volume': np.random.randint(1000, 10000, 100)
        })
    }
    
    # Make predictions
    user_config = {
        'risk_tolerance': 7,
        'investment_amount': 10000,
        'desired_profit_pct': 0.02
    }
    
    for (symbol, timeframe), df in sample_data.items():
        symbol_name, tf = symbol.split('_')
        result = predictor.predict_signal(df, symbol_name, tf, user_config)
        print(f"Prediction for {symbol}: {result}")

if __name__ == "__main__":
    main()
