@echo off
title APOLLO FITNESS AI - Servidor Web / PWA
cls
echo ============================================================
echo   APOLLO FITNESS AI - EXECUTANDO NO NAVEGADOR WEB
echo ============================================================
echo.
echo [1/1] Iniciando servidor web na porta 8550...
cd /d "%~dp0"
python run_web.py
pause
