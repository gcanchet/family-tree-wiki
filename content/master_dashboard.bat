@echo off
title Family Tree Wiki Dashboard
:menu
cls
echo ======================================================
echo           FAMILY TREE WIKI - MASTER DASHBOARD
echo ======================================================
echo [1] Update Data: Run family_processor.py
echo     (Standardizes markdown and updates JSON)
echo.
echo [2] Preview: Run preview_local.bat
echo     (Syncs content and starts local Quartz server)
echo.
echo [3] Publish: Run deploy_to_quartz.bat
echo     (Syncs content and pushes to GitHub Pages)
echo.
echo [4] Backups: Run backup_manager.bat
echo     (Create, list, and prune vault backups)
echo.
echo [5] Exit
echo ======================================================
set /p choice="Action (1-5): "

if "%choice%"=="1" (
    python "c:\Users\Great\AI\obsidian\my vault\family_processor.py"
    pause
    goto menu
)
if "%choice%"=="2" (
    start "Quartz Preview" cmd /k "c:\Users\Great\AI\obsidian\my vault\preview_local.bat"
    goto menu
)
if "%choice%"=="3" (
    start "Quartz Deploy" cmd /k "c:\Users\Great\AI\obsidian\my vault\deploy_to_quartz.bat"
    goto menu
)
if "%choice%"=="4" (
    call "c:\Users\Great\AI\obsidian\my vault\backup_manager.bat"
    goto menu
)
if "%choice%"=="5" exit
goto menu