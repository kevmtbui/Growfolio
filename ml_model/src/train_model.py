"""
Model Training Script
Trains PyTorch models for trading signal prediction
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import os
import json
from datetime import datetime
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from config import *
from src.models import ModelFactory, ModelTrainer, TradingDataset
from src.preprocess_data import DataPreprocessor

class TradingModelTrainer:
    """Main class for training trading models"""
    
    def __init__(self, model_type: str = 'lstm', device: str = None):
        self.model_type = model_type
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.preprocessor = DataPreprocessor(MODEL_CONFIG)
        
        print(f"Using device: {self.device}")
        
    def prepare_data(self, symbol: str, timeframe: str, data_dir: str = RAW_DATA_DIR):
        """
        Prepare training data for a specific symbol and timeframe
        
        Args:
            symbol: Stock/crypto symbol
            timeframe: Timeframe (1m, 5m, 15m)
            data_dir: Directory containing raw data
            
        Returns:
            Dictionary with training data
        """
        print(f"Preparing data for {symbol} {timeframe}")
        
        # Load raw data
        df = self.preprocessor.load_data(symbol, timeframe, data_dir)
        
        if df.empty:
            print(f"No data found for {symbol} {timeframe}")
            return {}
        
        # Prepare training data
        try:
            data = self.preprocessor.prepare_training_data(df)
            
            if not data:
                print(f"Failed to prepare data for {symbol} {timeframe}")
                return {}
        except Exception as e:
            print(f"Error preparing data for {symbol} {timeframe}: {e}")
            return {}
        
        # Save processed data
        self.preprocessor.save_processed_data(data, symbol, timeframe)
        
        return data
    
    def train_model(self, data: dict, symbol: str, timeframe: str, 
                   epochs: int = None, batch_size: int = None) -> dict:
        """
        Train a model on the prepared data
        
        Args:
            data: Training data dictionary
            symbol: Stock/crypto symbol
            timeframe: Timeframe
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Dictionary with training results
        """
        epochs = epochs or MODEL_CONFIG['epochs']
        batch_size = batch_size or MODEL_CONFIG['batch_size']
        
        print(f"Training {self.model_type} model for {symbol} {timeframe}")
        
        # Create datasets
        train_dataset = TradingDataset(data['X_train'], data['y_train'])
        val_dataset = TradingDataset(data['X_val'], data['y_val'])
        test_dataset = TradingDataset(data['X_test'], data['y_test'])
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        
        # Create model
        input_size = data['X_train'].shape[-1]
        model = ModelFactory.create_model(self.model_type, input_size, MODEL_CONFIG)
        
        # Create trainer
        trainer = ModelTrainer(model, self.device)
        
        # Setup training
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), 
                             lr=MODEL_CONFIG['learning_rate'],
                             weight_decay=MODEL_CONFIG['weight_decay'])
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
        
        # Training loop
        train_losses = []
        val_losses = []
        val_accuracies = []
        best_val_acc = 0
        patience_counter = 0
        
        for epoch in range(epochs):
            # Train
            train_loss = trainer.train_epoch(train_loader, optimizer, criterion)
            train_losses.append(train_loss)
            
            # Validate
            val_loss, val_acc = trainer.validate_epoch(val_loader, criterion)
            val_losses.append(val_loss)
            val_accuracies.append(val_acc)
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            # Early stopping
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                patience_counter = 0
                # Save best model
                self.save_model(model, symbol, timeframe)
            else:
                patience_counter += 1
            
            if patience_counter >= MODEL_CONFIG['early_stopping_patience']:
                print(f"Early stopping at epoch {epoch}")
                break
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Train Loss: {train_loss:.4f}, "
                      f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
        
        # Final evaluation
        test_loss, test_acc = trainer.validate_epoch(test_loader, criterion)
        predictions, probabilities = trainer.predict(test_loader)
        
        # Generate reports
        y_test = data['y_test']
        report = classification_report(y_test, predictions, 
                                    target_names=['Sell', 'Hold', 'Buy'],
                                    output_dict=True)
        
        # Save results
        results = {
            'model_type': self.model_type,
            'symbol': symbol,
            'timeframe': timeframe,
            'best_val_acc': best_val_acc,
            'test_acc': test_acc,
            'test_loss': test_loss,
            'classification_report': report,
            'train_losses': train_losses,
            'val_losses': val_losses,
            'val_accuracies': val_accuracies
        }
        
        self.save_results(results, symbol, timeframe)
        # Disable plotting in background threads to avoid macOS GUI issues
        # self.plot_training_history(results, symbol, timeframe)
        
        return results
    
    def save_model(self, model: nn.Module, symbol: str, timeframe: str):
        """Save trained model"""
        model_path = os.path.join(MODELS_DIR, f"{symbol}_{timeframe}_{self.model_type}.pth")
        torch.save({
            'model_state_dict': model.state_dict(),
            'model_type': self.model_type,
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat()
        }, model_path)
        print(f"Model saved to {model_path}")
    
    def save_results(self, results: dict, symbol: str, timeframe: str):
        """Save training results"""
        results_path = os.path.join(RESULTS_DIR, f"{symbol}_{timeframe}_{self.model_type}_results.json")
        
        # Convert numpy arrays to lists for JSON serialization
        serializable_results = results.copy()
        for key, value in serializable_results.items():
            if isinstance(value, np.ndarray):
                serializable_results[key] = value.tolist()
        
        with open(results_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"Results saved to {results_path}")
    
    def plot_training_history(self, results: dict, symbol: str, timeframe: str):
        """Plot training history"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Loss plot
        ax1.plot(results['train_losses'], label='Train Loss')
        ax1.plot(results['val_losses'], label='Validation Loss')
        ax1.set_title(f'Training History - {symbol} {timeframe}')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Accuracy plot
        ax2.plot(results['val_accuracies'], label='Validation Accuracy')
        ax2.set_title(f'Validation Accuracy - {symbol} {timeframe}')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(RESULTS_DIR, f"{symbol}_{timeframe}_{self.model_type}_history.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Training history plot saved to {plot_path}")

def main():
    """Main training function"""
    # Example usage
    trainer = TradingModelTrainer(model_type='lstm')
    
    # Train on sample data
    symbols = SAMPLE_STOCKS[:3]  # First 3 stocks
    timeframes = ['5m', '15m']  # Sample timeframes
    
    for symbol in symbols:
        for timeframe in timeframes:
            print(f"\n{'='*50}")
            print(f"Training {symbol} {timeframe}")
            print(f"{'='*50}")
            
            # Prepare data
            data = trainer.prepare_data(symbol, timeframe)
            
            if data:
                # Train model
                results = trainer.train_model(data, symbol, timeframe)
                print(f"Training completed for {symbol} {timeframe}")
                print(f"Best validation accuracy: {results['best_val_acc']:.4f}")
                print(f"Test accuracy: {results['test_acc']:.4f}")

if __name__ == "__main__":
    main()
