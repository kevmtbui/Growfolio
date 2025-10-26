# Railway Deployment Guide with Hugging Face ML Models

This guide will help you deploy the Growfolio backend to Railway with ML models hosted on Hugging Face.

## Prerequisites

1. **Hugging Face Account**: Create a free account at https://huggingface.co
2. **Railway Account**: Create a free account at https://railway.app
3. **Git**: Make sure git is installed and configured

## Step 1: Upload ML Models to Hugging Face

### 1.1 Install Hugging Face CLI

```bash
pip install huggingface_hub
```

### 1.2 Login to Hugging Face

```bash
huggingface-cli login
```

This will open a browser window. Copy your access token from https://huggingface.co/settings/tokens

### 1.3 Update the Upload Script

Edit `upload_to_huggingface.py` and change:

```python
REPO_NAME = "your-username/growfolio-models"
```

Replace `your-username` with your actual Hugging Face username. For example:
```python
REPO_NAME = "john-doe/growfolio-models"
```

### 1.4 Run the Upload Script

```bash
python upload_to_huggingface.py
```

This will:
- Create a new repository on Hugging Face
- Upload all your `.pth` model files
- Display the repository URL

**Note**: This may take 10-30 minutes depending on your internet speed and number of models.

### 1.5 Verify Upload

Visit your repository at: `https://huggingface.co/your-username/growfolio-models`

You should see all your `.pth` files listed.

## Step 2: Update Backend Configuration

### 2.1 Update ML Loader

Edit `backend/ml_loader.py` and change:

```python
REPO_NAME = "your-username/growfolio-models"
```

Use the same repository name from Step 1.3.

### 2.2 Test Locally (Optional)

```bash
cd backend
python ml_loader.py
```

This should download a test model from Hugging Face.

## Step 3: Commit Changes to Git

```bash
# Make sure you're on the railway-deployment branch
git status

# Add all files
git add .

# Commit
git commit -m "Setup Railway deployment with Hugging Face ML models"

# Push to GitHub
git push origin railway-deployment
```

## Step 4: Deploy to Railway

### 4.1 Create New Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your Growfolio repository
5. Select the `railway-deployment` branch

### 4.2 Configure Environment Variables

In Railway dashboard, go to your project → Variables → Add these:

```
GEMINI_API_KEY=your_gemini_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here
PORT=8000
```

Get your API keys from:
- Gemini: https://makersuite.google.com/app/apikey
- Finnhub: https://finnhub.io/dashboard

### 4.3 Configure Build Settings

Railway should auto-detect the `Procfile`. If not, set:

**Build Command:**
```bash
cd backend && pip install -r requirements.txt
```

**Start Command:**
```bash
cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT
```

### 4.4 Deploy

Click "Deploy" and wait for the build to complete.

## Step 5: What Happens on First Deploy

When Railway starts your backend:

1. ✓ Installs Python dependencies (including `huggingface_hub`, `torch`, etc.)
2. ✓ Starts the FastAPI server
3. ✓ On startup, automatically downloads ML models from Hugging Face
4. ✓ Caches models for faster subsequent starts
5. ✓ Backend is ready to serve predictions!

**First deployment may take 5-10 minutes** as it downloads models. Subsequent deploys will be faster due to caching.

## Step 6: Update Frontend

Once deployed, Railway will give you a URL like: `https://your-app.railway.app`

Update your Chrome extension to use this URL:

### 6.1 Update `frontend/popup.js`

```javascript
const API_BASE = "https://your-app.railway.app";  // Replace with your Railway URL
```

### 6.2 Update `frontend/dashboard.js`

```javascript
const API_BASE = "https://your-app.railway.app";  // Replace with your Railway URL
```

### 6.3 Update `frontend/manifest.json`

Add your Railway domain to `host_permissions`:

```json
"host_permissions": [
  "https://your-app.railway.app/*",
  "https://finnhub.io/*"
]
```

## Step 7: Test the Deployment

1. Load your updated Chrome extension
2. Fill out the investment questionnaire
3. Check Railway logs to see ML models being loaded
4. Verify predictions are working

## Monitoring

### View Logs

In Railway dashboard:
- Click on your project
- Go to "Deployments" tab
- Click on the latest deployment
- View logs to see:
  - ML models being downloaded
  - Prediction requests
  - Any errors

### Check Model Status

Look for these log messages:
```
Starting Growfolio Backend
Initializing ML models...
Downloading models from: your-username/growfolio-models
✓ Downloaded AAPL_5m_lstm.pth
✓ Downloaded MSFT_5m_lstm.pth
...
✓ ML models ready
✓ Backend ready!
```

## Troubleshooting

### Models Not Downloading

**Problem**: Logs show "Failed to download model"

**Solutions**:
1. Check `REPO_NAME` in `backend/ml_loader.py` matches your Hugging Face repo
2. Make sure your Hugging Face repository is public
3. Verify models were uploaded successfully

### Out of Memory

**Problem**: Railway crashes with "Out of memory"

**Solutions**:
1. Upgrade Railway plan for more RAM
2. Reduce number of models loaded at startup
3. Use smaller model architectures

### Slow First Start

**Problem**: First deployment takes 10+ minutes

**Solution**: This is normal! Models are being downloaded. Subsequent starts will be much faster.

### Import Errors

**Problem**: "ModuleNotFoundError: No module named 'torch'"

**Solution**: Make sure `backend/requirements.txt` includes all dependencies:
```
torch
numpy
pandas
scikit-learn
huggingface_hub
```

## Cost Estimate

- **Hugging Face**: FREE (unlimited public model hosting)
- **Railway**: FREE tier includes:
  - $5 credit per month
  - Enough for ~100 hours of runtime
  - Perfect for development/testing

For production, consider Railway's paid plans starting at $5/month.

## Next Steps

1. ✅ Models uploaded to Hugging Face
2. ✅ Backend deployed to Railway
3. ✅ Frontend updated with Railway URL
4. ✅ Extension working with live ML predictions

You're done! 🎉

## Support

If you encounter issues:
1. Check Railway logs for error messages
2. Verify Hugging Face repository is accessible
3. Test `backend/ml_loader.py` locally first
4. Check environment variables are set correctly

---

**Pro Tip**: Keep the `railway-deployment` branch separate from `main`. This way you can:
- Test deployments without affecting local development
- Merge changes when ready
- Roll back easily if needed

