@echo off
REM Script to push to GitHub using Personal Access Token
REM Follow these steps:
REM 1. Go to https://github.com/settings/tokens
REM 2. Click "Generate new token" -> "Generate new token (classic)"
REM 3. Give it a name like "Push Token"
REM 4. Select scope: "repo" (full control of private repositories)
REM 5. Click "Generate token"
REM 6. Copy the token (it starts with ghp_)
REM 7. Run this script and paste the token when prompted

echo ================================================
echo GitHub Push with Personal Access Token
echo ================================================
echo.
echo Please enter your GitHub Personal Access Token:
echo (You can create one at: https://github.com/settings/tokens)
echo.
set /p TOKEN="Token: "

if "%TOKEN%"=="" (
    echo Error: No token provided
    pause
    exit /b 1
)

echo.
echo Setting up remote URL with token...
git remote set-url origin https://%TOKEN%@github.com/IT-Industry-Oriented-Course/ioc-assignment-1-vpurushothaman133.git

echo.
echo Pushing to repository...
git push -u origin main

echo.
echo Cleaning up (removing token from remote URL)...
git remote set-url origin https://github.com/IT-Industry-Oriented-Course/ioc-assignment-1-vpurushothaman133.git

echo.
echo Done!
pause

