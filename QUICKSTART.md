# Quick Start Guide - 5 Minutes to Running Agent

Get the Clinical Workflow Agent running in 5 minutes.

## Option 1: Automated Setup (Recommended)

### Windows

1. Open PowerShell in the project directory
2. Run:
```powershell
.\setup.bat
```
3. Start the agent:
```powershell
venv\Scripts\activate
python main.py
```

### Mac/Linux

1. Open Terminal in the project directory
2. Run:
```bash
chmod +x setup.sh
./setup.sh
```
3. Start the agent:
```bash
source venv/bin/activate
python main.py
```

---

## Option 2: Manual Setup

### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Verify Configuration
Make sure `.env` file exists with:
```
HUGGINGFACE_API_KEY=purushoth_api_key
```

### Step 4: Run the Agent
```bash
python main.py
```

---

## Your First Commands

Once the agent starts, try these:

### 1. Get Help
```
You: help
```

### 2. Search for a Patient
```
You: Find patient Ravi Kumar
```

### 3. Complete Workflow
```
You: Schedule a cardiology follow-up for Ravi Kumar and check insurance
```

### 4. Test Safety (Should Reject)
```
You: What medication should I take?
```

### 5. View Summary
```
You: summary
```

### 6. Exit
```
You: quit
```

---

## Testing Without Interactive Mode

Run the automated test suite:
```bash
python test_agent.py
```

This runs all tests in dry-run mode (safe, no side effects).

---

## Dry-Run Mode (Safe Testing)

To simulate actions without executing them:
```bash
python main.py --dry-run
```

Or toggle within the agent:
```
You: dry-run on
```

---

## Troubleshooting

### "Python not found"
- **Windows:** Install from python.org
- **Mac:** `brew install python3`
- **Linux:** `sudo apt install python3 python3-venv`

### "Cannot activate virtual environment" (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### "API key error"
Check that `.env` file exists and contains:
```
HUGGINGFACE_API_KEY=purushoth_api_key
```

---

## What's Next?

- 📖 Read [README.md](README.md) for detailed documentation
- 🎯 Try scenarios in [DEMO_SCENARIOS.md](DEMO_SCENARIOS.md)
- 🏗️ Understand architecture in [ARCHITECTURE.md](ARCHITECTURE.md)
- ✅ Review [PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md) for demo prep

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `python main.py` | Start agent (normal mode) |
| `python main.py --dry-run` | Start in simulation mode |
| `python test_agent.py` | Run automated tests |
| `help` | Show examples in agent |
| `summary` | View session statistics |
| `dry-run on/off` | Toggle simulation mode |
| `quit` | Exit agent |

---

**You're ready! Run `python main.py` and type `help` to get started.** 🚀

