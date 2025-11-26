@echo off
echo ===================================================
echo  RIPARAZIONE DIPENDENZE POKER BOT
echo ===================================================
echo.
echo 1. Attivo ambiente virtuale...
call venv\Scripts\activate

echo.
echo 2. Installo libreria mancante CRITICA (python-multipart)...
pip install python-multipart

echo.
echo 3. Tento di reinstallare Motor e altre dipendenze...
pip install motor opencv-python mss pygetwindow PyQt5 uvicorn fastapi

echo.
echo ===================================================
echo  RIPARAZIONE COMPLETATA!
echo ===================================================
echo.
echo Se vedi ancora l'avviso su 'motor' (giallo), IGNORALO.
echo L'importante e che non ci siano errori rossi su 'python-multipart'.
echo.
echo Ora riprova ad avviare: run_auto_poker.bat
echo.
pause
