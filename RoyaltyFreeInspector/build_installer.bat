@echo off
REM Crea l'EXE (PyInstaller) e poi l'installer (Inno Setup 6).
REM Requisiti: Python 3.10-3.13 x64 + Inno Setup 6 (https://jrsoftware.org/isdl.php)
setlocal
cd /d "%~dp0"

call build_windows.bat nopause
if not exist dist\RoyaltyFreeInspector.exe goto :err

set "ISCC="
for %%P in ("%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%ProgramFiles%\Inno Setup 6\ISCC.exe" "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe") do (
    if exist %%P set "ISCC=%%~P"
)
if not defined ISCC (
    echo Inno Setup 6 non trovato. Installalo da https://jrsoftware.org/isdl.php e rilancia.
    goto :err
)

"%ISCC%" installer.iss || goto :err

echo.
echo Fatto! Installer in: installer_output\RoyaltyFreeInspector_Setup_1.0.0.exe
pause
exit /b 0

:err
echo.
echo ERRORE durante la creazione dell'installer.
pause
exit /b 1
