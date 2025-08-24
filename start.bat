@echo off
echo Starting AcademicPlot Pro Web UI...
echo.

REM Check if requirements are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Error: Required packages not installed
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Start the web application
echo Starting Flask server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python main.py

pause