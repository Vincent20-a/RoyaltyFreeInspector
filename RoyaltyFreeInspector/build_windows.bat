@echo off
REM Crea RoyaltyFreeInspector.exe (Windows 10/11, 64 bit)
REM Requisiti: Python 3.10-3.13 a 64 bit da python.org (spuntare "Add python.exe to PATH")
setlocal
cd /d "%~dp0"

if not exist .venv (
    python -m venv .venv || goto :err
)
call .venv\Scripts\activate.bat || goto :err

python -m pip install --upgrade pip || goto :err
pip install -r requirements.txt pyinstaller || goto :err

pyinstaller --noconfirm --clean --onefile --windowed ^
    --name RoyaltyFreeInspector ^
    --icon assets\icon.ico ^
    --add-data "assets\icon.ico;assets" ^
    --collect-submodules rfi ^
    main.py || goto :err

echo.
echo Fatto! L'eseguibile si trova in: dist\RoyaltyFreeInspector.exe
if /i not "%~1"=="nopause" pause
exit /b 0

:err
echo.
echo ERRORE durante la creazione dell'eseguibile.
if /i not "%~1"=="nopause" pause
exit /b 1
