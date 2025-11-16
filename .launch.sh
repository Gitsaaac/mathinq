#!/bin/bash

echo "🚀 Starting Backend (Python)..."
cd backend
python server.py &
BACKEND_PID=$!

echo "🚀 Starting Frontend (React)..."
cd ../frontend
npm start &
FRONTEND_PID=$!

# Go back to project root
cd ..

echo "🎉 Both servers are now running!"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "Press CTRL+C to stop everything."

# Wait so the script stays alive
wait
