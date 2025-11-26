@echo off
echo Avvio Poker Bot Server...
call venv\Scripts\activate
uvicorn server:app --reload --host 0.0.0.0 --port 8001
pause
