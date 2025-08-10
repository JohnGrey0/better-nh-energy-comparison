@echo off
echo ⚡ NH Energy Rates - Monthly Update
echo ================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the Python update script
python auto_update_github.py

REM Pause to see results
echo.
echo Press any key to close...
pause >nul
