@echo off
title NanoERP - Single User Desktop ERP
echo ========================================
echo        NANOERP - Starting...
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from python.org
    echo.
    pause
    exit /b 1
)

:: Check Python version
python -c "import sys; exit(0) if sys.version_info >= (3, 7) else exit(1)"
if errorlevel 1 (
    echo ERROR: Python 3.7 or higher is required.
    echo.
    pause
    exit /b 1
)

:: Create required directories
if not exist data mkdir data
if not exist backups mkdir backups
if not exist config mkdir config

:: Check dependencies
echo Checking dependencies...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Tkinter is not installed.
    echo On Windows, reinstall Python and make sure Tkinter is selected.
    echo.
    pause
    exit /b 1
)

:: Install optional dependencies
echo Installing optional packages (if needed)...
pip install fpdf2 --quiet 2>nul
pip install openpyxl --quiet 2>nul

:: Run the application
echo.
echo Starting NanoERP...
echo ========================================
python run.py

:: Pause if there was an error
if errorlevel 1 (
    echo.
    echo Application closed with error.
    pause
)

exit /b 0