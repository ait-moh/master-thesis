@echo off
:: Initialize conda
CALL E:\apps\miniconda3\Scripts\activate.bat

:: Activate your environment
CALL conda activate tf

:: Move to backend directory
cd /d E:\PFE\24h-1min-dataset\python-files\app\backend

:: Run Kafka producer
python producer.py

pause
