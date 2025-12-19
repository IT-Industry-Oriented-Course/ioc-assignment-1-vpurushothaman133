# Git Setup Instructions

## Problem
Git is not installed or not in your system PATH.

## Solution

### Step 1: Install Git for Windows

1. **Download Git:**
   - Visit: https://git-scm.com/download/win
   - Download the latest version (64-bit recommended)

2. **Install Git:**
   - Run the installer
   - Use default options (recommended)
   - Make sure "Add Git to PATH" is checked during installation

3. **Restart your terminal/PowerShell:**
   - Close and reopen PowerShell or Command Prompt
   - Or restart your computer

### Step 2: Verify Installation

Open PowerShell and run:
```powershell
git --version
```

You should see something like: `git version 2.x.x`

### Step 3: Configure Git (First Time Only)

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 4: Push to GitHub

Once Git is installed, you have two options:

**Option A: Run the batch script**
```powershell
.\push_to_github.bat
```

**Option B: Run commands manually**
```powershell
git init
git add README.md
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/PURUSHOTHAMAN-V/Clinical-Workflow-Agent.git
git push -u origin main
```

## Alternative: Use GitHub Desktop

If you prefer a GUI:
1. Download GitHub Desktop: https://desktop.github.com/
2. Sign in with your GitHub account
3. Click "File" → "Add Local Repository"
4. Select your project folder
5. Click "Publish repository"

## Troubleshooting

**If git command still not found after installation:**
1. Restart your computer
2. Or manually add Git to PATH:
   - Find Git installation (usually `C:\Program Files\Git\bin`)
   - Add it to System Environment Variables → Path

**If push fails with authentication error:**
- You may need to set up a Personal Access Token (PAT)
- Or use GitHub Desktop which handles authentication automatically

