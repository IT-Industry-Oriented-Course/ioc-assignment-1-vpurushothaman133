"""FHIR-compliant schemas for healthcare data validation.

These schemas enforce structure and validation on all healthcare objects
to ensure safety and compliance.
"""

from datetime import datetime, date
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum


class Gender(str, Enum):
    """FHIR-compliant gender values"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class InsuranceStatus(str, Enum):
    """Insurance eligibility status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    EXPIRED = "expired"


class AppointmentStatus(str, Enum):
    """Appointment status codes"""
    PROPOSED = "proposed"
    PENDING = "pending"
    BOOKED = "booked"
    ARRIVED = "arrived"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    NOSHOW = "noshow"


class PatientIdentifier(BaseModel):
    """Patient identifier with validation"""
    system: str = Field(..., description="Identifier namespace (e.g., MRN, SSN)")
    value: str = Field(..., description="Actual identifier value")
    
    @validator('value')
    def validate_value(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Identifier value cannot be empty")
        return v.strip()


class Patient(BaseModel):
    """FHIR-compliant Patient resource"""
    id: str = Field(..., description="Unique patient identifier")
    identifier: List[PatientIdentifier] = Field(default_factory=list)
    name: str = Field(..., min_length=2, max_length=200)
    given_name: Optional[str] = Field(None, alias="givenName")
    family_name: Optional[str] = Field(None, alias="familyName")
    birth_date: Optional[date] = Field(None, alias="birthDate")
    gender: Optional[Gender] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "P123456",
                "name": "Ravi Kumar",
                "givenName": "Ravi",
                "familyName": "Kumar",
                "birthDate": "1985-03-15",
                "gender": "male",
                "phone": "+91-9876543210"
            }
        }


class InsuranceCoverage(BaseModel):
    """Insurance coverage information"""
    id: str = Field(..., description="Coverage identifier")
    patient_id: str = Field(..., alias="patientId")
    subscriber_id: str = Field(..., alias="subscriberId")
    payer: str = Field(..., description="Insurance company name")
    plan_name: str = Field(..., alias="planName")
    status: InsuranceStatus
    period_start: Optional[date] = Field(None, alias="periodStart")
    period_end: Optional[date] = Field(None, alias="periodEnd")
    copay_amount: Optional[float] = Field(None, alias="copayAmount", ge=0)
    
    class Config:
        populate_by_name = True


class AppointmentSlot(BaseModel):
    """Available appointment time slot"""
    slot_id: str = Field(..., alias="slotId")
    specialty: str
    provider_name: str = Field(..., alias="providerName")
    provider_id: str = Field(..., alias="providerId")
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    location: str
    available: bool = True
    
    class Config:
        populate_by_name = True
        
    @validator('end_time')
    def validate_end_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("End time must be after start time")
        return v


class Appointment(BaseModel):
    """FHIR-compliant Appointment resource"""
    id: str = Field(..., description="Unique appointment identifier")
    status: AppointmentStatus
    patient_id: str = Field(..., alias="patientId")
    patient_name: str = Field(..., alias="patientName")
    provider_id: str = Field(..., alias="providerId")
    provider_name: str = Field(..., alias="providerName")
    specialty: str
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    location: str
    reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    
    class Config:
        populate_by_name = True


class FunctionCallLog(BaseModel):
    """Audit log entry for function calls"""
    timestamp: datetime = Field(default_factory=datetime.now)
    function_name: str
    parameters: dict
    result: Optional[dict] = None
    error: Optional[str] = None
    dry_run: bool = False
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-12-19T10:30:00",
                "function_name": "search_patient",
                "parameters": {"name": "Ravi Kumar"},
                "result": {"patient_id": "P123456"},
                "dry_run": False
            }
        }

