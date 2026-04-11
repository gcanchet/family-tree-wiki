@echo off
echo [1/2] Syncing Obsidian vault content for local preview...
robocopy "C:\Users\Great\AI\obsidian\my vault" "C:\Users\Great\AI\My-Quartz-Site\content" /MIR /XD .git .obsidian /R:3 /W:3

if %ERRORLEVEL% LSS 8 (
    echo [2/2] Sync complete. Navigating to Quartz site folder and running preview server...
    cd /d "C:\Users\Great\AI\My-Quartz-Site"
    call preview.bat
) else (
    echo Error: Robocopy failed with exit code %ERRORLEVEL%. Local preview aborted.
    pause
)