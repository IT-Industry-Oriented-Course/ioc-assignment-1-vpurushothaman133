# Architecture Documentation

Detailed technical architecture of the Clinical Workflow Automation Agent.

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Safety & Validation](#safety--validation)
5. [Audit & Compliance](#audit--compliance)
6. [Function Calling Mechanism](#function-calling-mechanism)
7. [Technology Stack](#technology-stack)
8. [Production Considerations](#production-considerations)

---

## System Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      USER INTERFACE LAYER                     │
│                    (CLI - Rich Terminal UI)                   │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              │ Natural Language Input
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATION LAYER                  │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  LLM Core     │  │  Safety      │  │  Audit Logger    │  │
│  │  (HuggingFace)│◄─┤  Validator   │◄─┤  (Compliance)    │  │
│  │               │  │              │  │                  │  │
│  └───────┬───────┘  └──────────────┘  └──────────────────┘  │
│          │                                                    │
│          │ Function Call Decisions                           │
│          ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │          Function Call Executor                        │  │
│  │  • Parameter Validation                                │  │
│  │  • Schema Enforcement                                  │  │
│  │  • Dry-Run Simulation                                  │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              │ Validated API Calls
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     HEALTHCARE API LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Patient      │  │ Insurance    │  │ Scheduling       │   │
│  │ Search API   │  │ Eligibility  │  │ API              │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              │ FHIR-Compliant Responses
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    MOCK DATABASE LAYER                        │
│  (In Production: Real EHR/EMR Systems)                        │
│  • Patients  • Insurance  • Appointments  • Providers         │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Agent Core (`src/agent.py`)

**Responsibilities:**
- Natural language understanding
- Function call decision making
- Workflow orchestration
- Error handling and recovery

**Key Classes:**
- `ClinicalWorkflowAgent`: Main orchestrator

**Key Methods:**
```python
process_request(user_input: str) -> Dict[str, Any]
    ├─ validate_request_intent()
    ├─ _get_agent_decision()
    ├─ _execute_function_calls()
    └─ _generate_final_response()
```

**LLM Integration:**
- HuggingFace Inference API
- Model: Mistral-7B-Instruct-v0.2
- Temperature: 0.3 (deterministic)
- Function calling via structured prompts

---

### 2. Schema Layer (`src/schemas.py`)

**Purpose:** FHIR-compliant data models

**Key Models:**

```python
Patient
├─ id: str
├─ name: str
├─ birthDate: date
├─ gender: Gender (enum)
└─ contact: ContactPoint

InsuranceCoverage
├─ id: str
├─ patientId: str
├─ payer: str
├─ status: InsuranceStatus (enum)
└─ period: Period

Appointment
├─ id: str
├─ status: AppointmentStatus (enum)
├─ patient: Reference
├─ practitioner: Reference
├─ start: datetime
└─ end: datetime

AppointmentSlot
├─ slotId: str
├─ specialty: str
├─ provider: Reference
└─ available: bool
```

**Validation:**
- Pydantic v2 models
- Type checking
- Field constraints
- Custom validators

---

### 3. Validation Layer (`src/validators.py`)

**Two-Tier Validation:**

#### Tier 1: Safety Validation
```python
SafetyValidator
├─ validate_request_intent()      # Reject medical advice
├─ validate_patient_name()         # Format & safety
├─ validate_patient_id()           # Injection prevention
├─ validate_specialty()            # Whitelist check
└─ validate_date_range()           # Business rules
```

**Prohibited Patterns:**
- Diagnosis requests
- Treatment recommendations
- Medication questions
- Symptom interpretation

#### Tier 2: Schema Validation
```python
SchemaValidator
└─ validate_against_schema()       # Pydantic enforcement
```

---

### 4. Healthcare API Layer (`src/healthcare_api.py`)

**Functions:**

```python
HealthcareAPI
├─ search_patient(name, patient_id)
│  └─ Returns: Patient | List[Patient]
│
├─ check_insurance_eligibility(patient_id)
│  └─ Returns: InsuranceCoverage + eligibility status
│
├─ find_available_slots(specialty, start_date, end_date)
│  └─ Returns: List[AppointmentSlot]
│
└─ book_appointment(patient_id, slot_id, reason, notes)
   └─ Returns: Appointment (confirmed)
```

**Function Schemas (OpenAI-style):**
```json
{
  "type": "function",
  "function": {
    "name": "search_patient",
    "description": "Search for a patient...",
    "parameters": {
      "type": "object",
      "properties": {...},
      "required": [...]
    }
  }
}
```

**Mock Implementation:**
- In-memory database (dictionaries)
- Realistic data generation
- Random slot availability
- Production: Replace with real API calls

---

### 5. Audit Logger (`src/audit_logger.py`)

**Logging Architecture:**

```
AuditLogger
├─ Session Management
│  ├─ session_id: Unique identifier
│  └─ log_file: logs/audit_{session_id}.jsonl
│
├─ Event Types
│  ├─ session_start
│  ├─ user_input
│  ├─ function_call
│  ├─ agent_response
│  └─ safety_violation
│
└─ Log Format: JSON Lines (JSONL)
```

**Log Entry Structure:**
```json
{
  "timestamp": "2025-12-19T10:30:00",
  "event_type": "function_call",
  "function_name": "search_patient",
  "parameters": {"name": "Ravi Kumar"},
  "result": {"success": true, "patient": {...}},
  "dry_run": false,
  "session_id": "20251219_103000"
}
```

**Compliance Features:**
- Immutable logs (append-only)
- Complete parameter capture
- Result/error tracking
- Dry-run distinction
- Session correlation

---

### 6. CLI Interface (`src/cli.py`)

**Features:**
- Rich terminal formatting
- Interactive prompts
- Response formatting
- Session management
- Help system

**Special Commands:**
```
help         → Show examples
summary      → Session statistics
dry-run on   → Enable simulation mode
quit         → Exit with summary
```

---

## Data Flow

### Request Processing Pipeline

```
1. User Input
   ↓
2. Safety Validation
   ├─ Check prohibited patterns
   └─ Log input
   ↓
3. LLM Decision Making
   ├─ Send prompt with function schemas
   ├─ Parse JSON response
   └─ Extract function calls
   ↓
4. Parameter Validation
   ├─ Schema validation (Pydantic)
   ├─ Business rule validation
   └─ Security checks
   ↓
5. Function Execution
   ├─ Check dry-run mode
   ├─ Call healthcare API
   ├─ Log call + result
   └─ Handle errors
   ↓
6. Response Generation
   ├─ Aggregate results
   ├─ Format output
   └─ Return to user
   ↓
7. Audit Logging
   └─ Write to JSONL file
```

### Example: Complete Appointment Workflow

```
User: "Schedule cardiology for Ravi Kumar"
↓
Agent Decision:
{
  "reasoning": "Need to search patient, check insurance, find slots, book",
  "function_calls": [
    {"function": "search_patient", "parameters": {"name": "Ravi Kumar"}},
    {"function": "check_insurance_eligibility", "parameters": {"patient_id": "P123456"}},
    {"function": "find_available_slots", "parameters": {"specialty": "cardiology"}},
    {"function": "book_appointment", "parameters": {...}}
  ]
}
↓
Execution: Each function validated, executed, logged
↓
Response: Structured summary with appointment confirmation
```

---

## Safety & Validation

### Multi-Layer Defense

```
Layer 1: Intent Validation
         ├─ Regex pattern matching
         └─ Prohibited keyword detection

Layer 2: Parameter Validation
         ├─ Type checking (Pydantic)
         ├─ Format validation
         └─ Range constraints

Layer 3: Business Rule Validation
         ├─ Date logic
         ├─ Specialty whitelist
         └─ Identifier format

Layer 4: API-Level Validation
         ├─ Entity existence checks
         └─ Relationship validation
```

### Safety Patterns

**Prohibited Requests:**
```python
PROHIBITED_PATTERNS = [
    r'\bdiagnos(e|is)\b',
    r'\btreat(ment)?\b',
    r'\bprescri(be|ption)\b',
    r'\bmedication\b',
    # ... more patterns
]
```

**Validation Exceptions:**
```python
try:
    validate_request()
except ValidationException as e:
    log_safety_violation(e)
    return {"error": str(e), "reason": "SAFETY_VIOLATION"}
```

---

## Function Calling Mechanism

### Prompt Engineering

```python
SYSTEM_PROMPT = """
You are a Clinical Workflow Automation Agent.

CRITICAL SAFETY RULES:
1. You MUST NOT provide medical advice
2. You can ONLY perform administrative tasks

Available Functions:
{function_schemas}

Response Format (JSON):
{
  "reasoning": "...",
  "function_calls": [...]
}
"""
```

### LLM Response Parsing

```python
response = client.text_generation(prompt, temperature=0.3)
decision = json.loads(response)

# Expected structure:
{
  "reasoning": "I'll search for the patient first...",
  "function_calls": [
    {
      "function": "search_patient",
      "parameters": {"name": "Ravi Kumar"}
    }
  ]
}
```

### Function Mapping

```python
function_map = {
    "search_patient": healthcare_api.search_patient,
    "check_insurance_eligibility": healthcare_api.check_insurance_eligibility,
    "find_available_slots": healthcare_api.find_available_slots,
    "book_appointment": healthcare_api.book_appointment
}

result = function_map[function_name](**parameters)
```

---

## Technology Stack

### Core Dependencies

```
LLM Framework:
├─ langchain==0.1.0              # Agent orchestration
├─ langchain-huggingface==0.0.1  # HF integration
└─ huggingface_hub==0.20.2       # API client

Data Validation:
├─ pydantic==2.5.3               # Schema validation
└─ jsonschema==4.20.0            # JSON validation

CLI/UX:
├─ rich==13.7.0                  # Terminal formatting
└─ colorama==0.4.6               # Cross-platform colors

Utilities:
├─ python-dotenv==1.0.0          # Environment variables
├─ requests==2.31.0              # HTTP client
└─ python-dateutil==2.8.2        # Date handling
```

### Model Selection

**Current: Mistral-7B-Instruct-v0.2**
- 7B parameters
- Instruction-tuned
- Good function calling
- Free tier compatible

**Alternatives:**
- Llama-2-7b-chat-hf
- Zephyr-7b-beta
- GPT-3.5 (OpenAI)

---

## Production Considerations

### Security Enhancements

```python
# 1. Authentication
class SecureAgent(ClinicalWorkflowAgent):
    def __init__(self, api_key, auth_token):
        self.auth = OAuth2Authenticator(auth_token)
        super().__init__(api_key)

# 2. Rate Limiting
@rate_limit(max_calls=100, period=3600)
def process_request(self, user_input):
    pass

# 3. PHI Protection
def sanitize_logs(log_entry):
    # Remove or encrypt PHI before logging
    pass
```

### HIPAA Compliance

**Requirements:**
1. **Encryption:**
   - At rest: Encrypt log files
   - In transit: HTTPS/TLS for API calls

2. **Access Control:**
   - RBAC implementation
   - Audit trail for all access
   - Session management

3. **Data Retention:**
   - Configurable log retention
   - Secure deletion procedures
   - Backup policies

4. **Audit:**
   - Complete audit trail (✅ implemented)
   - Regular audit reviews
   - Breach notification procedures

### Scalability

**Current Architecture:**
- Single-instance
- In-memory mock DB
- Local logging

**Production Architecture:**
```
Load Balancer
├─ Agent Instance 1
├─ Agent Instance 2
└─ Agent Instance N
   ↓
Centralized Services
├─ Redis (session management)
├─ PostgreSQL (audit logs)
├─ Elasticsearch (log search)
└─ Monitoring (Prometheus/Grafana)
```

### Real API Integration

**Replace Mock with Real APIs:**

```python
# Current (Mock)
def search_patient(name):
    return MOCK_PATIENTS.get(name)

# Production (Real FHIR API)
def search_patient(name):
    response = requests.get(
        f"{FHIR_BASE_URL}/Patient",
        params={"name": name},
        headers={
            "Authorization": f"Bearer {self.fhir_token}",
            "Content-Type": "application/fhir+json"
        },
        timeout=30
    )
    return response.json()
```

### Monitoring & Observability

**Metrics to Track:**
- Function call success rate
- Average response time
- Safety violations count
- API error rates
- User session statistics

**Tools:**
- Prometheus (metrics)
- Grafana (dashboards)
- ELK Stack (log analysis)
- Sentry (error tracking)

---

## Extension Points

### Adding New Functions

1. Define function in `healthcare_api.py`
2. Add function schema to `FUNCTION_SCHEMAS`
3. Add validation in `validators.py`
4. Update function map in `agent.py`
5. Add tests

### Custom Validators

```python
class CustomValidator(SafetyValidator):
    @staticmethod
    def validate_custom_field(value):
        # Custom logic
        pass
```

### Alternative LLM Providers

```python
# OpenAI
from langchain.llms import OpenAI
llm = OpenAI(api_key=...)

# Anthropic Claude
from langchain.llms import Anthropic
llm = Anthropic(api_key=...)

# Local Model
from langchain.llms import LlamaCpp
llm = LlamaCpp(model_path=...)
```

---

## Design Decisions

### Why Function Calling?

✅ **Deterministic:** Predictable outputs
✅ **Structured:** Schema-validated responses
✅ **Auditable:** Every action logged
✅ **Safe:** No free-text hallucination

❌ **Not Using:** Free-text generation for critical actions

### Why Pydantic?

✅ **Type Safety:** Compile-time checks
✅ **Validation:** Automatic constraint enforcement
✅ **FHIR Alignment:** Easy to model healthcare resources
✅ **Documentation:** Self-documenting models

### Why Mock APIs?

✅ **Demo-Ready:** Works without external dependencies
✅ **Reproducible:** Consistent behavior
✅ **Safe:** No real data at risk

🔄 **Production:** Replace with real API clients

---

## Performance Considerations

### Latency Profile

```
User Input → Response:
├─ LLM Inference: 1-3 seconds (main bottleneck)
├─ Validation: <10ms
├─ API Calls: 50-200ms (mock)
└─ Logging: <5ms

Total: ~2-4 seconds per request
```

### Optimization Strategies

1. **Model Selection:** Smaller models (7B vs 13B)
2. **Caching:** Cache common LLM responses
3. **Async:** Parallel function execution
4. **Prompt Optimization:** Shorter, focused prompts

---

**This architecture prioritizes safety, auditability, and extensibility for healthcare applications.**

