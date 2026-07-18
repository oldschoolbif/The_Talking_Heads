#!/bin/bash
# Start script for The Talking Heads UI

echo "Starting The Talking Heads UI..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start Flask API server in background
echo "Starting Flask API server on port 5001..."
python server.py &
API_PID=$!

# Wait a moment for API to start
sleep 2

# Start React dev server
echo "Starting React dev server on port 3000..."
npm start

# Cleanup on exit
trap "kill $API_PID" EXIT

