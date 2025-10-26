#!/usr/bin/env python3
"""
Setup and test script for Growfolio project
This script helps you test the complete workflow from extension to backend
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def check_backend_dependencies():
    """Check if backend dependencies are installed"""
    print("🔍 Checking backend dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import google.generativeai
        print("✅ All backend dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r backend/requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists with required API keys"""
    print("🔍 Checking environment configuration...")
    
    env_path = Path("backend/.env")
    if not env_path.exists():
        print("❌ .env file not found in backend directory")
        print("💡 Create backend/.env with:")
        print("   GEMINI_API_KEY=your_gemini_api_key_here")
        print("   FINNHUB_API_KEY=your_finnhub_api_key_here (optional for development)")
        return False
    
    # Check if API keys are set
    with open(env_path, 'r') as f:
        content = f.read()
        if "GEMINI_API_KEY=" not in content or "your_gemini_api_key_here" in content:
            print("❌ GEMINI_API_KEY not properly set in .env file")
            print("💡 Update backend/.env with your actual Gemini API key")
            return False
        
        if "FINNHUB_API_KEY=" not in content or "your_finnhub_api_key_here" in content:
            print("⚠️  FINNHUB_API_KEY not set - will use mock data for development")
        else:
            print("✅ Both API keys are configured")
    
    print("✅ Environment configuration looks good")
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    
    try:
        # Change to backend directory and start server
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/get_question_sections", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server is running on http://localhost:8000")
                return process
            else:
                print(f"❌ Backend server responded with status {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend server not responding: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None

def test_backend_endpoints():
    """Test the backend endpoints"""
    print("🧪 Testing backend endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Get question sections
    try:
        response = requests.get(f"{base_url}/get_question_sections")
        if response.status_code == 200:
            print("✅ GET /get_question_sections - OK")
        else:
            print(f"❌ GET /get_question_sections - Status {response.status_code}")
    except Exception as e:
        print(f"❌ GET /get_question_sections - Error: {e}")
    
    # Test 2: Create basic profile (with sample data)
    sample_data = {
        "1": 5000,  # income
        "2": {"Housing": 1500, "Groceries": 400, "Utilities": 200, "Transportation": 300, "Miscellaneous": 200},
        "3": 10000,  # savings
        "4": "None",
        "5": 0,  # dependents
        "6": 30,  # age
        "7": "Retirement",  # primary goal
        "8": "15+ years",  # horizon
        "9": 65,  # retirement age
        "10": 20,  # invest percentage
        "11": 3,  # risk scale
        "12": "Do nothing",  # drawdown response
        "13": "Intermediate",  # experience
        "14": "Weekly",  # news frequency
        "15": "I'm okay with short-term losses if I can earn more long-term.",
        "16": "Balanced Growth"
    }
    
    try:
        response = requests.post(f"{base_url}/create_profile", json=sample_data)
        if response.status_code == 200:
            print("✅ POST /create_profile - OK")
        else:
            print(f"❌ POST /create_profile - Status {response.status_code}")
    except Exception as e:
        print(f"❌ POST /create_profile - Error: {e}")
    
    # Test 3: Create advanced profile
    try:
        response = requests.post(f"{base_url}/create_advanced_profile", json=sample_data)
        if response.status_code == 200:
            print("✅ POST /create_advanced_profile - OK")
            profile = response.json().get("user_profile", {})
            
            # Test 4: Analyze trader type
            trader_data = {
                "user_profile": profile,
                "trader_type": "retirement_investor"
            }
            
            response = requests.post(f"{base_url}/analyze_trader_type", json=trader_data)
            if response.status_code == 200:
                print("✅ POST /analyze_trader_type - OK")
            else:
                print(f"❌ POST /analyze_trader_type - Status {response.status_code}")
                
        else:
            print(f"❌ POST /create_advanced_profile - Status {response.status_code}")
            if response.json().get("error"):
                print(f"   Error: {response.json()['error']}")
    except Exception as e:
        print(f"❌ POST /create_advanced_profile - Error: {e}")

def print_extension_instructions():
    """Print instructions for testing the Chrome extension"""
    print("\n" + "="*60)
    print("📱 CHROME EXTENSION TESTING INSTRUCTIONS")
    print("="*60)
    print("""
1. Open Chrome and go to chrome://extensions/
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked" and select the 'frontend' folder
4. The GrowFolio extension should appear in your extensions
5. Click the extension icon to open the popup
6. Complete the 3-step onboarding questionnaire
7. Click "Continue to Dashboard" to see your analysis
8. Use the "Refresh" button to get new insights

🔧 If you see CORS errors:
   - Make sure the backend is running on http://localhost:8000
   - Check that the extension has the correct host permissions in manifest.json

📊 Expected Workflow:
   - Step 1: Financial Snapshot (income, expenses, savings, etc.)
   - Step 2: Investment Goals (trader type, horizon, risk tolerance)
   - Step 3: Personal Profile (experience, behavior)
   - Dashboard: Shows different content based on trader type
     * Day Trader: ML predictions with buy/sell/hold signals
     * Retirement Investor: Portfolio allocation recommendations
""")

def main():
    """Main setup and test function"""
    print("🚀 GrowFolio Setup & Test Script")
    print("="*40)
    
    # Check dependencies
    if not check_backend_dependencies():
        return
    
    # Check environment
    if not check_env_file():
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        return
    
    try:
        # Test endpoints
        test_backend_endpoints()
        
        # Print extension instructions
        print_extension_instructions()
        
        print("\n✅ Setup complete! Backend is running.")
        print("💡 Press Ctrl+C to stop the backend server when done testing.")
        
        # Keep the script running
        backend_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping backend server...")
        backend_process.terminate()
        print("✅ Backend server stopped.")

if __name__ == "__main__":
    main()
