"""
FHIR-Inspired Schemas for Healthcare Data
These schemas enforce structure and validation for patient data,
appointments, and insurance information.
"""
from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum

# ============================================================================
# Patient Resources (FHIR-inspired)
# ============================================================================

class HumanName(BaseModel):
    """FHIR HumanName structure"""
    use: Literal["official", "usual", "temp", "nickname"] = "official"
    family: str = Field(..., description="Family/last name")
    given: List[str] = Field(..., description="Given/first name(s)")
    
    def full_name(self) -> str:
        """Return formatted full name"""
        given = " ".join(self.given)
        return f"{given} {self.family}"

class Address(BaseModel):
    """FHIR Address structure"""
    line: List[str] = Field(..., description="Street address lines")
    city: str
    state: str
    postal_code: str
    country: str = "USA"

class ContactPoint(BaseModel):
    """FHIR ContactPoint structure"""
    system: Literal["phone", "email", "fax"] = "phone"
    value: str
    use: Literal["home", "work", "mobile"] = "mobile"

class Identifier(BaseModel):
    """FHIR Identifier structure"""
    system: str = Field(..., description="Identifier system (e.g., MRN)")
    value: str = Field(..., description="Identifier value")

class Patient(BaseModel):
    """FHIR Patient resource"""
    id: str = Field(..., description="Unique patient identifier")
    identifier: List[Identifier] = Field(default_factory=list)
    active: bool = True
    name: List[HumanName]
    telecom: List[ContactPoint] = Field(default_factory=list)
    gender: Literal["male", "female", "other", "unknown"] = "unknown"
    birth_date: date
    address: List[Address] = Field(default_factory=list)
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        """Ensure birth date is not in future"""
        if v > date.today():
            raise ValueError("Birth date cannot be in the future")
        return v

# ============================================================================
# Insurance/Coverage Resources
# ============================================================================

class CoverageStatus(str, Enum):
    """Insurance coverage status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    DRAFT = "draft"
    ENTERED_IN_ERROR = "entered-in-error"

class Coverage(BaseModel):
    """FHIR Coverage resource (insurance)"""
    id: str
    status: CoverageStatus
    subscriber_id: str = Field(..., description="Insurance member ID")
    beneficiary: str = Field(..., description="Patient ID")
    payor: str = Field(..., description="Insurance company name")
    plan_name: str
    coverage_start: date
    coverage_end: Optional[date] = None
    copay: Optional[float] = None
    deductible: Optional[float] = None
    out_of_pocket_max: Optional[float] = None

class EligibilityResponse(BaseModel):
    """Insurance eligibility check response"""
    patient_id: str
    coverage_id: str
    is_eligible: bool
    status: CoverageStatus
    coverage_details: Coverage
    service_type: str = Field(..., description="Type of service being checked")
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None

# ============================================================================
# Appointment/Scheduling Resources
# ============================================================================

class AppointmentStatus(str, Enum):
    """FHIR Appointment status"""
    PROPOSED = "proposed"
    PENDING = "pending"
    BOOKED = "booked"
    ARRIVED = "arrived"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    NOSHOW = "noshow"

class Participant(BaseModel):
    """Appointment participant"""
    actor_type: Literal["patient", "practitioner", "location"] = "patient"
    actor_id: str
    required: bool = True
    status: Literal["accepted", "declined", "tentative", "needs-action"] = "accepted"

class AppointmentSlot(BaseModel):
    """Available appointment slot"""
    slot_id: str
    start: datetime
    end: datetime
    practitioner_id: str
    practitioner_name: str
    specialty: str
    location: str
    available: bool = True

class Appointment(BaseModel):
    """FHIR Appointment resource"""
    id: str
    status: AppointmentStatus
    service_type: str = Field(..., description="Type of service (e.g., cardiology)")
    specialty: str
    description: Optional[str] = None
    start: datetime
    end: datetime
    participant: List[Participant]
    location: str
    created: datetime = Field(default_factory=datetime.utcnow)
    comment: Optional[str] = None
    
    @validator('end')
    def validate_end_after_start(cls, v, values):
        """Ensure appointment end is after start"""
        if 'start' in values and v <= values['start']:
            raise ValueError("Appointment end must be after start")
        return v

# ============================================================================
# Function Call Schemas (Tool Input/Output)
# ============================================================================

class SearchPatientInput(BaseModel):
    """Input schema for search_patient function"""
    query: str = Field(
        ..., 
        description="Patient name or identifier to search for",
        min_length=2
    )
    search_type: Literal["name", "mrn", "phone"] = Field(
        default="name",
        description="Type of search to perform"
    )

class SearchPatientOutput(BaseModel):
    """Output schema for search_patient function"""
    patients: List[Patient]
    total_count: int
    query: str

class CheckEligibilityInput(BaseModel):
    """Input schema for check_insurance_eligibility function"""
    patient_id: str = Field(..., description="Patient ID to check eligibility for")
    service_type: str = Field(
        ..., 
        description="Service type (e.g., 'cardiology', 'general-practice')"
    )

class FindSlotsInput(BaseModel):
    """Input schema for find_available_slots function"""
    specialty: str = Field(..., description="Medical specialty (e.g., 'cardiology')")
    start_date: date = Field(..., description="Start date for slot search")
    end_date: date = Field(..., description="End date for slot search")
    practitioner_name: Optional[str] = Field(
        None, 
        description="Specific practitioner name if requested"
    )
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Ensure date range is valid"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError("End date must be after start date")
        return v

class FindSlotsOutput(BaseModel):
    """Output schema for find_available_slots function"""
    slots: List[AppointmentSlot]
    total_count: int
    specialty: str
    date_range: str

class BookAppointmentInput(BaseModel):
    """Input schema for book_appointment function"""
    patient_id: str = Field(..., description="Patient ID")
    slot_id: str = Field(..., description="Slot ID to book")
    reason: Optional[str] = Field(None, description="Reason for appointment")
    comment: Optional[str] = Field(None, description="Additional comments")

class BookAppointmentOutput(BaseModel):
    """Output schema for book_appointment function"""
    appointment: Appointment
    confirmation_number: str
    success: bool
    message: str

# ============================================================================
# Audit and Safety
# ============================================================================

class AuditLogEntry(BaseModel):
    """Audit log entry for compliance"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str = Field(..., description="Action performed")
    function_name: str = Field(..., description="Function called")
    input_data: dict = Field(..., description="Sanitized input data")
    output_data: dict = Field(..., description="Sanitized output data")
    user_query: str = Field(..., description="Original user query")
    success: bool
    error_message: Optional[str] = None
    agent_reasoning: Optional[str] = None

class SafetyValidation(BaseModel):
    """Safety validation result"""
    is_safe: bool
    reason: Optional[str] = None
    violations: List[str] = Field(default_factory=list)




