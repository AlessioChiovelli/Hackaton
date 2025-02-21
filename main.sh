#!/bin/bash

# Funzione per terminare entrambi i processi
cleanup() {
    echo "Stopping frontend and backend..."
    kill $frontend_pid
    kill $backend_pid
    exit 0
}

# Imposta il trap per il segnale SIGINT (Ctrl+C)
trap cleanup SIGINT

# Avvia il frontend
streamlit run streamlit_app.py &
frontend_pid=$!

# Avvia il backend
uvicorn app:app --host=127.0.0.1 --port 5000 &
backend_pid=$!

# Attende che entrambi i processi terminino
wait $frontend_pid
wait $backend_pid