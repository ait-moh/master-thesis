@echo off
echo Stopping all project services...

echo Stopping Docker containers...
docker-compose -f E:\PFE\24h-1min-dataset\python-files\app\docker-compose.yml down

echo Killing terminals...
taskkill /IM cmd.exe /F
taskkill /IM conda.exe /F
taskkill /IM python.exe /F

echo ✅ All services stopped!
pause
