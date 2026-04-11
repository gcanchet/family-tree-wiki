@echo off
REM Local Preview Script for Quartz
echo Starting local Quartz preview server...
cd /d "%~dp0"

REM Check if node_modules exists; if not, install them.
if not exist "node_modules" (
    echo node_modules folder not found. Running npm install...
    call npm install
)

echo Attempting to start Quartz on http://localhost:8080...
echo (Press Ctrl+C to stop the server later)
call npx quartz build --serve
pause