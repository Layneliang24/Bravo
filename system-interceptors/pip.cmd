@echo off
echo.
echo === SYSTEM LEVEL COMMAND INTERCEPTED ===
echo ===============================================
echo BLOCKED: Command 'pip' has been system-level intercepted
echo CALL: pip %*
echo.
echo IMPORTANT:
echo   - This interceptor has physically replaced the original pip
echo   - All pip calls are redirected to Docker containers
echo   - AI and any scripts CANNOT bypass
echo.
echo RECOMMENDED SOLUTION:
echo   docker-compose exec backend pip %*
echo   docker-compose exec backend pip install [package]
echo.
echo TO RESTORE ORIGINAL COMMAND:
echo   1. Administrator privileges required
echo   2. Delete this file: S:\pip.cmd
echo   3. Original pip.exe is at S:\Python3.10\Scripts\pip.exe
echo ===============================================

REM Log interception
if not exist "C:\SystemGuard_Logs" mkdir "C:\SystemGuard_Logs"
echo %date% %time% SYSTEM_BLOCK pip %* >> "C:\SystemGuard_Logs\intercept.log"

echo Need to restore original command? Delete S:\pip.cmd
exit /b 1
