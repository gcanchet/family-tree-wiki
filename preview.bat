@echo off
cd /d "%~dp0"
echo ========================================
echo   Quartz Local Preview Server
echo ========================================

if not exist "node_modules" (
    echo [INFO] node_modules not found. Installing dependencies...
    call npm install
)

echo [INFO] Starting server at http://localhost:8080
echo [HINT] Press Ctrl+C to stop the server.
call npm exec quartz build -- --serve
pause