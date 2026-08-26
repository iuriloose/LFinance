@echo off
setlocal
cd /d %~dp0

echo ========================================
echo LFinance - Gerador de EXE
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 1
)

echo Limpando build anterior...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Gerando executavel...
python -m PyInstaller --clean --noconfirm LFinance.spec

if errorlevel 1 (
    echo.
    echo ERRO: falha ao gerar o executavel.
    pause
    exit /b 1
)

echo.
echo ========================================
echo EXE criado com sucesso:
echo dist\LFinance\LFinance.exe
echo ========================================
pause