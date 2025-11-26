@echo off
echo ===================================================
echo  AVVIO AUTOMATICO POKER BOT
echo ===================================================
echo.
echo 1. Avvio Server Backend (in una nuova finestra)...
start "Poker Server" cmd /k "venv\Scripts\activate && uvicorn server:app --host 0.0.0.0 --port 8001"

echo.
echo Attendo 5 secondi che il server parta...
timeout /t 5

echo.
echo 2. Avvio Client Cattura Schermo...
echo (Tieni questa finestra aperta per vedere l'analisi)
echo.
call venv\Scripts\activate
python screenshot_client.py
pause
