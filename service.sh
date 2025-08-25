#!/bin/bash
PORT=8000
PID=$(lsof -t -i:$PORT)
if [ -n "$PID" ]; then
    kill -9 $PID
    echo "Killed process using port $PORT"
fi
uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1