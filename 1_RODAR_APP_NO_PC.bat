@echo off
title APOLLO FITNESS AI - Super-App de Saúde 360
cls
echo ============================================================
echo   APOLLO FITNESS AI - SUPER-APP DE SAUDE & MUSCULACAO 360
echo ============================================================
echo.
echo [1/2] Verificando dependencias...
python -m pip install -q flet requests

echo.
echo [2/2] Iniciando aplicativo na Area de Trabalho...
cd /d "%~dp0"
python run_local.py
pause
