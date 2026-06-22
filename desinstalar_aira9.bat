@echo off
title Desinstalador AIra9Touch v3.0 ULTRA
color 0B
echo.
echo  ==========================================
echo     DESINSTALADOR DO AIRA9TOUCH v3.0
echo  ==========================================
echo.

echo  [1/5] Encerrando processos...
taskkill /f /im aira9touch.exe      >nul 2>&1
taskkill /f /im aira9touch_v2.exe   >nul 2>&1
taskkill /f /im aira9touch_v3.exe   >nul 2>&1
taskkill /f /im pythonw.exe         >nul 2>&1
taskkill /f /im python.exe          >nul 2>&1
echo  OK.

echo  [2/5] Removendo do Inicio Automatico...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "AIra9Touch" /f >nul 2>&1
echo  OK.

echo  [3/5] Removendo arquivos de configuracao...
if exist "config.json"    del /f /q "config.json"
if exist "config_v3.json" del /f /q "config_v3.json"
if exist "macros.json"    del /f /q "macros.json"
echo  OK.

echo  [4/5] Removendo atalho da Area de Trabalho (se existir)...
set DESK=%USERPROFILE%\Desktop
if exist "%DESK%\AIra9Touch.lnk" del /f /q "%DESK%\AIra9Touch.lnk"
echo  OK.

echo  [5/5] Limpeza concluida!
echo.
echo  ==========================================
echo   Sistema limpo. Pode deletar a pasta.
echo  ==========================================
echo.
pause
