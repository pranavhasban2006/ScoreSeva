#!/bin/bash
echo "Starting ScoreSeva..."
echo ""
echo "Starting backend on port 8000..."
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 3
echo ""
echo "Starting frontend on port 5173..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!
echo ""
echo "ScoreSeva running:"
echo "  Frontend → http://localhost:5173"
echo "  Backend  → http://localhost:8000"
echo "  API Docs → http://localhost:8000/docs"
echo "  Demo Guide → http://localhost:8000/meta/demo-guide"
echo ""
echo "Press Ctrl+C to stop both servers."
wait $BACKEND_PID $FRONTEND_PID
