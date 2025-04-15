@echo off
:: Move to your docker-compose directory
cd /d E:\PFE\24h-1min-dataset\python-files\app

:: Start Kafka
docker-compose up -d

pause
