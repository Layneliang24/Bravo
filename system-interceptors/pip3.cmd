@echo off
echo.
echo === SYSTEM LEVEL COMMAND INTERCEPTED ===
echo ===============================================
echo BLOCKED: Command 'pip3' has been system-level intercepted
echo CALL: pip3 %*
echo.
echo IMPORTANT:
echo   - This interceptor has physically replaced the original pip3
echo   - All pip3 calls are redirected to Docker containers
echo   - AI and any scripts CANNOT bypass
echo.
echo RECOMMENDED SOLUTION:
echo   docker-compose exec backend pip3 %*
echo   docker-compose exec backend pip install [package]
echo.
echo TO RESTORE ORIGINAL COMMAND:
echo   1. Administrator privileges required
echo   2. Delete this file: S:\pip3.cmd
echo   3. Original pip3.exe is at S:\Python3.10\Scripts\pip3.exe
echo ===============================================

REM Log interception
if not exist "C:\SystemGuard_Logs" mkdir "C:\SystemGuard_Logs"
echo %date% %time% SYSTEM_BLOCK pip3 %* >> "C:\SystemGuard_Logs\intercept.log"

echo Need to restore original command? Delete S:\pip3.cmd
exit /b 1
