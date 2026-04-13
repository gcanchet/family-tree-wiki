@echo off
setlocal enabledelayedexpansion

set "SOURCE=c:\Users\Great\AI\obsidian\my vault"
set "BACKUP_ROOT=c:\Users\Great\AI\obsidian\backups"

:menu
cls
echo ======================================================
echo               WIKI BACKUP MANAGER
echo ======================================================
echo [1] Create New Backup
echo [2] List Existing Backups
echo [3] Prune Old Backups (Keep latest 5)
echo [4] Return to Dashboard
echo ======================================================
set /p choice="Action (1-4): "

if "%choice%"=="1" goto create
if "%choice%"=="2" goto list
if "%choice%"=="3" goto prune
if "%choice%"=="4" exit /b
goto menu

:create
echo.
set "desc="
set /p "desc=Enter a short description (optional): "
if defined desc set "desc=!desc: =_!"

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set "stamp=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%%datetime:~12,2%"
if "!desc!"=="" (set "DEST=%BACKUP_ROOT%\%stamp%") else (set "DEST=%BACKUP_ROOT%\%stamp%_!desc!")

echo [1/1] Creating mirrored backup at: %DEST%
if not exist "%BACKUP_ROOT%" mkdir "%BACKUP_ROOT%"
robocopy "%SOURCE%" "%DEST%" /MIR /XD .git .obsidian /R:3 /W:3
echo.
echo Success: Backup created.
pause
goto menu

:list
echo.
echo Existing Backups in %BACKUP_ROOT%:
if not exist "%BACKUP_ROOT%" (echo No backups found.) else (dir "%BACKUP_ROOT%" /AD /B /O-N)
pause
goto menu

:prune
echo [1/1] Pruning old backups... keeping latest 5.
for /f "skip=5 delims=" %%A in ('dir "%BACKUP_ROOT%" /AD /B /O-N') do (
    echo Deleting old backup: %%A
    rd /s /q "%BACKUP_ROOT%\%%A"
)
echo Pruning complete.
pause
goto menu