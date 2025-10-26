#!/usr/bin/env python3
"""
Smart Train Top 20 Tickers
Skips existing models and only trains missing ones
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
                # Extract ticker and timeframe from filename
                # Format: TICKER_TIMEFRAME_MODELTYPE.pth
                parts = file.replace('.pth', '').split('_')
                if len(parts) >= 3:
                    ticker = parts[0]
                    timeframe = parts[1]
                    existing_models.add(f"{ticker}_{timeframe}")
    
    return existing_models

def train_top20_tickers_smart():
    """Train on top 20 most important tickers, skipping existing models"""
    print("Smart Training - Top 20 Tickers")
    print("=" * 40)
    
    # Top 20 most important tickers
    top20_tickers = [
        # Top 10 Stocks
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
        'NVDA', 'META', 'NFLX', 'AMD', 'INTC',
        
        # Top 10 Cryptos
        'BTC_USDT', 'ETH_USDT', 'BNB_USDT', 'XRP_USDT', 'ADA_USDT',
        'SOL_USDT', 'DOGE_USDT', 'DOT_USDT', 'AVAX_USDT', 'SHIB_USDT'
    ]
    
    timeframes = ['5m', '15m']
    
    # Check existing models
    print("Checking existing models...")
    existing_models = check_existing_models()
    
    # Create list of models to train
    models_to_train = []
    for ticker in top20_tickers:
        for timeframe in timeframes:
            model_key = f"{ticker}_{timeframe}"
            if model_key not in existing_models:
                models_to_train.append((ticker, timeframe))
            else:
                print(f"  ✓ {ticker} {timeframe} - Already exists")
    
    if not models_to_train:
        print("\n🎉 All models already exist! Nothing to train.")
        return []
    
    print(f"\nTraining {len(models_to_train)} missing models")
    print(f"Total possible: {len(top20_tickers) * len(timeframes)} models")
    print(f"Already exist: {len(existing_models)} models")
    print(f"Need training: {len(models_to_train)} models")
    print()
    
    trainer = TradingModelTrainer(model_type='lstm')
    results = []
    
    completed = 0
    start_time = time.time()
    
    for i, (ticker, timeframe) in enumerate(models_to_train, 1):
        print(f"[{i}/{len(models_to_train)}] Training {ticker} {timeframe}")
        
        try:
            # Prepare data
            data = trainer.prepare_data(ticker, timeframe)
            
            if data:
                # Train model with reduced epochs for speed
                model_results = trainer.train_model(data, ticker, timeframe, epochs=10)
                
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
    
    print("Training Summary:")
    print(f"✅ Successful: {len(successful)} models")
    print(f"❌ Failed: {len(failed)} models")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    
    if successful:
        avg_accuracy = sum(r['accuracy'] for r in successful) / len(successful)
        print(f"📊 Average accuracy: {avg_accuracy:.4f}")
        
        # Show best performers
        best_models = sorted(successful, key=lambda x: x['accuracy'], reverse=True)[:5]
        print(f"\n🏆 Top 5 New Models:")
        for i, model in enumerate(best_models, 1):
            print(f"  {i}. {model['ticker']} {model['timeframe']}: {model['accuracy']:.4f}")
    
    # Show final model count
    final_existing = check_existing_models()
    print(f"\n📁 Total models now: {len(final_existing)}")
    print(f"📁 Check models/ folder for all trained models")
    
    return results

def main():
    """Main function"""
    print("ML Trading Bot - Smart Top 20 Tickers Training")
    print("=" * 55)
    print("This script will only train models that don't already exist.")
    print()
    
    # Auto-start training (no user input required)
    print("Starting smart training...")
    train_top20_tickers_smart()

if __name__ == "__main__":
    main()
