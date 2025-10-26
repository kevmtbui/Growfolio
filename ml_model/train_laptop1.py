#!/usr/bin/env python3
"""
Laptop 1 Training Script
Trains: INTC models + First 3 crypto models (BTC, ETH, BNB)
Total: 8 models
"""
import os
import time
from src.train_model import TradingModelTrainer

def check_existing_models():
    """Check which models already exist"""
    models_dir = "models"
    existing_models = set()
    
    if os.path.exists(models_dir):
        for file in os.listdir(models_dir):
            if file.endswith('.pth'):
                parts = file.replace('.pth', '').split('_')
                if len(parts) >= 3:
                    ticker = parts[0]
                    timeframe = parts[1]
                    existing_models.add(f"{ticker}_{timeframe}")
    
    return existing_models

def train_laptop1():
    """Train Laptop 1: INTC + BTC, ETH, BNB"""
    print("💻 LAPTOP 1 TRAINING")
    print("=" * 40)
    print("Models: INTC + BTC, ETH, BNB (8 models total)")
    print()
    
    # Laptop 1 models
    laptop1_tickers = ['INTC', 'BTC_USDT', 'ETH_USDT', 'BNB_USDT']
    timeframes = ['5m', '15m']
    
    # Check existing models
    print("Checking existing models...")
    existing_models = check_existing_models()
    
    # Create list of models to train
    models_to_train = []
    for ticker in laptop1_tickers:
        for timeframe in timeframes:
            model_key = f"{ticker}_{timeframe}"
            if model_key not in existing_models:
                models_to_train.append((ticker, timeframe))
            else:
                print(f"  ✓ {ticker} {timeframe} - Already exists")
    
    if not models_to_train:
        print("\n🎉 All Laptop 1 models already exist! Nothing to train.")
        return []
    
    print(f"\nTraining {len(models_to_train)} models on Laptop 1")
    print(f"Estimated time: {len(models_to_train) * 8} minutes")
    print()
    
    trainer = TradingModelTrainer(model_type='lstm')
    results = []
    
    completed = 0
    start_time = time.time()
    
    for i, (ticker, timeframe) in enumerate(models_to_train, 1):
        print(f"[{i}/{len(models_to_train)}] Training {ticker} {timeframe}")
        
        try:
            data = trainer.prepare_data(ticker, timeframe)
            
            if data:
                model_results = trainer.train_model(data, ticker, timeframe, epochs=8)
                completed += 1
                accuracy = model_results['test_acc']
                
                print(f"    ✅ SUCCESS: {ticker} {timeframe}: {accuracy:.4f}")
                
                results.append({
                    'ticker': ticker,
                    'timeframe': timeframe,
                    'accuracy': accuracy,
                    'status': 'success'
                })
            else:
                print(f"    ❌ ERROR: No data for {ticker} {timeframe}")
                results.append({
                    'ticker': ticker,
                    'timeframe': timeframe,
                    'accuracy': 0.0,
                    'status': 'no_data'
                })
                
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
            results.append({
                'ticker': ticker,
                'timeframe': timeframe,
                'accuracy': 0.0,
                'status': f'error: {e}'
            })
        
        # Progress update
        elapsed = time.time() - start_time
        remaining = (elapsed / completed) * (len(models_to_train) - completed) if completed > 0 else 0
        
        print(f"  Progress: {completed}/{len(models_to_train)} models ({completed/len(models_to_train)*100:.1f}%)")
        print(f"  Elapsed: {elapsed/60:.1f}min, Remaining: {remaining/60:.1f}min")
        print()
    
    # Final summary
    end_time = time.time()
    total_time = end_time - start_time
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    
    print("LAPTOP 1 Training Summary:")
    print(f"✅ Successful: {len(successful)} models")
    print(f"❌ Failed: {len(failed)} models")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    
    if successful:
        avg_accuracy = sum(r['accuracy'] for r in successful) / len(successful)
        print(f"📊 Average accuracy: {avg_accuracy:.4f}")
    
    print(f"\n📁 Check models/ folder for trained models")
    return results

def main():
    """Main function"""
    print("🤖 ML Trading Bot - Laptop 1 Training")
    print("=" * 50)
    print("This laptop will train: INTC + BTC, ETH, BNB")
    print("Total models: 8")
    print()
    
    train_laptop1()

if __name__ == "__main__":
    main()
