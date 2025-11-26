@echo off
echo ===================================================
echo  RIPARAZIONE DIPENDENZE POKER BOT
echo ===================================================
echo.
echo Sto installando le librerie mancanti (OpenCV, Motor, ecc)...
echo.

call venv\Scripts\activate
pip install opencv-python motor mss pygetwindow PyQt5

echo.
echo ===================================================
echo  RIPARAZIONE COMPLETATA!
echo ===================================================
echo.
echo Ora puoi riprovare ad avviare: run_auto_poker.bat
echo.
pause
