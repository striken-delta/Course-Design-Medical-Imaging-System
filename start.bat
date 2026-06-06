@echo off
title Medical Imaging System
echo.
echo ============================================
echo   Medical Imaging System - One-Click Start
echo ============================================
echo.
echo   First run will auto-install dependencies.
echo   Next run will start instantly.
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"
pause