#!/usr/bin/env python3
"""
Train Top 20 Tickers
Fast training on the most important symbols
"""
import os
import time
from src.train_model import TradingModelTrainer

def train_top20_tickers():
    """Train on top 20 most important tickers"""
    print("Training Top 20 Tickers")
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
    
    print(f"Training {len(top20_tickers)} tickers × {len(timeframes)} timeframes = {len(top20_tickers) * len(timeframes)} models")
    print("Estimated time: ~1-2 hours")
    print()
    
    trainer = TradingModelTrainer(model_type='lstm')
    results = []
    
    total_models = len(top20_tickers) * len(timeframes)
    completed = 0
    
    start_time = time.time()
    
    for i, ticker in enumerate(top20_tickers, 1):
        print(f"[{i}/{len(top20_tickers)}] Training {ticker}")
        
        for timeframe in timeframes:
            print(f"  {ticker} {timeframe}...")
            
            try:
                # Prepare data
                data = trainer.prepare_data(ticker, timeframe)
                
                if data:
                    # Train model with reduced epochs for speed
                    model_results = trainer.train_model(data, ticker, timeframe, epochs=10)
                    
                    completed += 1
                    accuracy = model_results['test_acc']
                    
                    print(f"    SUCCESS: {ticker} {timeframe}: {accuracy:.4f} ({completed}/{total_models})")
                    
                    results.append({
                        'ticker': ticker,
                        'timeframe': timeframe,
                        'accuracy': accuracy,
                        'status': 'success'
                    })
                else:
                    print(f"    ERROR: No data for {ticker} {timeframe}")
                    results.append({
                        'ticker': ticker,
                        'timeframe': timeframe,
                        'accuracy': 0.0,
                        'status': 'no_data'
                    })
                    
            except Exception as e:
                print(f"    ERROR: {e}")
                results.append({
                    'ticker': ticker,
                    'timeframe': timeframe,
                    'accuracy': 0.0,
                    'status': f'error: {e}'
                })
        
        # Progress update
        elapsed = time.time() - start_time
        remaining = (elapsed / completed) * (total_models - completed) if completed > 0 else 0
        
        print(f"  Progress: {completed}/{total_models} models ({completed/total_models*100:.1f}%)")
        print(f"  Elapsed: {elapsed/60:.1f}min, Remaining: {remaining/60:.1f}min")
        print()
    
    # Final summary
    end_time = time.time()
    total_time = end_time - start_time
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    
    print("Training Summary:")
    print(f"Successful: {len(successful)} models")
    print(f"Failed: {len(failed)} models")
    print(f"Total time: {total_time/60:.1f} minutes")
    
    if successful:
        avg_accuracy = sum(r['accuracy'] for r in successful) / len(successful)
        print(f"Average accuracy: {avg_accuracy:.4f}")
        
        # Show best performers
        best_models = sorted(successful, key=lambda x: x['accuracy'], reverse=True)[:5]
        print(f"\nTop 5 Models:")
        for i, model in enumerate(best_models, 1):
            print(f"  {i}. {model['ticker']} {model['timeframe']}: {model['accuracy']:.4f}")
    
    print(f"\nCheck models/ folder for trained models")
    return results

def main():
    """Main function"""
    print("ML Trading Bot - Top 20 Tickers Training")
    print("=" * 50)
    
    # Auto-start training (no user input required)
    print("Starting training automatically...")
    train_top20_tickers()

if __name__ == "__main__":
    main()
