@echo off
echo ==========================================
echo       Setting up Mazeo AI Environment
echo ==========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Mazeo AI...
echo Open your browser to: http://127.0.0.1:5000
echo.
python mazeo.py
pause
