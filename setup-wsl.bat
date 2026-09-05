@echo off
echo.
echo ========================================
echo    Enabling WSL and Virtualization
echo ========================================
echo.
echo This will enable Windows features needed for Docker.
echo You may need to restart your PC after this.
echo.

:: Run as admin
net session >nul 2>&1
if errorlevel 1 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [1/3] Enabling Windows Subsystem for Linux...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

echo.
echo [2/3] Enabling Virtual Machine Platform...
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

echo.
echo [3/3] Installing WSL2...
wsl --install --no-distribution

echo.
echo ========================================
echo    Setup complete!
echo    Please RESTART your computer now.
echo    Then run start.bat
echo ========================================
echo.
pause
