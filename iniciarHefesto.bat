@echo off
chcp 65001 > nul
title Executando Hefesto Script

echo =========================================
echo       Iniciando Script Hefesto
echo =========================================

:: 1. Verifica se o ambiente virtual (.venv) existe
if not exist ".venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual (.venv) nao encontrado!
    echo Certifique-se de criar o .venv na pasta do projeto.
    pause
    exit /b 1
)

:: 2. Ativa o ambiente virtual
call .venv\Scripts\activate.bat

:: 3. Verifica se o arquivo Python existe
if not exist "Hefesto.py" (
    echo [ERRO] O arquivo Hefesto.py nao foi encontrado nesta pasta.
    pause
    exit /b 1
)

:: 4. Executa o script Python
echo [INFO] Executando Hefesto.py...
python Hefesto.py

:: 5. Finalização e Desativação
if %ERRORLEVEL% EQU 0 (
    echo =========================================
    echo [SUCESSO] Script executado com sucesso!
    echo =========================================
) else (
    echo =========================================
    echo [ERRO] Ocorreu uma falha durante a execucao.
    echo =========================================
)

call deactivate 2>nul
pause