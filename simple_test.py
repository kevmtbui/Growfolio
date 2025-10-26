#!/usr/bin/env python3
"""
Simple test script for Growfolio backend
Tests basic functionality without complex setup
"""
import requests
import json
import time
import subprocess
import sys
import os

def test_backend():
    """Test the backend API"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Growfolio Backend")
    print("=" * 40)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test 2: Question sections
    try:
        response = requests.get(f"{base_url}/get_question_sections", timeout=5)
        if response.status_code == 200:
            data = response.json()
            sections = data.get("sections", [])
            print(f"✅ Question sections: {len(sections)} sections found")
        else:
            print(f"❌ Question sections: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Question sections failed: {e}")
    
    # Test 3: Create profile
    sample_data = {
        "1": 5000,  # income
        "2": {"Housing": 2000, "Groceries": 500, "Utilities": 200, "Transportation": 300, "Miscellaneous": 300},
        "3": 10000,  # savings
        "4": "None",  # debt
        "5": 0,  # dependents
        "6": 30,  # age
        "7": "Retirement",  # goal
        "8": "15+ years",  # horizon
        "9": 65,  # retirement age
        "10": 20,  # invest percentage
        "11": 3,  # risk preference
        "12": "Do nothing",  # reaction to loss
        "13": "Intermediate",  # experience
        "14": "Weekly",  # check frequency
        "15": "I'm okay with short-term losses if I can earn more long-term.",
        "16": "Balanced Growth"
    }
    
    try:
        response = requests.post(f"{base_url}/create_profile", json=sample_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            profile = data.get("user_profile", {})
            print(f"✅ Profile creation: Success")
            print(f"   Risk tolerance: {profile.get('risk_tolerance', 'N/A')}")
            print(f"   Investment goal: {profile.get('investment_goal', 'N/A')}")
            return True
        else:
            print(f"❌ Profile creation: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Profile creation failed: {e}")
    
    return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    
    try:
        # Change to backend directory and start server
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/", timeout=5)
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

def main():
    """Main test function"""
    print("🧪 Growfolio Simple Test")
    print("=" * 30)
    
    # Check if backend is already running
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("✅ Backend is already running")
            test_backend()
            return
    except:
        pass
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Could not start backend. Please check your setup.")
        print("\n💡 Make sure you have:")
        print("   1. Created backend/.env with GEMINI_API_KEY")
        print("   2. Installed dependencies: pip install -r backend/requirements.txt")
        return
    
    try:
        # Test backend
        success = test_backend()
        
        if success:
            print("\n🎉 Backend test completed successfully!")
            print("\n📱 To test the frontend:")
            print("   1. Open Chrome and go to chrome://extensions/")
            print("   2. Enable Developer mode")
            print("   3. Click 'Load unpacked' and select the 'frontend' folder")
            print("   4. Click the extension icon to test")
        else:
            print("\n❌ Backend test failed. Check the errors above.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    finally:
        if backend_process:
            print("\n🧹 Stopping backend server...")
            backend_process.terminate()
            print("✅ Backend server stopped")

if __name__ == "__main__":
    main()
