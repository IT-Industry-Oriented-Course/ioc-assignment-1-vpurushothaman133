"""
Healthcare API Functions (Mock/Sandbox Implementation)
These functions simulate real healthcare system APIs with realistic data.
In production, these would call actual FHIR servers or EHR systems.
"""
import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional
from schemas import (
    Patient, HumanName, Address, ContactPoint, Identifier,
    Coverage, CoverageStatus, EligibilityResponse,
    AppointmentSlot, Appointment, AppointmentStatus, Participant,
    SearchPatientInput, SearchPatientOutput,
    CheckEligibilityInput, FindSlotsInput, FindSlotsOutput,
    BookAppointmentInput, BookAppointmentOutput
)
from config import config

# ============================================================================
# Mock Database (In-memory for sandbox mode)
# ============================================================================

# Mock patient database
MOCK_PATIENTS = [
    Patient(
        id="PT-001",
        identifier=[Identifier(system="MRN", value="MRN123456")],
        name=[HumanName(family="Kumar", given=["Ravi"], use="official")],
        telecom=[
            ContactPoint(system="phone", value="+1-555-0101", use="mobile"),
            ContactPoint(system="email", value="ravi.kumar@email.com", use="home")
        ],
        gender="male",
        birth_date=date(1985, 3, 15),
        address=[Address(
            line=["123 Main St", "Apt 4B"],
            city="Boston",
            state="MA",
            postal_code="02101",
            country="USA"
        )]
    ),
    Patient(
        id="PT-002",
        identifier=[Identifier(system="MRN", value="MRN789012")],
        name=[HumanName(family="Smith", given=["Sarah", "Jane"], use="official")],
        telecom=[
            ContactPoint(system="phone", value="+1-555-0102", use="mobile"),
            ContactPoint(system="email", value="sarah.smith@email.com", use="home")
        ],
        gender="female",
        birth_date=date(1992, 7, 22),
        address=[Address(
            line=["456 Oak Avenue"],
            city="Cambridge",
            state="MA",
            postal_code="02139",
            country="USA"
        )]
    ),
    Patient(
        id="PT-003",
        identifier=[Identifier(system="MRN", value="MRN345678")],
        name=[HumanName(family="Johnson", given=["Michael"], use="official")],
        telecom=[
            ContactPoint(system="phone", value="+1-555-0103", use="mobile")
        ],
        gender="male",
        birth_date=date(1978, 11, 5),
        address=[Address(
            line=["789 Elm Street"],
            city="Somerville",
            state="MA",
            postal_code="02144",
            country="USA"
        )]
    ),
]

# Mock insurance coverage database
MOCK_COVERAGE = {
    "PT-001": Coverage(
        id="COV-001",
        status=CoverageStatus.ACTIVE,
        subscriber_id="SUB123456",
        beneficiary="PT-001",
        payor="BlueCross BlueShield",
        plan_name="Gold PPO",
        coverage_start=date(2024, 1, 1),
        coverage_end=date(2024, 12, 31),
        copay=30.0,
        deductible=1500.0,
        out_of_pocket_max=6000.0
    ),
    "PT-002": Coverage(
        id="COV-002",
        status=CoverageStatus.ACTIVE,
        subscriber_id="SUB789012",
        beneficiary="PT-002",
        payor="Aetna",
        plan_name="Silver HMO",
        coverage_start=date(2024, 1, 1),
        coverage_end=date(2024, 12, 31),
        copay=50.0,
        deductible=2000.0,
        out_of_pocket_max=8000.0
    ),
    "PT-003": Coverage(
        id="COV-003",
        status=CoverageStatus.CANCELLED,
        subscriber_id="SUB345678",
        beneficiary="PT-003",
        payor="UnitedHealthcare",
        plan_name="Bronze Plan",
        coverage_start=date(2023, 1, 1),
        coverage_end=date(2023, 12, 31),
        copay=75.0,
        deductible=3000.0,
        out_of_pocket_max=10000.0
    ),
}

# Mock practitioners and specialties
MOCK_PRACTITIONERS = {
    "cardiology": [
        {"id": "PRAC-001", "name": "Dr. Emily Chen", "specialty": "cardiology"},
        {"id": "PRAC-002", "name": "Dr. James Wilson", "specialty": "cardiology"},
    ],
    "general-practice": [
        {"id": "PRAC-003", "name": "Dr. Maria Garcia", "specialty": "general-practice"},
    ],
    "orthopedics": [
        {"id": "PRAC-004", "name": "Dr. Robert Taylor", "specialty": "orthopedics"},
    ],
}

# Mock appointments storage
MOCK_APPOINTMENTS = {}

# ============================================================================
# API Function: search_patient
# ============================================================================

def search_patient(query: str, search_type: str = "name") -> SearchPatientOutput:
    """
    Search for patients by name, MRN, or phone number.
    
    Args:
        query: Search query string
        search_type: Type of search ("name", "mrn", "phone")
    
    Returns:
        SearchPatientOutput with matching patients
    """
    if config.agent_mode == "sandbox":
        # Mock search logic
        results = []
        query_lower = query.lower()
        
        for patient in MOCK_PATIENTS:
            if search_type == "name":
                # Search in patient names
                for name in patient.name:
                    full_name = name.full_name().lower()
                    if query_lower in full_name:
                        results.append(patient)
                        break
            elif search_type == "mrn":
                # Search in identifiers
                for identifier in patient.identifier:
                    if query_lower in identifier.value.lower():
                        results.append(patient)
                        break
            elif search_type == "phone":
                # Search in phone numbers
                for contact in patient.telecom:
                    if contact.system == "phone" and query in contact.value:
                        results.append(patient)
                        break
        
        return SearchPatientOutput(
            patients=results,
            total_count=len(results),
            query=query
        )
    else:
        # Production mode: would call actual FHIR API
        raise NotImplementedError("Production mode not implemented")

# ============================================================================
# API Function: check_insurance_eligibility
# ============================================================================

def check_insurance_eligibility(
    patient_id: str,
    service_type: str
) -> EligibilityResponse:
    """
    Check insurance eligibility for a patient and service type.
    
    Args:
        patient_id: Patient identifier
        service_type: Type of service to check eligibility for
    
    Returns:
        EligibilityResponse with coverage details
    """
    if config.agent_mode == "sandbox":
        # Check if patient has coverage
        if patient_id not in MOCK_COVERAGE:
            return EligibilityResponse(
                patient_id=patient_id,
                coverage_id="",
                is_eligible=False,
                status=CoverageStatus.CANCELLED,
                coverage_details=Coverage(
                    id="",
                    status=CoverageStatus.CANCELLED,
                    subscriber_id="",
                    beneficiary=patient_id,
                    payor="Unknown",
                    plan_name="No Coverage",
                    coverage_start=date.today()
                ),
                service_type=service_type,
                message="No active coverage found for this patient"
            )
        
        coverage = MOCK_COVERAGE[patient_id]
        is_eligible = coverage.status == CoverageStatus.ACTIVE
        
        message = "Patient is eligible for service" if is_eligible else \
                  f"Coverage status is {coverage.status.value}"
        
        return EligibilityResponse(
            patient_id=patient_id,
            coverage_id=coverage.id,
            is_eligible=is_eligible,
            status=coverage.status,
            coverage_details=coverage,
            service_type=service_type,
            message=message
        )
    else:
        # Production mode: would call actual eligibility verification API
        raise NotImplementedError("Production mode not implemented")

# ============================================================================
# API Function: find_available_slots
# ============================================================================

def find_available_slots(
    specialty: str,
    start_date: date,
    end_date: date,
    practitioner_name: Optional[str] = None
) -> FindSlotsOutput:
    """
    Find available appointment slots for a specialty and date range.
    
    Args:
        specialty: Medical specialty
        start_date: Start date for search
        end_date: End date for search
        practitioner_name: Optional specific practitioner
    
    Returns:
        FindSlotsOutput with available slots
    """
    if config.agent_mode == "sandbox":
        # Generate mock available slots
        slots = []
        
        # Get practitioners for specialty
        practitioners = MOCK_PRACTITIONERS.get(specialty.lower(), [])
        if not practitioners:
            return FindSlotsOutput(
                slots=[],
                total_count=0,
                specialty=specialty,
                date_range=f"{start_date} to {end_date}"
            )
        
        # Filter by practitioner name if specified
        if practitioner_name:
            practitioners = [
                p for p in practitioners 
                if practitioner_name.lower() in p["name"].lower()
            ]
        
        # Generate slots for each practitioner
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                for practitioner in practitioners:
                    # Generate 4 slots per day (9am, 11am, 2pm, 4pm)
                    for hour in [9, 11, 14, 16]:
                        slot_start = datetime.combine(current_date, datetime.min.time())
                        slot_start = slot_start.replace(hour=hour)
                        slot_end = slot_start + timedelta(minutes=30)
                        
                        slot = AppointmentSlot(
                            slot_id=f"SLOT-{uuid.uuid4().hex[:8]}",
                            start=slot_start,
                            end=slot_end,
                            practitioner_id=practitioner["id"],
                            practitioner_name=practitioner["name"],
                            specialty=specialty,
                            location="Main Hospital - Floor 3",
                            available=True
                        )
                        slots.append(slot)
            
            current_date += timedelta(days=1)
        
        return FindSlotsOutput(
            slots=slots[:20],  # Limit to first 20 slots
            total_count=len(slots),
            specialty=specialty,
            date_range=f"{start_date} to {end_date}"
        )
    else:
        # Production mode: would call actual scheduling API
        raise NotImplementedError("Production mode not implemented")

# ============================================================================
# API Function: book_appointment
# ============================================================================

def book_appointment(
    patient_id: str,
    slot_id: str,
    reason: Optional[str] = None,
    comment: Optional[str] = None
) -> BookAppointmentOutput:
    """
    Book an appointment for a patient in a specific slot.
    
    Args:
        patient_id: Patient identifier
        slot_id: Slot identifier to book
        reason: Reason for appointment
        comment: Additional comments
    
    Returns:
        BookAppointmentOutput with appointment details
    """
    if config.agent_mode == "sandbox":
        # Verify patient exists
        patient_exists = any(p.id == patient_id for p in MOCK_PATIENTS)
        if not patient_exists:
            return BookAppointmentOutput(
                appointment=None,
                confirmation_number="",
                success=False,
                message=f"Patient {patient_id} not found"
            )
        
        # Generate appointment from slot
        # In real implementation, would verify slot availability
        appointment_id = f"APT-{uuid.uuid4().hex[:8]}"
        confirmation_number = f"CONF-{uuid.uuid4().hex[:10].upper()}"
        
        # Create appointment (simplified - using mock data)
        appointment = Appointment(
            id=appointment_id,
            status=AppointmentStatus.BOOKED,
            service_type=reason or "Follow-up",
            specialty="cardiology",  # Would come from slot data
            description=reason,
            start=datetime.now() + timedelta(days=7),  # Mock: 7 days from now
            end=datetime.now() + timedelta(days=7, minutes=30),
            participant=[
                Participant(
                    actor_type="patient",
                    actor_id=patient_id,
                    required=True,
                    status="accepted"
                )
            ],
            location="Main Hospital - Floor 3",
            comment=comment
        )
        
        # Store appointment
        MOCK_APPOINTMENTS[appointment_id] = appointment
        
        return BookAppointmentOutput(
            appointment=appointment,
            confirmation_number=confirmation_number,
            success=True,
            message=f"Appointment successfully booked. Confirmation: {confirmation_number}"
        )
    else:
        # Production mode: would call actual booking API
        raise NotImplementedError("Production mode not implemented")

# ============================================================================
# Function Registry (for LLM function calling)
# ============================================================================

HEALTHCARE_FUNCTIONS = {
    "search_patient": {
        "function": search_patient,
        "description": "Search for patients by name, MRN (Medical Record Number), or phone number",
        "parameters": SearchPatientInput.schema(),
    },
    "check_insurance_eligibility": {
        "function": check_insurance_eligibility,
        "description": "Check if a patient has active insurance coverage for a specific service type",
        "parameters": CheckEligibilityInput.schema(),
    },
    "find_available_slots": {
        "function": find_available_slots,
        "description": "Find available appointment slots for a medical specialty within a date range",
        "parameters": FindSlotsInput.schema(),
    },
    "book_appointment": {
        "function": book_appointment,
        "description": "Book an appointment for a patient in a specific time slot",
        "parameters": BookAppointmentInput.schema(),
    },
}



