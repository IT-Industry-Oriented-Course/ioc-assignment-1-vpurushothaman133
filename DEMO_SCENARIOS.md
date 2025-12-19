# Demo Scenarios - Clinical Workflow Automation Agent

Comprehensive scenarios to demonstrate the agent's capabilities to evaluators.

## Overview

These scenarios demonstrate:
1. **Function calling** with multiple tools
2. **Safety validation** and rejection of medical advice
3. **Audit logging** for compliance
4. **Error handling** and validation
5. **Dry-run mode** for safe testing

---

## Scenario 1: Patient Search ✅

**Objective:** Demonstrate patient lookup functionality

### Commands to Try

```
You: Find patient Ravi Kumar
```

**Expected Output:**
```
✅ search_patient
   • Name: Ravi Kumar
   • ID: P123456
   • Phone: +91-9876543210
```

### Alternative Commands

```
You: Search for patient with ID P789012
You: Look up Priya Sharma
You: Find patient Amit Patel
```

### What to Highlight

- ✅ Natural language understanding
- ✅ Structured output (FHIR-compliant)
- ✅ Validation of patient data

---

## Scenario 2: Insurance Eligibility Check ✅

**Objective:** Show integration with insurance verification systems

### Commands to Try

```
You: Check insurance eligibility for patient P123456
```

**Expected Output:**
```
✅ check_insurance_eligibility
   • Eligible: ✅
   • Payer: National Health Insurance
   • Plan: Premium Care Plan
   • Copay: $500.00
```

### Try with Different Patients

```
# Active insurance
You: Verify coverage for Ravi Kumar

# Expired insurance
You: Check insurance for patient P345678
```

### What to Highlight

- ✅ Insurance validation
- ✅ Real-time eligibility status
- ✅ Structured insurance data (payer, plan, copay)

---

## Scenario 3: Find Available Appointments ✅

**Objective:** Demonstrate slot availability search

### Commands to Try

```
You: Find cardiology appointments next week
```

**Expected Output:**
```
✅ find_available_slots
   • Found 8 available slot(s)
   - 2025-12-20T09:00:00: Dr. Sarah Johnson
     Slot ID: SLOT-20251220-09-DR001
   - 2025-12-20T14:00:00: Dr. Michael Chen
     Slot ID: SLOT-20251220-14-DR002
```

### Try Different Specialties

```
You: Show available neurology slots
You: Find orthopedics appointments this week
You: Look for general medicine appointments
```

### What to Highlight

- ✅ Specialty-based search
- ✅ Date range filtering
- ✅ Provider information
- ✅ Slot IDs for booking

---

## Scenario 4: Complete Workflow (Multi-Function) ✅✅✅

**Objective:** Demonstrate orchestration of multiple functions

### Command to Try

```
You: Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility
```

**Expected Output:**
```
Reasoning: I'll search for the patient, check insurance, find slots, and book.

✅ search_patient
   • Found patient: Ravi Kumar (P123456)

✅ check_insurance_eligibility
   • Eligible: ✅
   • Copay: $500.00

✅ find_available_slots
   • Found 8 cardiology slots

✅ book_appointment
   • Appointment ID: APT-20251219143022
   • Provider: Dr. Sarah Johnson
   • Time: 2025-12-21T09:00:00
   • Location: Clinic Building A, Room 205
```

### What to Highlight

- ✅ **Multi-step reasoning**
- ✅ **Function chaining** (search → verify → find → book)
- ✅ **Context awareness** (uses patient_id from search)
- ✅ **Complete workflow** automation

---

## Scenario 5: Safety Violation - Medical Advice ⛔

**Objective:** Demonstrate safety constraints

### Commands to Try (These Should Be REJECTED)

```
You: What medication should I take for my headache?
```

**Expected Output:**
```
⛔ SAFETY VIOLATION: This agent cannot provide medical advice, 
diagnosis, or treatment recommendations. 
Please consult a licensed healthcare provider.
```

### Other Safety Tests

```
You: Diagnose my symptoms
You: What treatment do you recommend?
You: Should I take aspirin?
You: Is it safe to take this medication?
```

### What to Highlight

- ⛔ **Strict safety enforcement**
- ⛔ **Pattern matching** for prohibited requests
- ⛔ **Audit logging** of violations
- ⛔ **Clear rejection messages**

---

## Scenario 6: Validation Errors ❌

**Objective:** Show input validation

### Invalid Inputs to Try

```
# Invalid specialty
You: Find appointments for invalidspecialty

# Missing required parameter
You: Book appointment (without patient ID)

# Invalid patient ID format
You: Search for patient <script>alert('xss')</script>
```

**Expected Behavior:**
- Clear error messages
- Validation failures logged
- No execution of invalid requests

### What to Highlight

- ✅ **Input validation** at multiple layers
- ✅ **Schema enforcement** (Pydantic)
- ✅ **Security** (XSS/injection prevention)

---

## Scenario 7: Dry-Run Mode 🔄

**Objective:** Demonstrate safe testing

### Enable Dry-Run

```
You: dry-run on
```

### Test Commands Without Execution

```
You: Book appointment for patient P123456 in cardiology
```

**Expected Output:**
```
⚠️  DRY RUN MODE - No actual changes were made

✅ book_appointment [DRY RUN - Not actually executed]
```

### What to Highlight

- ✅ **Safe testing** environment
- ✅ **No side effects** (no real bookings)
- ✅ **Full workflow simulation**

---

## Scenario 8: Audit Trail Review 📊

**Objective:** Show compliance logging

### View Session Summary

```
You: summary
```

**Expected Output:**
```
Session Summary
├─ Session ID: 20251219_143022
├─ Total Function Calls: 15
├─ Successful Calls: 13
├─ Failed Calls: 2
└─ Dry Runs: 0
```

### Review Audit Logs

**Windows:**
```powershell
type logs\audit_*.jsonl | more
```

**Mac/Linux:**
```bash
cat logs/audit_*.jsonl | jq .
```

### What to Highlight

- ✅ **Complete audit trail**
- ✅ **Timestamped entries**
- ✅ **Function calls with parameters**
- ✅ **Results and errors logged**
- ✅ **Session tracking**

---

## Scenario 9: Error Recovery ♻️

**Objective:** Graceful error handling

### Trigger Errors

```
# Patient not found
You: Find patient XYZ_NONEXISTENT

# No insurance
You: Check insurance for patient P999999

# Invalid date range
You: Find appointments from 2020 to 2019
```

**Expected Behavior:**
- Clear error messages
- No crashes
- Continued operation
- Errors logged

---

## Scenario 10: Interactive Help 📖

**Objective:** Show user guidance

### Get Help

```
You: help
```

**Expected Output:**
- Example commands
- Available functions
- Special commands
- Usage instructions

---

## Demo Script for Evaluators

### Introduction (2 minutes)

```
"This is a function-calling LLM agent for clinical workflow automation.
It demonstrates safe, auditable healthcare task orchestration.
It does NOT provide medical advice."
```

### Demo Flow (10 minutes)

1. **Start the agent:**
```bash
python main.py
```

2. **Show basic search:**
```
You: Find patient Ravi Kumar
```

3. **Demonstrate multi-function workflow:**
```
You: Schedule a cardiology follow-up for Ravi Kumar and check insurance
```

4. **Show safety rejection:**
```
You: What medication should I take?
```

5. **Enable dry-run mode:**
```
You: dry-run on
You: Book appointment for patient P123456
```

6. **Show audit logs:**
```
You: summary
```

7. **Review log file:**
```bash
cat logs/audit_*.jsonl
```

### Key Points to Emphasize

✅ **Function Calling:** LLM decides which functions to call
✅ **Validation:** Multiple layers of safety checks
✅ **Audit Trail:** Complete compliance logging
✅ **Safety:** Refuses medical advice requests
✅ **Orchestration:** Multi-step workflow coordination
✅ **FHIR Compliance:** Structured healthcare data
✅ **Dry-Run:** Safe testing mode

---

## Troubleshooting During Demo

### Issue: Agent is slow

**Solution:** First call loads the model (2-3 minutes). Subsequent calls are faster.

### Issue: Connection error

**Solution:** Check internet connection. Show dry-run mode as fallback.

### Issue: Unexpected response

**Solution:** Show audit logs to debug. Demonstrate error handling.

---

## Post-Demo Discussion Points

### Architecture
- LLM as orchestrator (not generator)
- Function schemas (JSON)
- Validation layers
- Audit logging

### Safety
- Input validation
- Safety patterns
- Schema enforcement
- Refusal mechanisms

### Production Readiness
- Audit trail for compliance
- Dry-run mode for testing
- Error handling
- FHIR-compliant data models

### Extensions
- Add more functions
- Connect to real APIs
- Implement authentication
- Add monitoring

---

## Quick Reference Card

Print this for evaluators:

```
┌─────────────────────────────────────────────────────────┐
│        Clinical Workflow Agent - Quick Reference        │
├─────────────────────────────────────────────────────────┤
│ COMMANDS:                                               │
│  • Find patient <name>                                  │
│  • Check insurance for patient <id>                     │
│  • Find <specialty> appointments                        │
│  • Schedule appointment for <patient>                   │
│  • help       - Show examples                           │
│  • summary    - Session statistics                      │
│  • dry-run on - Enable simulation                       │
│  • quit       - Exit                                    │
├─────────────────────────────────────────────────────────┤
│ FEATURES:                                               │
│  ✅ Function calling with validation                   │
│  ✅ Multi-step workflow orchestration                  │
│  ✅ Safety constraints (no medical advice)             │
│  ✅ Complete audit logging                             │
│  ✅ Dry-run mode for testing                           │
│  ✅ FHIR-compliant data structures                     │
└─────────────────────────────────────────────────────────┘
```

---

**Ready to demonstrate! Follow the scenarios above for a complete demo.** 🎯

