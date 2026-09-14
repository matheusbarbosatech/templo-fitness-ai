@echo off
title TEMPLO FITNESS AI - Super-App Cristão de Treino 360
cls
echo ============================================================
echo   TEMPLO FITNESS AI - MORDOMIA DO TEMPLO & FORCA 360
echo ============================================================
echo.
echo [1/2] Verificando dependencias...
python -m pip install -q flet requests

echo.
echo [2/2] Iniciando aplicativo na Area de Trabalho...
cd /d "%~dp0"
python run_local.py
pause
