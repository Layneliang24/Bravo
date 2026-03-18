@echo off
echo.
echo === SYSTEM LEVEL COMMAND INTERCEPTED ===
echo ===============================================
echo BLOCKED: Command 'python' has been system-level intercepted
echo CALL: python %*
echo.
echo IMPORTANT:
echo   - This interceptor has physically replaced the original python
echo   - All python calls are redirected to Docker containers
echo   - AI and any scripts CANNOT bypass
echo.
echo RECOMMENDED SOLUTION:
echo   docker-compose exec backend python %*
echo   docker-compose exec backend pip install [package]
echo.
echo TO RESTORE ORIGINAL COMMAND:
echo   1. Administrator privileges required
echo   2. Delete this file: S:\python.cmd
echo   3. Original python.exe is at S:\Python3.10\python.exe
echo ===============================================

REM Log interception
if not exist "C:\SystemGuard_Logs" mkdir "C:\SystemGuard_Logs"
echo %date% %time% SYSTEM_BLOCK python %* >> "C:\SystemGuard_Logs\intercept.log"

echo Need to restore original command? Delete S:\python.cmd
exit /b 1
