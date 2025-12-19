# Setup Guide - Clinical Workflow Automation Agent

Complete step-by-step setup instructions for Windows, Mac, and Linux.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [First Run](#first-run)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Check version: `python --version` or `python3 --version`
   - Download: https://www.python.org/downloads/

2. **pip (Python package manager)**
   - Usually comes with Python
   - Check: `pip --version`

3. **HuggingFace Account & API Key**
   - Create account: https://huggingface.co/join
   - Get API key: https://huggingface.co/settings/tokens
   - Your key: `purushoth_api_key` (already provided)

---

## Installation

### Step 1: Navigate to Project Directory

```bash
cd C:\Users\admin\Documents\H
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- langchain (LLM framework)
- huggingface_hub (HuggingFace API client)
- pydantic (Data validation)
- rich (Beautiful terminal output)
- python-dotenv (Environment variables)
- And other dependencies

**Expected output:**
```
Successfully installed langchain-0.1.0 pydantic-2.5.3 ...
```

---

## Configuration

### Step 1: Environment Variables

The `.env` file is already created with your API key:

```bash
HUGGINGFACE_API_KEY=purushoth_api_key
DRY_RUN_MODE=false
LOG_LEVEL=INFO
MOCK_API_ENABLED=true
```

### Step 2: Verify Configuration

Check that the `.env` file exists:

**Windows:**
```powershell
type .env
```

**Mac/Linux:**
```bash
cat .env
```

---

## First Run

### Test Installation

Run the agent in dry-run mode first (safe testing):

```bash
python main.py --dry-run
```

You should see:
```
🤖 Clinical Workflow Agent initialized
   Model: mistralai/Mistral-7B-Instruct-v0.2
   Dry Run: True
   Log File: logs\audit_20251219_143022.jsonl

╔════════════════════════════════════════════════════════════╗
║                         Welcome                            ║
╚════════════════════════════════════════════════════════════╝

🏥 Clinical Workflow Automation Agent

Type 'help' for example commands, or 'quit' to exit.

You:
```

### Try Example Commands

1. **Get help:**
```
You: help
```

2. **Search for a patient:**
```
You: Find patient Ravi Kumar
```

3. **Check the session summary:**
```
You: summary
```

4. **Exit:**
```
You: quit
```

### Run in Normal Mode

Once you're comfortable, run without dry-run:

```bash
python main.py
```

---

## Troubleshooting

### Problem: "python: command not found"

**Solution:** Use `python3` instead:
```bash
python3 -m venv venv
python3 main.py
```

### Problem: "Cannot activate virtual environment" (Windows PowerShell)

**Solution:** Enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try again:
```powershell
.\venv\Scripts\Activate.ps1
```

### Problem: "Module not found" errors

**Solution:** Ensure virtual environment is activated and reinstall:
```bash
# Check if (venv) is in your prompt
pip install -r requirements.txt --upgrade
```

### Problem: "HUGGINGFACE_API_KEY not found"

**Solution:** Check your `.env` file exists and has the correct format:
```bash
# Windows
type .env

# Mac/Linux
cat .env
```

Should contain:
```
HUGGINGFACE_API_KEY=purushoth_api_key
```

### Problem: "API key is invalid"

**Solution:** Generate a new key at https://huggingface.co/settings/tokens and update `.env`

### Problem: "Connection timeout" or "API errors"

**Solution:** 
1. Check your internet connection
2. Try a different model in `src/agent.py`:
```python
model="mistralai/Mistral-7B-Instruct-v0.2"  # Change this
```

Alternatives:
- `meta-llama/Llama-2-7b-chat-hf`
- `HuggingFaceH4/zephyr-7b-beta`

### Problem: No output or hanging

**Solution:** The first run may take time to download the model. Wait 2-3 minutes.

---

## Verification Checklist

Before demonstrating to evaluators, verify:

- [ ] Python 3.8+ is installed
- [ ] Virtual environment is activated (see `(venv)` in prompt)
- [ ] All dependencies installed successfully
- [ ] `.env` file exists with API key
- [ ] Agent starts without errors (`python main.py`)
- [ ] Can search for patients
- [ ] Can check insurance eligibility
- [ ] Audit logs are created in `logs/` directory
- [ ] Dry-run mode works (`python main.py --dry-run`)

---

## Quick Reference

### Activate Virtual Environment

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Run the Agent

```bash
# Normal mode
python main.py

# Dry-run mode (safe testing)
python main.py --dry-run

# Help
python main.py --help
```

### Deactivate Virtual Environment

```bash
deactivate
```

### View Logs

```bash
# Windows
type logs\audit_*.jsonl

# Mac/Linux
cat logs/audit_*.jsonl
```

---

## Next Steps

1. ✅ Complete setup (you are here)
2. 📖 Read the [README.md](README.md) for usage examples
3. 🧪 Test with example scenarios
4. 📊 Review audit logs
5. 🎯 Prepare for evaluator demo

---

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Review error messages in the logs
3. Verify all prerequisites are met
4. Try dry-run mode first

---

**Ready to go! Run `python main.py` to start the agent.** 🚀

