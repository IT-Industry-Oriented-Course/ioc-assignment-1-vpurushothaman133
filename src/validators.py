"""Input validation and safety checks for the clinical agent.

This module ensures all inputs are validated before any API calls are made.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import ValidationError


class ValidationException(Exception):
    """Custom exception for validation errors"""
    pass


class SafetyValidator:
    """Validates inputs for safety and compliance"""
    
    # Prohibited patterns that indicate medical advice requests
    PROHIBITED_PATTERNS = [
        r'\bdiagnos(e|is)\b',
        r'\btreat(ment)?\b',
        r'\bprescri(be|ption)\b',
        r'\bmedication\b',
        r'\bdrug\b',
        r'\bwhat (is|are) (my|the) (symptoms?|condition\??)',
        r'\bshould i take\b',
        r'\bis it (safe|dangerous)\b',
        r'\bcan i (take|use)\b',
    ]
    
    @staticmethod
    def validate_patient_name(name: str) -> bool:
        """Validate patient name format"""
        if not name or len(name.strip()) < 2:
            raise ValidationException("Patient name must be at least 2 characters")
        
        if len(name) > 200:
            raise ValidationException("Patient name exceeds maximum length")
        
        # Check for suspicious patterns
        if re.search(r'[<>{}[\]\\]', name):
            raise ValidationException("Patient name contains invalid characters")
        
        return True
    
    @staticmethod
    def validate_patient_id(patient_id: str) -> bool:
        """Validate patient ID format"""
        if not patient_id or len(patient_id.strip()) == 0:
            raise ValidationException("Patient ID cannot be empty")
        
        # Basic format check (alphanumeric, dashes, underscores)
        if not re.match(r'^[A-Za-z0-9_-]+$', patient_id):
            raise ValidationException("Patient ID contains invalid characters")
        
        return True
    
    @staticmethod
    def validate_specialty(specialty: str) -> bool:
        """Validate medical specialty"""
        valid_specialties = [
            "cardiology", "neurology", "orthopedics", "pediatrics",
            "dermatology", "psychiatry", "oncology", "general",
            "internal_medicine", "surgery", "radiology", "pathology"
        ]
        
        if specialty.lower() not in valid_specialties:
            raise ValidationException(
                f"Invalid specialty. Must be one of: {', '.join(valid_specialties)}"
            )
        
        return True
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Validate date range for appointments"""
        if start_date >= end_date:
            raise ValidationException("Start date must be before end date")
        
        # Cannot book appointments in the past (with 1 hour grace period)
        if start_date < datetime.now() - timedelta(hours=1):
            raise ValidationException("Cannot book appointments in the past")
        
        # Limit appointment scheduling to 1 year in advance
        if start_date > datetime.now() + timedelta(days=365):
            raise ValidationException("Cannot book appointments more than 1 year in advance")
        
        return True
    
    @staticmethod
    def validate_request_intent(user_input: str) -> bool:
        """
        Validate that the user request is for workflow automation,
        NOT medical advice.
        """
        input_lower = user_input.lower()
        
        # Check for prohibited medical advice patterns
        for pattern in SafetyValidator.PROHIBITED_PATTERNS:
            if re.search(pattern, input_lower, re.IGNORECASE):
                raise ValidationException(
                    "⛔ SAFETY VIOLATION: This agent cannot provide medical advice, "
                    "diagnosis, or treatment recommendations. "
                    "Please consult a licensed healthcare provider."
                )
        
        return True
    
    @staticmethod
    def validate_function_parameters(
        function_name: str, 
        parameters: Dict[str, Any]
    ) -> bool:
        """Validate parameters for a specific function"""
        
        validators = {
            "search_patient": lambda p: (
                SafetyValidator.validate_patient_name(p["name"]) if "name" in p and p.get("name")
                else SafetyValidator.validate_patient_id(p["patient_id"]) if "patient_id" in p and p.get("patient_id")
                else (_ for _ in ()).throw(ValidationException("Either name or patient_id must be provided"))
            ),
            "check_insurance_eligibility": lambda p: SafetyValidator.validate_patient_id(
                p.get("patient_id", "")
            ),
            "find_available_slots": lambda p: SafetyValidator.validate_specialty(
                p.get("specialty", "")
            ),
            "book_appointment": lambda p: (
                SafetyValidator.validate_patient_id(p.get("patient_id", "")) and
                (True if p.get("slot_id") else (_ for _ in ()).throw(ValidationException("slot_id is required for booking")))
            ),
        }
        
        validator_func = validators.get(function_name)
        if validator_func:
            try:
                return validator_func(parameters)
            except ValidationException:
                raise
            except Exception as e:
                raise ValidationException(f"Parameter validation failed: {str(e)}")
        
        return True


class SchemaValidator:
    """Validates data against Pydantic schemas"""
    
    @staticmethod
    def validate_against_schema(data: Dict[str, Any], schema_class) -> Any:
        """
        Validate data against a Pydantic model
        
        Args:
            data: Dictionary to validate
            schema_class: Pydantic model class
            
        Returns:
            Validated instance of the schema
            
        Raises:
            ValidationException: If validation fails
        """
        try:
            return schema_class(**data)
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error['loc'])
                msg = error['msg']
                error_messages.append(f"{field}: {msg}")
            
            raise ValidationException(
                f"Schema validation failed:\n" + "\n".join(error_messages)
            )

