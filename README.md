# Clinical Workflow Automation Agent 

A production-ready **function-calling LLM agent** for healthcare workflow orchestration using **LangChain** and **HuggingFace**. This agent acts as an intelligent coordinator for clinical and administrative tasks, **NOT** as a medical advisor.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

##  Project Overview

### Industry Context

Healthcare organizations are drowning in unstructured data (clinical notes, discharge summaries) while their operational systems remain rigid, API-driven, and heavily regulated. This agent bridges the gap by providing intelligent workflow automation that is:

- **Safe**: Enforces strict validation and safety constraints
- **Auditable**: Logs every action for regulatory compliance
- **Deterministic**: Uses function calling, not free-text generation
- **Structured**: Returns validated, schema-compliant data

### What This Agent Does

 **Workflow Orchestration:**
- Patient search and lookup
- Insurance eligibility verification
- Appointment slot discovery
- Appointment booking and scheduling

### What This Agent Does NOT Do

 **Medical Advice & Diagnosis:**
- No diagnoses
- No treatment recommendations
- No prescription guidance
- No symptom interpretation
- No medication advice

##  Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (CLI)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   Clinical Workflow Agent                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   LLM Core   │  │  Validators  │  │  Audit Logger   │  │
│  │  (HuggingFace)│ │  (Safety)    │  │  (Compliance)   │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              Healthcare API Layer (Functions)                │
│  • search_patient()                                          │
│  • check_insurance_eligibility()                             │
│  • find_available_slots()                                    │
│  • book_appointment()                                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│         Mock EHR/Scheduling Systems (Sandbox)                │
│         (In production: Real FHIR APIs)                      │
└─────────────────────────────────────────────────────────────┘
```

##  Quick Start

### Prerequisites

- **Python 3.8+**
- **HuggingFace API Key** (free tier works fine)
- **pip** or **conda** for package management

### Installation

1. **Clone or download this project:**
```bash
cd clinical-workflow-agent
```

2. **Create a virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up your API key:**

Create a `.env` file in the project root:
```bash
HUGGINGFACE_API_KEY= purushoth_api
DRY_RUN_MODE=false
LOG_LEVEL=INFO
MOCK_API_ENABLED=true
```

### Running the Agent

**Normal Mode:**
```bash
python main.py
```

**Dry-Run Mode** (simulate without executing):
```bash
python main.py --dry-run
```

**Help:**
```bash
python main.py --help
```

##  Usage Examples

### Example 1: Search for a Patient

```
You: Find patient Ravi Kumar

Agent Response:
 search_patient
   • Name: Ravi Kumar
   • ID: P123456
   • Phone: +91-9876543210
```

### Example 2: Check Insurance Eligibility

```
You: Check insurance eligibility for patient P123456

Agent Response:
check_insurance_eligibility
   • Eligible: 
   • Payer: National Health Insurance
   • Plan: Premium Care Plan
   • Copay: $500.00
```

### Example 3: Find Available Appointments

```
You: Find cardiology appointments next week

Agent Response:
 find_available_slots
   • Found 8 available slot(s)
   - 2025-12-20T09:00:00: Dr. Sarah Johnson
     Slot ID: SLOT-20251220-09-DR001
   - 2025-12-20T14:00:00: Dr. Michael Chen
     Slot ID: SLOT-20251220-14-DR002
```

### Example 4: Complete Workflow

```
You: Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance eligibility

Agent Response:
Reasoning: I'll first search for the patient, check their insurance, 
find available cardiology slots, and book an appointment.

 search_patient
   • Found patient: Ravi Kumar (P123456)

 check_insurance_eligibility
   • Eligible: yes
   • Copay: $500.00

 find_available_slots
   • Found 8 cardiology slots

book_appointment
   • Appointment ID: APT-20251219143022
   • Provider: Dr. Sarah Johnson
   • Time: 2025-12-21T09:00:00
   • Location: Clinic Building A, Room 205
```

### Example 5: Safety Violation (Rejected)

```
You: What medication should I take for my headache?

Agent Response:
 SAFETY VIOLATION: This agent cannot provide medical advice, 
diagnosis, or treatment recommendations. 
Please consult a licensed healthcare provider.
```

##  Safety & Compliance Features

### 1. Input Validation

All inputs are validated against:
- FHIR-compliant schemas (Pydantic models)
- Safety patterns (no medical advice keywords)
- Parameter constraints (dates, IDs, names)

### 2. Audit Logging

Every action is logged with:
- Timestamp
- Function called
- Parameters used
- Results or errors
- User session ID

**Log files are stored in:** `logs/audit_YYYYMMDD_HHMMSS.jsonl`

### 3. Dry-Run Mode

Test workflows without making actual changes:
```bash
python main.py --dry-run
```

### 4. Prohibited Actions

The agent will **refuse** to:
- Provide diagnoses
- Recommend treatments
- Prescribe medications
- Interpret symptoms
- Give medical advice

##  Project Structure

```
clinical-workflow-agent/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── agent.py                 # Core LLM agent with function calling
│   ├── schemas.py               # FHIR-compliant Pydantic models
│   ├── validators.py            # Safety and input validation
│   ├── audit_logger.py          # Compliance logging system
│   ├── healthcare_api.py        # Mock healthcare API functions
│   └── cli.py                   # Command-line interface
├── logs/                        # Audit logs (auto-generated)
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (API keys)
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HUGGINGFACE_API_KEY` | Your HuggingFace API key | Required |
| `DRY_RUN_MODE` | Enable dry-run mode | `false` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `MOCK_API_ENABLED` | Use mock APIs | `true` |

### Supported Models

The agent uses **Mistral-7B-Instruct-v0.2** by default. You can modify this in `src/agent.py`:

```python
agent = ClinicalWorkflowAgent(
    api_key=api_key,
    model="mistralai/Mistral-7B-Instruct-v0.2"  # Change here
)
```

**Recommended models:**
- `mistralai/Mistral-7B-Instruct-v0.2` (default)
- `meta-llama/Llama-2-7b-chat-hf`
- `HuggingFaceH4/zephyr-7b-beta`

## 🔌 API Functions

### 1. `search_patient(name=None, patient_id=None)`

Search for patients by name or ID.

**Parameters:**
- `name` (str, optional): Patient name (partial match)
- `patient_id` (str, optional): Exact patient ID

**Returns:**
- Patient object with demographics

### 2. `check_insurance_eligibility(patient_id)`

Verify insurance coverage and eligibility.

**Parameters:**
- `patient_id` (str): Patient identifier

**Returns:**
- Insurance coverage details, eligibility status, copay

### 3. `find_available_slots(specialty, start_date=None, end_date=None)`

Find available appointment time slots.

**Parameters:**
- `specialty` (str): Medical specialty (cardiology, neurology, etc.)
- `start_date` (str, optional): Search start date (ISO format)
- `end_date` (str, optional): Search end date (ISO format)

**Returns:**
- List of available appointment slots with provider info

### 4. `book_appointment(patient_id, slot_id, reason=None, notes=None)`

Book an appointment for a patient.

**Parameters:**
- `patient_id` (str): Patient identifier
- `slot_id` (str): Selected slot ID from `find_available_slots`
- `reason` (str, optional): Visit reason
- `notes` (str, optional): Additional notes

**Returns:**
- Confirmed appointment details

##  Testing & Validation

### Run with Dry-Run Mode

Test workflows without making changes:
```bash
python main.py --dry-run
```

### View Audit Logs

All actions are logged in `logs/audit_*.jsonl`:
```bash
# View the latest log
cat logs/audit_*.jsonl | jq .
```

### Session Summary

Get session statistics:
```
You: summary

Session Summary:
├─ Session ID: 20251219_143022
├─ Total Function Calls: 15
├─ Successful Calls: 13
├─ Failed Calls: 2
└─ Dry Runs: 0
```

##  Learning Outcomes

By studying this project, you'll learn how to:

1.  **Design function schemas** aligned with real healthcare APIs (FHIR)
2.  **Implement deterministic tool execution** via function calling
3.  **Enforce safety and validation** at multiple layers
4.  **Build auditable systems** for regulatory compliance
5.  **Create agents that reason then act**, not hallucinate
6.  **Integrate LLMs** with structured external APIs
7.  **Handle errors gracefully** with proper validation

##  Security Considerations

### For Production Deployment

1. **API Key Management:**
   - Use secrets management (AWS Secrets Manager, Azure Key Vault)
   - Rotate keys regularly
   - Never commit keys to version control

2. **HIPAA Compliance:**
   - Enable encryption at rest and in transit
   - Implement role-based access control (RBAC)
   - Audit log retention per regulations
   - PHI de-identification where required

3. **Authentication & Authorization:**
   - Add OAuth2/SAML for user authentication
   - Implement session management
   - Add rate limiting

4. **Data Privacy:**
   - Ensure logs don't contain PHI
   - Implement data retention policies
   - Add consent management

##  Extending the Agent

### Adding New Functions

1. **Define the function** in `src/healthcare_api.py`:
```python
@staticmethod
def cancel_appointment(appointment_id: str) -> Dict[str, Any]:
    # Implementation
    pass
```

2. **Add function schema** in `FUNCTION_SCHEMAS`:
```python
{
    "type": "function",
    "function": {
        "name": "cancel_appointment",
        "description": "Cancel an existing appointment",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {"type": "string"}
            },
            "required": ["appointment_id"]
        }
    }
}
```

3. **Add validation** in `src/validators.py`:
```python
def validate_appointment_id(appointment_id: str) -> bool:
    # Validation logic
    pass
```

4. **Update function map** in `src/agent.py`:
```python
function_map = {
    # ...existing functions...
    "cancel_appointment": self.healthcare_api.cancel_appointment
}
```

### Connecting to Real APIs

Replace the mock implementations in `src/healthcare_api.py` with real API calls:

```python
def search_patient(self, name: str) -> Dict[str, Any]:
    # Instead of MOCK_PATIENTS, call real EHR API
    response = requests.get(
        f"{FHIR_BASE_URL}/Patient",
        params={"name": name},
        headers={"Authorization": f"Bearer {self.api_token}"}
    )
    return response.json()
```

##  Troubleshooting

### Issue: "HUGGINGFACE_API_KEY not found"

**Solution:** Create a `.env` file with your API key:
```bash
HUGGINGFACE_API_KEY=your_key_here
```

### Issue: "Model loading failed"

**Solution:** Try a different model or check your API key permissions.

### Issue: "Function calls not working"

**Solution:** Enable dry-run mode to see what the agent is trying to do:
```bash
python main.py --dry-run
```

### Issue: "Import errors"

**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

##  License

This project is provided as educational material. For production use, ensure compliance with:
- HIPAA (Health Insurance Portability and Accountability Act)
- HITECH (Health Information Technology for Economic and Clinical Health)
- FDA regulations for medical software
- Local healthcare regulations

##  Contributing

This is an educational project. To extend it:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

##  Support

For questions about this project:
- Review the code documentation
- Check the audit logs for debugging
- Read the FHIR specification for healthcare standards

##  Next Steps

1. **Test the agent** with various workflow scenarios
2. **Review audit logs** to understand the decision flow
3. **Experiment with dry-run mode** for safety
4. **Extend functionality** by adding new healthcare functions
5. **Deploy locally** and demonstrate to evaluators

---

** IMPORTANT DISCLAIMER:**

This is an educational proof-of-concept. It is NOT intended for:
- Production clinical use
- Patient care decisions
- Real patient data processing
- Medical diagnosis or treatment

Always consult licensed healthcare professionals for medical advice and treatment.

---

Built with  for healthcare workflow automation education.

#   C l i n i c a l - W o r k f l o w - A g e n t 
 
 #   C l i n i c a l - W o r k f l o w - A g e n t 
 
 
