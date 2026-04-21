#!/bin/bash

# start.sh
# Check if python is available
PYTHON="python"
if command -v python3 &>/dev/null; then
    PYTHON="python3"
fi

echo "Installing backend requirements..."
cd backend
$PYTHON -m pip install -r requirements.txt

echo "Starting backend server (port 8000)..."
$PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Installing frontend dependencies..."
cd ../frontend
npm install

echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo "Both servers are running."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both."

trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
