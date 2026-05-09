#!/bin/bash
# Start both backend and frontend

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

echo "Starting FastAPI backend..."
cd "$SCRIPT_DIR/backend"
"$VENV_PYTHON" -m pip install -r requirements.txt -q
"$VENV_PYTHON" main.py &
BACKEND_PID=$!

echo "Starting Vue frontend..."
cd "$SCRIPT_DIR/frontend"
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
