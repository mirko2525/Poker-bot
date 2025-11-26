@echo off
echo ===================================================
echo  RIPARAZIONE TOTALE DIPENDENZE
echo ===================================================
echo.
echo 1. Attivo ambiente virtuale...
call venv\Scripts\activate

echo.
echo 2. Installo TUTTE le librerie necessarie...
echo.
pip install groq emergentintegrations python-multipart opencv-python motor mss pygetwindow PyQt5 uvicorn fastapi requests python-dotenv --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

echo.
echo ===================================================
echo  RIPARAZIONE COMPLETATA!
echo ===================================================
echo.
echo Ora riprova ad avviare: run_auto_poker.bat
echo.
pause
