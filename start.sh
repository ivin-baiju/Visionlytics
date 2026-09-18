#!/bin/bash
echo "Starting Visionlytics Microservices..."

# Start FastAPI Backend in background
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a few seconds for backend to boot
sleep 3

# Start Streamlit Frontend
cd frontend
streamlit run app/main.py --server.port 8501 &
FRONTEND_PID=$!
cd ..

echo "Services are running."
echo "FastAPI Backend: http://localhost:8000"
echo "Streamlit Frontend: http://localhost:8501"

wait $FRONTEND_PID
