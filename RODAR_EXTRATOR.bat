@echo off
title RPA Google Maps - Executor
cls

echo ======================================================
echo           INICIANDO AUTOMACAO GOOGLE MAPS
echo ======================================================
echo.
echo Diretorio: %~dp0
echo.

:: Navega ate a pasta do script
cd /d "%~dp0"

:: Executa o Python (ajuste o caminho se nao estiver no PATH)
python main.py

echo.
echo ======================================================
echo           PROCESSO FINALIZADO!
echo ======================================================
echo.
pause