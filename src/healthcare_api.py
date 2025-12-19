"""Mock Healthcare API Functions

These functions simulate real healthcare API interactions.
In production, these would connect to actual EHR systems, scheduling systems, etc.

Each function has a JSON schema for the LLM to understand how to call it.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import random
from src.schemas import (
    Patient, InsuranceCoverage, AppointmentSlot, 
    Appointment, InsuranceStatus, AppointmentStatus
)


# Mock database (in production, this would be a real database)
MOCK_PATIENTS = {
    "P123456": {
        "id": "P123456",
        "name": "Ravi Kumar",
        "givenName": "Ravi",
        "familyName": "Kumar",
        "birthDate": "1985-03-15",
        "gender": "male",
        "phone": "+91-9876543210",
        "email": "ravi.kumar@example.com"
    },
    "P789012": {
        "id": "P789012",
        "name": "Priya Sharma",
        "givenName": "Priya",
        "familyName": "Sharma",
        "birthDate": "1990-07-22",
        "gender": "female",
        "phone": "+91-9988776655",
        "email": "priya.sharma@example.com"
    },
    "P345678": {
        "id": "P345678",
        "name": "Amit Patel",
        "givenName": "Amit",
        "familyName": "Patel",
        "birthDate": "1978-11-03",
        "gender": "male",
        "phone": "+91-9123456789",
        "email": "amit.patel@example.com"
    },
    "P111111": {
        "id": "P111111",
        "name": "Sundaram Iyer",
        "givenName": "Sundaram",
        "familyName": "Iyer",
        "birthDate": "1992-05-18",
        "gender": "male",
        "phone": "+91-9876543211",
        "email": "sundaram.iyer@example.com"
    },
    "P222222": {
        "id": "P222222",
        "name": "Lakshmi Menon",
        "givenName": "Lakshmi",
        "familyName": "Menon",
        "birthDate": "1987-09-25",
        "gender": "female",
        "phone": "+91-9876543212",
        "email": "lakshmi.menon@example.com"
    },
    "P333333": {
        "id": "P333333",
        "name": "Meera Devi",
        "givenName": "Meera",
        "familyName": "Devi",
        "birthDate": "1995-12-08",
        "gender": "female",
        "phone": "+91-9876543213",
        "email": "meera.devi@example.com"
    },
    "P444444": {
        "id": "P444444",
        "name": "Vijay Nair",
        "givenName": "Vijay",
        "familyName": "Nair",
        "birthDate": "1983-04-14",
        "gender": "male",
        "phone": "+91-9876543214",
        "email": "vijay.nair@example.com"
    },
    "P555555": {
        "id": "P555555",
        "name": "Anjali Reddy",
        "givenName": "Anjali",
        "familyName": "Reddy",
        "birthDate": "1991-08-30",
        "gender": "female",
        "phone": "+91-9876543215",
        "email": "anjali.reddy@example.com"
    },
    "P666666": {
        "id": "P666666",
        "name": "Murugan Pillai",
        "givenName": "Murugan",
        "familyName": "Pillai",
        "birthDate": "1989-02-22",
        "gender": "male",
        "phone": "+91-9876543216",
        "email": "murugan.pillai@example.com"
    },
    "P777777": {
        "id": "P777777",
        "name": "Anitha Krishnan",
        "givenName": "Anitha",
        "familyName": "Krishnan",
        "birthDate": "1993-06-11",
        "gender": "female",
        "phone": "+91-9876543217",
        "email": "anitha.krishnan@example.com"
    },
    "P888888": {
        "id": "P888888",
        "name": "Sekar Raman",
        "givenName": "Sekar",
        "familyName": "Raman",
        "birthDate": "1981-10-05",
        "gender": "male",
        "phone": "+91-9876543218",
        "email": "sekar.raman@example.com"
    },
    "P999999": {
        "id": "P999999",
        "name": "Kamala Venkatesh",
        "givenName": "Kamala",
        "familyName": "Venkatesh",
        "birthDate": "1994-01-19",
        "gender": "female",
        "phone": "+91-9876543219",
        "email": "kamala.venkatesh@example.com"
    },
    "P101010": {
        "id": "P101010",
        "name": "Rajesh Naidu",
        "givenName": "Rajesh",
        "familyName": "Naidu",
        "birthDate": "1986-07-27",
        "gender": "male",
        "phone": "+91-9876543220",
        "email": "rajesh.naidu@example.com"
    },
    "P202020": {
        "id": "P202020",
        "name": "Divya Gopal",
        "givenName": "Divya",
        "familyName": "Gopal",
        "birthDate": "1996-03-09",
        "gender": "female",
        "phone": "+91-9876543221",
        "email": "divya.gopal@example.com"
    },
    "P303030": {
        "id": "P303030",
        "name": "Suresh Iyengar",
        "givenName": "Suresh",
        "familyName": "Iyengar",
        "birthDate": "1984-11-16",
        "gender": "male",
        "phone": "+91-9876543222",
        "email": "suresh.iyengar@example.com"
    },
    "P404040": {
        "id": "P404040",
        "name": "Malathi Subramanian",
        "givenName": "Malathi",
        "familyName": "Subramanian",
        "birthDate": "1997-09-23",
        "gender": "female",
        "phone": "+91-9876543223",
        "email": "malathi.subramanian@example.com"
    },
    "P505050": {
        "id": "P505050",
        "name": "Karthik Narayanan",
        "givenName": "Karthik",
        "familyName": "Narayanan",
        "birthDate": "1988-05-31",
        "gender": "male",
        "phone": "+91-9876543224",
        "email": "karthik.narayanan@example.com"
    },
    "P606060": {
        "id": "P606060",
        "name": "Saranya Mohan",
        "givenName": "Saranya",
        "familyName": "Mohan",
        "birthDate": "1992-12-07",
        "gender": "female",
        "phone": "+91-9876543225",
        "email": "saranya.mohan@example.com"
    },
    "P707070": {
        "id": "P707070",
        "name": "Arjun Swamy",
        "givenName": "Arjun",
        "familyName": "Swamy",
        "birthDate": "1985-08-14",
        "gender": "male",
        "phone": "+91-9876543226",
        "email": "arjun.swamy@example.com"
    },
    "P808080": {
        "id": "P808080",
        "name": "Deepika Ravi",
        "givenName": "Deepika",
        "familyName": "Ravi",
        "birthDate": "1990-04-20",
        "gender": "female",
        "phone": "+91-9876543227",
        "email": "deepika.ravi@example.com"
    },
    "P909090": {
        "id": "P909090",
        "name": "Srinivasan Ganesh",
        "givenName": "Srinivasan",
        "familyName": "Ganesh",
        "birthDate": "1987-01-13",
        "gender": "male",
        "phone": "+91-9876543228",
        "email": "srinivasan.ganesh@example.com"
    }
}

MOCK_INSURANCE = {
    "P123456": {
        "id": "INS-001",
        "patientId": "P123456",
        "subscriberId": "SUB123456",
        "payer": "National Health Insurance",
        "planName": "Premium Care Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 500.0
    },
    "P789012": {
        "id": "INS-002",
        "patientId": "P789012",
        "subscriberId": "SUB789012",
        "payer": "Star Health Insurance",
        "planName": "Family Health Shield",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 1000.0
    },
    "P345678": {
        "id": "INS-003",
        "patientId": "P345678",
        "subscriberId": "SUB345678",
        "payer": "ICICI Lombard",
        "planName": "Complete Health Insurance",
        "status": "expired",
        "periodStart": "2024-01-01",
        "periodEnd": "2024-12-31",
        "copayAmount": 750.0
    },
    "P111111": {
        "id": "INS-004",
        "patientId": "P111111",
        "subscriberId": "SUB111111",
        "payer": "Blue Cross Blue Shield",
        "planName": "Gold Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 250.0
    },
    "P222222": {
        "id": "INS-005",
        "patientId": "P222222",
        "subscriberId": "SUB222222",
        "payer": "UnitedHealthcare",
        "planName": "Platinum Plus",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 300.0
    },
    "P333333": {
        "id": "INS-006",
        "patientId": "P333333",
        "subscriberId": "SUB333333",
        "payer": "Aetna",
        "planName": "Standard Health Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 400.0
    },
    "P444444": {
        "id": "INS-007",
        "patientId": "P444444",
        "subscriberId": "SUB444444",
        "payer": "Cigna",
        "planName": "Comprehensive Care",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 350.0
    },
    "P555555": {
        "id": "INS-008",
        "patientId": "P555555",
        "subscriberId": "SUB555555",
        "payer": "Humana",
        "planName": "Select Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 450.0
    },
    "P666666": {
        "id": "INS-009",
        "patientId": "P666666",
        "subscriberId": "SUB666666",
        "payer": "Kaiser Permanente",
        "planName": "Premium HMO",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 200.0
    },
    "P777777": {
        "id": "INS-010",
        "patientId": "P777777",
        "subscriberId": "SUB777777",
        "payer": "Medicaid",
        "planName": "State Health Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 0.0
    },
    "P888888": {
        "id": "INS-011",
        "patientId": "P888888",
        "subscriberId": "SUB888888",
        "payer": "Anthem",
        "planName": "Blue Advantage",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 275.0
    },
    "P999999": {
        "id": "INS-012",
        "patientId": "P999999",
        "subscriberId": "SUB999999",
        "payer": "Molina Healthcare",
        "planName": "Complete Care",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 150.0
    },
    "P101010": {
        "id": "INS-013",
        "patientId": "P101010",
        "subscriberId": "SUB101010",
        "payer": "Oscar Health",
        "planName": "Simple Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 325.0
    },
    "P202020": {
        "id": "INS-014",
        "patientId": "P202020",
        "subscriberId": "SUB202020",
        "payer": "Centene",
        "planName": "Wellcare Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 180.0
    },
    "P303030": {
        "id": "INS-015",
        "patientId": "P303030",
        "subscriberId": "SUB303030",
        "payer": "Blue Shield of California",
        "planName": "Gold Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 280.0
    },
    "P404040": {
        "id": "INS-016",
        "patientId": "P404040",
        "subscriberId": "SUB404040",
        "payer": "Medicare",
        "planName": "Medicare Advantage",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 100.0
    },
    "P505050": {
        "id": "INS-017",
        "patientId": "P505050",
        "subscriberId": "SUB505050",
        "payer": "Health Net",
        "planName": "Total Care",
        "status": "expired",
        "periodStart": "2024-01-01",
        "periodEnd": "2024-12-31",
        "copayAmount": 420.0
    },
    "P606060": {
        "id": "INS-018",
        "patientId": "P606060",
        "subscriberId": "SUB606060",
        "payer": "WellPoint",
        "planName": "Essential Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 375.0
    },
    "P707070": {
        "id": "INS-019",
        "patientId": "P707070",
        "subscriberId": "SUB707070",
        "payer": "Highmark",
        "planName": "Blue Cross Plan",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 310.0
    },
    "P808080": {
        "id": "INS-020",
        "patientId": "P808080",
        "subscriberId": "SUB808080",
        "payer": "Independence Blue Cross",
        "planName": "Personal Choice",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 290.0
    },
    "P909090": {
        "id": "INS-021",
        "patientId": "P909090",
        "subscriberId": "SUB909090",
        "payer": "CareSource",
        "planName": "Managed Care",
        "status": "active",
        "periodStart": "2025-01-01",
        "periodEnd": "2025-12-31",
        "copayAmount": 220.0
    }
}

MOCK_APPOINTMENTS = {}


class HealthcareAPI:
    """
    Mock Healthcare API with FHIR-compliant operations.
    
    In production, this would interface with:
    - Epic/Cerner EHR systems
    - Practice management systems
    - Insurance verification services
    - Scheduling platforms
    """
    
    @staticmethod
    def search_patient(name: Optional[str] = None, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for a patient by name or ID.
        
        Args:
            name: Patient name (partial match supported)
            patient_id: Exact patient ID
            
        Returns:
            Patient information or list of matching patients
        """
        if patient_id:
            patient_data = MOCK_PATIENTS.get(patient_id)
            if patient_data:
                patient = Patient(**patient_data)
                return {
                    "success": True,
                    "patient": patient.model_dump(by_alias=True, mode='json'),
                    "message": f"Found patient: {patient.name}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Patient with ID {patient_id} not found"
                }
        
        elif name:
            # Search by name (case-insensitive partial match)
            matches = []
            name_lower = name.lower()
            
            for patient_data in MOCK_PATIENTS.values():
                if name_lower in patient_data["name"].lower():
                    patient = Patient(**patient_data)
                    matches.append(patient.model_dump(by_alias=True, mode='json'))
            
            if matches:
                return {
                    "success": True,
                    "patients": matches,
                    "count": len(matches),
                    "message": f"Found {len(matches)} patient(s) matching '{name}'"
                }
            else:
                return {
                    "success": False,
                    "error": f"No patients found matching '{name}'"
                }
        
        else:
            return {
                "success": False,
                "error": "Either name or patient_id must be provided"
            }
    
    @staticmethod
    def check_insurance_eligibility(patient_id: str) -> Dict[str, Any]:
        """
        Check insurance eligibility and coverage for a patient.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Insurance coverage details
        """
        # First verify patient exists
        if patient_id not in MOCK_PATIENTS:
            return {
                "success": False,
                "error": f"Patient {patient_id} not found"
            }
        
        # Check insurance
        insurance_data = MOCK_INSURANCE.get(patient_id)
        
        if insurance_data:
            coverage = InsuranceCoverage(**insurance_data)
            
            # Determine eligibility
            is_eligible = coverage.status == InsuranceStatus.ACTIVE
            
            return {
                "success": True,
                "eligible": is_eligible,
                "coverage": coverage.model_dump(by_alias=True, mode='json'),
                "message": f"Insurance status: {coverage.status.value}"
            }
        else:
            return {
                "success": True,
                "eligible": False,
                "message": "No insurance coverage found for this patient"
            }
    
    @staticmethod
    def find_available_slots(
        specialty: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        provider_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find available appointment slots.
        
        Args:
            specialty: Medical specialty (e.g., cardiology, neurology)
            start_date: Search start date (ISO format)
            end_date: Search end date (ISO format)
            provider_id: Specific provider (optional)
            
        Returns:
            List of available time slots
        """
        # Parse dates
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                return {"success": False, "error": "Invalid start_date format"}
        else:
            start_dt = datetime.now()
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                return {"success": False, "error": "Invalid end_date format"}
        else:
            end_dt = start_dt + timedelta(days=7)
        
        # Generate mock available slots
        slots = []
        providers = {
            "cardiology": [
                {"id": "DR001", "name": "Dr. Sarah Johnson"},
                {"id": "DR002", "name": "Dr. Michael Chen"}
            ],
            "neurology": [
                {"id": "DR003", "name": "Dr. Emily Williams"},
                {"id": "DR004", "name": "Dr. David Brown"}
            ],
            "orthopedics": [
                {"id": "DR005", "name": "Dr. James Miller"},
                {"id": "DR006", "name": "Dr. Lisa Anderson"}
            ],
            "general": [
                {"id": "DR007", "name": "Dr. Robert Taylor"},
                {"id": "DR008", "name": "Dr. Jennifer White"}
            ]
        }
        
        specialty_lower = specialty.lower()
        provider_list = providers.get(specialty_lower, providers["general"])
        
        # Generate 5-10 random slots
        current_date = start_dt
        slot_count = 0
        
        while current_date <= end_dt and slot_count < 10:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                for hour in [9, 11, 14, 16]:  # Morning and afternoon slots
                    if random.random() > 0.3:  # 70% chance slot is available
                        provider = random.choice(provider_list)
                        
                        if provider_id and provider["id"] != provider_id:
                            continue
                        
                        slot_start = current_date.replace(
                            hour=hour, minute=0, second=0, microsecond=0
                        )
                        slot_end = slot_start + timedelta(minutes=30)
                        
                        slot = AppointmentSlot(
                            slotId=f"SLOT-{current_date.strftime('%Y%m%d')}-{hour:02d}-{provider['id']}",
                            specialty=specialty,
                            providerId=provider["id"],
                            providerName=provider["name"],
                            startTime=slot_start,
                            endTime=slot_end,
                            location=f"Clinic Building A, Room {random.randint(101, 350)}",
                            available=True
                        )
                        
                        slots.append(slot.model_dump(by_alias=True, mode='json'))
                        slot_count += 1
            
            current_date += timedelta(days=1)
        
        return {
            "success": True,
            "slots": slots,
            "count": len(slots),
            "message": f"Found {len(slots)} available slots for {specialty}"
        }
    
    @staticmethod
    def book_appointment(
        patient_id: str,
        slot_id: str,
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Book an appointment for a patient.
        
        Args:
            patient_id: Patient identifier
            slot_id: Selected slot identifier (e.g., "SLOT-20251222-11-DR001")
            reason: Reason for visit
            notes: Additional notes
            
        Returns:
            Booked appointment details
        """
        # Verify patient exists
        patient_data = MOCK_PATIENTS.get(patient_id)
        if not patient_data:
            return {
                "success": False,
                "error": f"Patient {patient_id} not found"
            }
        
        # Validate slot_id
        if not slot_id or slot_id.strip() == "":
            return {
                "success": False,
                "error": f"slot_id is required for booking appointment. Received: '{slot_id}'"
            }
        
        # Parse slot_id to extract slot information
        # Format: SLOT-YYYYMMDD-HH-PROVIDERID (e.g., SLOT-20251222-09-DR001)
        slot_info = None
        try:
            if isinstance(slot_id, str) and slot_id.startswith("SLOT-"):
                parts = slot_id.split("-")
                if len(parts) >= 4:
                    date_str = parts[1]  # YYYYMMDD
                    hour = int(parts[2])  # HH
                    provider_id = parts[3]  # PROVIDERID
                    
                    # Parse date and time
                    slot_date = datetime.strptime(date_str, "%Y%m%d")
                    slot_start = slot_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    slot_end = slot_start + timedelta(minutes=30)
                    
                    # Determine specialty and provider name from provider_id
                    specialty = "cardiology"  # Default
                    provider_name = "Dr. Sarah Johnson"  # Default
                    location = f"Clinic Building A, Room {random.randint(101, 350)}"
                    
                    # Map provider IDs to names and specialties
                    provider_map = {
                        "DR001": {"name": "Dr. Sarah Johnson", "specialty": "cardiology"},
                        "DR002": {"name": "Dr. Michael Chen", "specialty": "cardiology"},
                        "DR003": {"name": "Dr. Emily Williams", "specialty": "neurology"},
                        "DR004": {"name": "Dr. David Brown", "specialty": "neurology"},
                        "DR005": {"name": "Dr. James Miller", "specialty": "orthopedics"},
                        "DR006": {"name": "Dr. Lisa Anderson", "specialty": "orthopedics"},
                        "DR007": {"name": "Dr. Robert Taylor", "specialty": "general-practice"},
                        "DR008": {"name": "Dr. Jennifer White", "specialty": "general-practice"}
                    }
                    
                    if provider_id in provider_map:
                        provider_info = provider_map[provider_id]
                        provider_name = provider_info["name"]
                        specialty = provider_info["specialty"]
                    
                    slot_info = {
                        "start_time": slot_start,
                        "end_time": slot_end,
                        "provider_id": provider_id,
                        "provider_name": provider_name,
                        "specialty": specialty,
                        "location": location
                    }
        except Exception as e:
            # If slot_id parsing fails, log and use defaults
            import traceback
            print(f"       ⚠️  Slot ID parsing failed: {e}, slot_id: {slot_id}")
            print(f"       Traceback: {traceback.format_exc()}")
            slot_info = None
        
        # If slot_id couldn't be parsed, use defaults
        if not slot_info:
            appointment_time = datetime.now() + timedelta(days=random.randint(1, 7))
            slot_info = {
                "start_time": appointment_time,
                "end_time": appointment_time + timedelta(minutes=30),
                "provider_id": "DR001",
                "provider_name": "Dr. Sarah Johnson",
                "specialty": "cardiology",
                "location": "Clinic Building A, Room 205"
            }
        
        # Create appointment
        appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            # Validate slot_info before creating appointment
            if not slot_info.get("start_time") or not slot_info.get("end_time"):
                return {
                    "success": False,
                    "error": "Invalid slot information: missing start_time or end_time"
                }
            
            # Ensure datetime objects are datetime instances
            start_time = slot_info["start_time"]
            end_time = slot_info["end_time"]
            
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            # Create appointment
            appointment = Appointment(
                id=appointment_id,
                status=AppointmentStatus.BOOKED,
                patientId=patient_id,
                patientName=patient_data["name"],
                providerId=slot_info["provider_id"],
                providerName=slot_info["provider_name"],
                specialty=slot_info["specialty"],
                startTime=start_time,
                endTime=end_time,
                location=slot_info["location"],
                reason=reason or "General consultation",
                notes=notes
            )
            
            # Store appointment
            appointment_dict = appointment.model_dump(by_alias=True, mode='json')
            MOCK_APPOINTMENTS[appointment_id] = appointment_dict
            
            return {
                "success": True,
                "appointment": appointment_dict,
                "message": f"Appointment booked successfully for {patient_data['name']}"
            }
        except ValueError as ve:
            # Pydantic validation error
            import traceback
            error_details = traceback.format_exc()
            print(f"       ❌ Appointment validation error: {str(ve)}")
            print(f"       Error details: {error_details}")
            return {
                "success": False,
                "error": f"Validation error: {str(ve)}"
            }
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"       ❌ Appointment creation error: {str(e)}")
            print(f"       Error type: {type(e).__name__}")
            print(f"       Error details: {error_details}")
            return {
                "success": False,
                "error": f"Failed to create appointment: {str(e)}"
            }


# Function schemas for LLM (OpenAI-style function calling)
FUNCTION_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_patient",
            "description": "Search for a patient by name or patient ID. Use this to find patient records before booking appointments or checking eligibility.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Patient name (supports partial matching, case-insensitive)"
                    },
                    "patient_id": {
                        "type": "string",
                        "description": "Exact patient ID (e.g., P123456)"
                    }
                },
                "oneOf": [
                    {"required": ["name"]},
                    {"required": ["patient_id"]}
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_insurance_eligibility",
            "description": "Check insurance eligibility and coverage details for a patient. Returns insurance status, payer information, and copay amount.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier (required)"
                    }
                },
                "required": ["patient_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_available_slots",
            "description": "Find available appointment time slots for a specific medical specialty. Returns a list of available slots with provider and location details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "specialty": {
                        "type": "string",
                        "description": "Medical specialty (e.g., cardiology, neurology, orthopedics, general)",
                        "enum": ["cardiology", "neurology", "orthopedics", "pediatrics", "general", "dermatology"]
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for search (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                        "format": "date-time"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for search (ISO format)",
                        "format": "date-time"
                    },
                    "provider_id": {
                        "type": "string",
                        "description": "Specific provider ID (optional)"
                    }
                },
                "required": ["specialty"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for a patient in a specific time slot. This creates a confirmed appointment in the system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier"
                    },
                    "slot_id": {
                        "type": "string",
                        "description": "Selected appointment slot ID from find_available_slots"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the visit"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Additional notes or special requirements"
                    }
                },
                "required": ["patient_id", "slot_id"]
            }
        }
    }
]

