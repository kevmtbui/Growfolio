"""
ML Model Loader - Downloads models from Hugging Face on Railway deployment
"""
import os
from pathlib import Path
from typing import Optional

# Configuration - UPDATE THIS WITH YOUR HUGGING FACE REPO
REPO_NAME = "your-username/growfolio-models"  # Example: "john-doe/growfolio-models"

# Directories
BASE_DIR = Path(__file__).parent.parent
MODEL_DIR = BASE_DIR / "ml_model" / "models"
PROCESSED_DATA_DIR = BASE_DIR / "ml_model" / "data" / "processed"

# Create directories if they don't exist
MODEL_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

class ModelLoader:
    """Load ML models from Hugging Face Hub"""
    
    def __init__(self):
        self.repo_name = REPO_NAME
        self.model_dir = MODEL_DIR
        self.hf_available = False
        
        # Check if huggingface_hub is available
        try:
            from huggingface_hub import hf_hub_download
            self.hf_hub_download = hf_hub_download
            self.hf_available = True
            print("✓ Hugging Face Hub available")
        except ImportError:
            print("⚠️  huggingface_hub not installed - ML models will not be available")
            print("   Install with: pip install huggingface_hub")
    
    def download_model(self, model_name: str) -> Optional[Path]:
        """
        Download a model from Hugging Face Hub
        
        Args:
            model_name: Name of the model file (e.g., "AAPL_5m_lstm.pth")
            
        Returns:
            Path to the downloaded model, or None if failed
        """
        if not self.hf_available:
            print(f"✗ Cannot download {model_name}: huggingface_hub not available")
            return None
        
        # Check if model already exists locally
        local_path = self.model_dir / model_name
        if local_path.exists():
            print(f"✓ Model {model_name} already cached locally")
            return local_path
        
        # Download from Hugging Face
        try:
            print(f"Downloading {model_name} from Hugging Face...")
            downloaded_path = self.hf_hub_download(
                repo_id=self.repo_name,
                filename=model_name,
                repo_type="model",
                cache_dir=str(self.model_dir.parent),
                local_dir=str(self.model_dir),
                local_dir_use_symlinks=False
            )
            print(f"✓ Downloaded {model_name}")
            return Path(downloaded_path)
        except Exception as e:
            print(f"✗ Failed to download {model_name}: {e}")
            return None
    
    def download_all_models(self, symbols: list = None, timeframes: list = None, model_types: list = None):
        """
        Download multiple models
        
        Args:
            symbols: List of symbols (default: top 5 stocks)
            timeframes: List of timeframes (default: ["5m", "15m"])
            model_types: List of model types (default: ["lstm"])
        """
        if symbols is None:
            symbols = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL"]
        
        if timeframes is None:
            timeframes = ["5m", "15m"]
        
        if model_types is None:
            model_types = ["lstm"]
        
        print(f"\nDownloading models from: {self.repo_name}")
        print("=" * 80)
        
        total = len(symbols) * len(timeframes) * len(model_types)
        downloaded = 0
        
        for symbol in symbols:
            for timeframe in timeframes:
                for model_type in model_types:
                    model_name = f"{symbol}_{timeframe}_{model_type}.pth"
                    if self.download_model(model_name):
                        downloaded += 1
        
        print("=" * 80)
        print(f"✓ Downloaded {downloaded}/{total} models")
        
        return downloaded > 0
    
    def get_model_path(self, symbol: str, timeframe: str, model_type: str = "lstm") -> Optional[Path]:
        """
        Get path to a model, downloading if necessary
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            timeframe: Timeframe (e.g., "5m", "15m")
            model_type: Model type (default: "lstm")
            
        Returns:
            Path to model file, or None if not available
        """
        model_name = f"{symbol}_{timeframe}_{model_type}.pth"
        return self.download_model(model_name)
    
    def list_available_models(self) -> list:
        """List all locally cached models"""
        if not self.model_dir.exists():
            return []
        
        models = list(self.model_dir.glob("*.pth"))
        return [m.name for m in models]

# Global instance
_loader = None

def get_model_loader() -> ModelLoader:
    """Get or create the global model loader instance"""
    global _loader
    if _loader is None:
        _loader = ModelLoader()
    return _loader

def ensure_models_ready(symbols: list = None) -> bool:
    """
    Ensure required models are downloaded and ready
    Call this on app startup
    
    Args:
        symbols: List of symbols to download models for
        
    Returns:
        True if models are ready
    """
    loader = get_model_loader()
    
    if not loader.hf_available:
        print("⚠️  ML models not available - using fallback predictions")
        return False
    
    # Check if we already have some models cached
    cached_models = loader.list_available_models()
    if len(cached_models) >= 5:  # At least 5 models cached
        print(f"✓ Found {len(cached_models)} cached models")
        return True
    
    # Download models
    print("Downloading ML models from Hugging Face...")
    return loader.download_all_models(symbols=symbols)

if __name__ == "__main__":
    # Test the loader
    print("Testing ML Model Loader")
    print("=" * 80)
    
    loader = get_model_loader()
    
    if "your-username" in REPO_NAME:
        print("⚠️  Please update REPO_NAME in backend/ml_loader.py")
        print("   Set it to your Hugging Face repository name")
        exit(1)
    
    # Try to download a test model
    test_model = loader.download_model("AAPL_5m_lstm.pth")
    
    if test_model:
        print(f"\n✓ Success! Model downloaded to: {test_model}")
    else:
        print("\n✗ Failed to download model")
        print("   Make sure you've uploaded models to Hugging Face first")

