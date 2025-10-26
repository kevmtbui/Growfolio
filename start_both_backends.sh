#!/bin/bash
# 🚀 Start Both Backends Script
# Starts both the secure proxy and original backend for testing

echo "🚀 Starting Both Backends for Testing"
echo "====================================="

# Function to start secure proxy
start_secure_proxy() {
    echo "🔐 Starting Secure Proxy on port 8000..."
    cd secure-proxy
    python run.py &
    SECURE_PID=$!
    echo "✅ Secure Proxy started (PID: $SECURE_PID)"
    cd ..
}

# Function to start original backend
start_original_backend() {
    echo "🔧 Starting Original Backend on port 8001..."
    cd backend
    python -m uvicorn app:app --host 0.0.0.0 --port 8001 &
    ORIGINAL_PID=$!
    echo "✅ Original Backend started (PID: $ORIGINAL_PID)"
    cd ..
}

# Function to cleanup processes
cleanup() {
    echo "🧹 Cleaning up processes..."
    if [ ! -z "$SECURE_PID" ]; then
        kill $SECURE_PID 2>/dev/null
        echo "✅ Secure Proxy stopped"
    fi
    if [ ! -z "$ORIGINAL_PID" ]; then
        kill $ORIGINAL_PID 2>/dev/null
        echo "✅ Original Backend stopped"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start both backends
start_secure_proxy
sleep 2
start_original_backend
sleep 2

echo ""
echo "🎉 Both backends are running!"
echo "Secure Proxy: http://localhost:8000"
echo "Original Backend: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop both backends"
echo ""

# Wait for user to stop
wait
