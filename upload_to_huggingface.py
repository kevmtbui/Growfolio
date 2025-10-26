"""
Upload ML models to Hugging Face Hub (free hosting for ML models)

Setup:
1. Create account at https://huggingface.co
2. Install: pip install huggingface_hub
3. Login: huggingface-cli login
4. Update REPO_NAME below with your username
5. Run: python upload_to_huggingface.py
"""

from pathlib import Path
from huggingface_hub import HfApi, create_repo
import os

# Configuration - CHANGE THIS TO YOUR USERNAME
REPO_NAME = "your-username/growfolio-models"  # Example: "john-doe/growfolio-models"
MODEL_DIR = Path("ml_model/models")

def upload_models_to_hf():
    """Upload all .pth models to Hugging Face"""
    api = HfApi()
    
    print(f"Uploading models to: {REPO_NAME}")
    print("=" * 80)
    
    # Create repository (only needed once)
    try:
        create_repo(REPO_NAME, repo_type="model", exist_ok=True, private=False)
        print(f"✓ Repository created/verified: https://huggingface.co/{REPO_NAME}")
    except Exception as e:
        print(f"Note: {e}")
    
    # Get all .pth files
    model_files = list(MODEL_DIR.glob("*.pth"))
    
    if not model_files:
        print(f"\n✗ No .pth files found in {MODEL_DIR}")
        print("Please make sure your models are in the ml_model/models/ directory")
        return
    
    print(f"\nFound {len(model_files)} model files to upload:\n")
    for f in model_files:
        print(f"  - {f.name} ({f.stat().st_size / 1024 / 1024:.2f} MB)")
    
    print("\nStarting upload...")
    print("-" * 80)
    
    # Upload all .pth files
    for i, model_file in enumerate(model_files, 1):
        print(f"\n[{i}/{len(model_files)}] Uploading {model_file.name}...")
        try:
            api.upload_file(
                path_or_fileobj=str(model_file),
                path_in_repo=model_file.name,
                repo_id=REPO_NAME,
                repo_type="model"
            )
            print(f"✓ Uploaded {model_file.name}")
        except Exception as e:
            print(f"✗ Failed to upload {model_file.name}: {e}")
    
    print("\n" + "=" * 80)
    print(f"✓ Upload complete!")
    print(f"\nYour models are now available at:")
    print(f"https://huggingface.co/{REPO_NAME}")
    print(f"\nNext steps:")
    print(f"1. Update backend/ml_loader.py with REPO_NAME = '{REPO_NAME}'")
    print(f"2. Deploy to Railway")
    print(f"3. Models will be automatically downloaded on first run")

if __name__ == "__main__":
    # Check if huggingface_hub is installed
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Please install huggingface_hub first:")
        print("pip install huggingface_hub")
        exit(1)
    
    # Check if user updated REPO_NAME
    if "your-username" in REPO_NAME:
        print("⚠️  Please update REPO_NAME in this script with your Hugging Face username!")
        print("Example: REPO_NAME = 'john-doe/growfolio-models'")
        exit(1)
    
    upload_models_to_hf()

