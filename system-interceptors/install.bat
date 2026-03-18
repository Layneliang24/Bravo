@echo off
echo ===============================================
echo   Python System-Level Interceptor Installer
echo ===============================================
echo.
echo This script will install Python interceptors to S:\ root directory
echo This requires Administrator privileges!
echo.
pause

echo.
echo Copying interceptor files...

copy /Y "%~dp0python.cmd" "S:\python.cmd"
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy python.cmd
    echo Please run this script as Administrator!
    pause
    exit /b 1
)

copy /Y "%~dp0python3.cmd" "S:\python3.cmd"
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy python3.cmd
    pause
    exit /b 1
)

copy /Y "%~dp0pip.cmd" "S:\pip.cmd"
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy pip.cmd
    pause
    exit /b 1
)

copy /Y "%~dp0pip3.cmd" "S:\pip3.cmd"
if %errorlevel% neq 0 (
    echo ERROR: Failed to copy pip3.cmd
    pause
    exit /b 1
)

echo.
echo ===============================================
echo   Installation Complete!
echo ===============================================
echo.
echo Intercepted commands:
echo   - python  -^> Docker container
echo   - python3 -^> Docker container
echo   - pip     -^> Docker container
echo   - pip3    -^> Docker container
echo.
echo To restore original commands:
echo   Delete S:\python.cmd, S:\python3.cmd, S:\pip.cmd, S:\pip3.cmd
echo.
pause
