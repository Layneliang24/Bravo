@echo off
echo.
echo === SYSTEM LEVEL COMMAND INTERCEPTED ===
echo ===============================================
echo BLOCKED: Command 'python3' has been system-level intercepted
echo CALL: python3 %*
echo.
echo IMPORTANT:
echo   - This interceptor has physically replaced the original python3
echo   - All python3 calls are redirected to Docker containers
echo   - AI and any scripts CANNOT bypass
echo.
echo RECOMMENDED SOLUTION:
echo   docker-compose exec backend python3 %*
echo   docker-compose exec backend pip install [package]
echo.
echo TO RESTORE ORIGINAL COMMAND:
echo   1. Administrator privileges required
echo   2. Delete this file: S:\python3.cmd
echo   3. Original python.exe is at S:\Python3.10\python.exe
echo ===============================================

REM Log interception
if not exist "C:\SystemGuard_Logs" mkdir "C:\SystemGuard_Logs"
echo %date% %time% SYSTEM_BLOCK python3 %* >> "C:\SystemGuard_Logs\intercept.log"

echo Need to restore original command? Delete S:\python3.cmd
exit /b 1
