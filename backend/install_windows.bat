@echo off
echo ===================================================
echo  INSTALLAZIONE POKER BOT (WINDOWS)
echo ===================================================
echo.

echo 1. Creazione Virtual Environment...
python -m venv venv
call venv\Scripts\activate

echo.
echo 2. Aggiornamento PIP...
python -m pip install --upgrade pip

echo.
echo 3. Installazione Librerie Standard...
pip install -r requirements.txt

echo.
echo 4. Installazione Libreria Emergent (Speciale)...
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

echo.
echo 5. Configurazione .env...
if not exist .env (
    copy .env.example .env
    echo.
    echo [ATTENZIONE] Ho creato il file .env!
    echo APRI IL FILE .env E INCOLLA LE TUE CHIAVI API ORA.
) else (
    echo File .env gia esistente.
)

echo.
echo ===================================================
echo  INSTALLAZIONE COMPLETATA!
echo ===================================================
echo.
echo Per avviare il server:
echo    run_server.bat
echo.
echo Per testare la Visione AI:
echo    venv\Scripts\python poker_vision_ai.py
echo.
pause
