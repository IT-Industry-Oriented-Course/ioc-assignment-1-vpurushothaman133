@echo off
echo Initializing Git repository...
git init

echo Adding README.md...
git add README.md

echo Committing...
git commit -m "first commit"

echo Setting branch to main...
git branch -M main

echo Adding remote origin...
git remote add origin https://github.com/PURUSHOTHAMAN-V/Clinical-Workflow-Agent.git

echo Pushing to GitHub...
git push -u origin main

echo Done!
pause

