@echo off
title Bujji AI - Dependency Installer
cd /d "%~dp0"
echo ========================================================
echo       Installing Bujji Assistant Dependencies...
echo ========================================================
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo ========================================================
echo [DONE] Dependencies installed successfully!
echo ========================================================
pause
