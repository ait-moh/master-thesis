@echo off
echo 🚀 Starting entire application...

:: Start Docker Kafka
start "Docker Kafka" run_docker_kafka.bat

:: Wait for Docker Kafka to initialize
timeout /t 15 /nobreak

:: Start Backend (Anaconda terminal)
start "FastAPI Backend" run_backend.bat

:: Start Frontend (React)
start "Frontend" run_frontend.bat

:: Wait a bit to let backend and frontend fully boot
timeout /t 5 /nobreak

:: Start Producer (Anaconda terminal)
start "Kafka Producer" run_producer.bat

echo ✅ All services started!
pause
