@echo off
title Bujji - Health Check & Diagnostics
cd /d "%~dp0"
echo ========================================================
echo       Running Bujji Verification Self-Test...
echo ========================================================
python test_agent.py
echo.
echo ========================================================
echo [DONE] All checks complete! Press any key to exit.
echo ========================================================
pause
