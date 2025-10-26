# Quick Start: Deploy to Railway with ML Models

## TL;DR - 5 Steps to Deploy

### 1. Upload Models to Hugging Face (One-time setup)

```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Edit upload_to_huggingface.py - change this line:
# REPO_NAME = "your-username/growfolio-models"

# Upload models (takes 10-30 min)
python upload_to_huggingface.py
```

### 2. Update Backend Config

Edit `backend/ml_loader.py` - change this line:
```python
REPO_NAME = "your-username/growfolio-models"  # Use YOUR Hugging Face username
```

### 3. Push to GitHub

```bash
git add .
git commit -m "Setup Railway deployment"
git push origin railway-deployment
```

### 4. Deploy on Railway

1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select your repo and `railway-deployment` branch
4. Add environment variables:
   - `GEMINI_API_KEY=your_key`
   - `FINNHUB_API_KEY=your_key`
5. Deploy!

### 5. Update Frontend

In `frontend/popup.js` and `frontend/dashboard.js`:
```javascript
const API_BASE = "https://your-app.railway.app";  // Your Railway URL
```

In `frontend/manifest.json`:
```json
"host_permissions": [
  "https://your-app.railway.app/*"
]
```

## Done! 🎉

Your backend will:
- ✅ Auto-download ML models from Hugging Face on first start
- ✅ Cache models for faster subsequent starts
- ✅ Serve real ML predictions to your Chrome extension

## Need Help?

See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for detailed instructions and troubleshooting.

