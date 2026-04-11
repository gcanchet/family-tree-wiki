@echo off
cd /d "%~dp0"
echo ========================================
echo   Quartz Build and Deploy to GitHub
echo ========================================

:: 1. Pre-flight Build Check
echo [1/3] Running local validation build...
call npm exec quartz build -- --output .temp_build
if %errorlevel% neq 0 (
    echo [ERROR] Local build failed. Fix the errors above before pushing.
    if exist ".temp_build" rd /s /q ".temp_build"
    pause
    exit /b %errorlevel%
)
if exist ".temp_build" rd /s /q ".temp_build"

:: 2. Git Sync
echo [2/3] Staging and committing changes...
git add .

git diff --cached --quiet
if %errorlevel% neq 0 (
    git commit -m "Quartz Sync: %date% %time%"
) else (
    echo [INFO] No changes detected to commit.
)

:: 3. Push to Remote
echo [3/3] Pushing to GitHub...
git push origin HEAD

echo.
echo [SUCCESS] Changes pushed! 
echo Monitor build progress at: https://github.com/gcanchet/family-tree-wiki/actions
pause