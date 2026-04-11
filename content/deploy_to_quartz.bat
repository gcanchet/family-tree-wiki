@echo off
echo [1/2] Syncing Obsidian vault content to Quartz site...
robocopy "C:\Users\Great\AI\obsidian\my vault" "C:\Users\Great\AI\My-Quartz-Site\content" /MIR /XD .git .obsidian /R:3 /W:3

if %ERRORLEVEL% LSS 8 (
    echo [2/2] Sync complete. Navigating to Quartz site folder and running deployment script...
    cd /d "C:\Users\Great\AI\My-Quartz-Site"
    call deploy.bat
) else (
    echo Error: Robocopy failed with exit code %ERRORLEVEL%. Deployment aborted.
    pause
)