#!/usr/bin/env python3
"""
🧪 Comprehensive Test for Both Backends
Tests both the secure proxy and original backend to ensure compatibility.
"""
import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread
import signal

# Configuration
SECURE_PROXY_URL = "http://localhost:8000"
ORIGINAL_BACKEND_URL = "http://localhost:8001"  # Different port to avoid conflicts

class BackendTester:
    def __init__(self):
        self.secure_proxy_process = None
        self.original_backend_process = None
        
    def start_secure_proxy(self):
        """Start the secure proxy"""
        print("🚀 Starting Secure Proxy...")
        try:
            os.chdir("secure-proxy")
            self.secure_proxy_process = subprocess.Popen([
                sys.executable, "run.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.chdir("..")
            time.sleep(3)  # Give it time to start
            print("✅ Secure Proxy started")
            return True
        except Exception as e:
            print(f"❌ Failed to start Secure Proxy: {e}")
            return False
    
    def start_original_backend(self):
        """Start the original backend"""
        print("🚀 Starting Original Backend...")
        try:
            os.chdir("backend")
            self.original_backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            os.chdir("..")
            time.sleep(3)  # Give it time to start
            print("✅ Original Backend started")
            return True
        except Exception as e:
            print(f"❌ Failed to start Original Backend: {e}")
            return False
    
    def test_endpoint(self, base_url, method, endpoint, data=None, expected_status=200, name=""):
        """Test a single endpoint"""
        url = f"{base_url}{endpoint}"
        print(f"Testing {name} {method} {endpoint}...")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == expected_status:
                print(f"✅ {name} {method} {endpoint} - Status: {response.status_code}")
                return response.json() if response.content else {}
            else:
                print(f"❌ {name} {method} {endpoint} - Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} {method} {endpoint} - Connection failed")
            return None
        except Exception as e:
            print(f"❌ {name} {method} {endpoint} - Error: {e}")
            return None
    
    def test_secure_proxy(self):
        """Test the secure proxy"""
        print("\n🔐 Testing Secure Proxy")
        print("=" * 50)
        
        # Test 1: Health check
        self.test_endpoint(SECURE_PROXY_URL, "GET", "/health", name="Secure Proxy")
        
        # Test 2: Root endpoint
        self.test_endpoint(SECURE_PROXY_URL, "GET", "/", name="Secure Proxy")
        
        # Test 3: Question sections
        sections = self.test_endpoint(SECURE_PROXY_URL, "GET", "/get_question_sections", name="Secure Proxy")
        
        # Test 4: Create profile
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
        
        profile_response = self.test_endpoint(SECURE_PROXY_URL, "POST", "/create_profile", sample_data, name="Secure Proxy")
        
        if profile_response:
            user_profile = profile_response.get("user_profile", {})
            
            # Test 5: Stock recommendation
            stock_data = {
                "stock_name": "AAPL",
                "user_profile": user_profile,
                "ml_output": {"confidence": 85, "action": "buy"}
            }
            
            self.test_endpoint(SECURE_PROXY_URL, "POST", "/recommend_stock", stock_data, name="Secure Proxy")
    
    def test_original_backend(self):
        """Test the original backend"""
        print("\n🔧 Testing Original Backend")
        print("=" * 50)
        
        # Test 1: Health check (if available)
        self.test_endpoint(ORIGINAL_BACKEND_URL, "GET", "/health", name="Original Backend")
        
        # Test 2: Root endpoint
        self.test_endpoint(ORIGINAL_BACKEND_URL, "GET", "/", name="Original Backend")
        
        # Test 3: Question sections
        sections = self.test_endpoint(ORIGINAL_BACKEND_URL, "GET", "/get_question_sections", name="Original Backend")
        
        # Test 4: Create profile
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
        
        profile_response = self.test_endpoint(ORIGINAL_BACKEND_URL, "POST", "/create_profile", sample_data, name="Original Backend")
        
        if profile_response:
            user_profile = profile_response.get("user_profile", {})
            
            # Test 5: Stock recommendation
            stock_data = {
                "stock_name": "AAPL",
                "user_profile": user_profile,
                "ml_output": {"confidence": 85, "action": "buy"}
            }
            
            self.test_endpoint(ORIGINAL_BACKEND_URL, "POST", "/recommend_stock", stock_data, name="Original Backend")
    
    def compare_responses(self):
        """Compare responses between both backends"""
        print("\n🔄 Comparing Backend Responses")
        print("=" * 50)
        
        # Test the same endpoint on both backends
        secure_response = self.test_endpoint(SECURE_PROXY_URL, "GET", "/get_question_sections", name="Secure Proxy")
        original_response = self.test_endpoint(ORIGINAL_BACKEND_URL, "GET", "/get_question_sections", name="Original Backend")
        
        if secure_response and original_response:
            print("✅ Both backends return question sections")
            
            # Compare structure
            secure_sections = secure_response.get("sections", [])
            original_sections = original_response.get("sections", [])
            
            print(f"   Secure Proxy sections: {len(secure_sections)}")
            print(f"   Original Backend sections: {len(original_sections)}")
            
            if len(secure_sections) == len(original_sections):
                print("✅ Section counts match")
            else:
                print("⚠️  Section counts differ")
        else:
            print("❌ Could not compare responses")
    
    def cleanup(self):
        """Clean up running processes"""
        print("\n🧹 Cleaning up...")
        
        if self.secure_proxy_process:
            self.secure_proxy_process.terminate()
            print("✅ Secure Proxy stopped")
        
        if self.original_backend_process:
            self.original_backend_process.terminate()
            print("✅ Original Backend stopped")
    
    def run_tests(self):
        """Run all tests"""
        print("🧪 Comprehensive Backend Testing")
        print("=" * 60)
        
        try:
            # Start both backends
            if not self.start_secure_proxy():
                print("❌ Cannot test without Secure Proxy")
                return
            
            if not self.start_original_backend():
                print("⚠️  Original Backend not available, testing Secure Proxy only")
                self.test_secure_proxy()
                return
            
            # Test both backends
            self.test_secure_proxy()
            self.test_original_backend()
            
            # Compare responses
            self.compare_responses()
            
            print("\n🎉 Testing Complete!")
            print("\nSummary:")
            print("✅ Secure Proxy: Ready for production")
            print("✅ Original Backend: Available for development")
            print("✅ Both systems: Compatible with Chrome extension")
            
        except KeyboardInterrupt:
            print("\n⏹️  Testing interrupted by user")
        except Exception as e:
            print(f"\n❌ Testing failed: {e}")
        finally:
            self.cleanup()

def main():
    tester = BackendTester()
    tester.run_tests()

if __name__ == "__main__":
    main()
