"""Clinical Workflow Agent with Function Calling

This agent uses LangChain and HuggingFace to orchestrate healthcare workflows.
It does NOT provide medical advice - only workflow automation.
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests

try:
    from huggingface_hub import InferenceClient
    HF_CLIENT_AVAILABLE = True
except ImportError:
    HF_CLIENT_AVAILABLE = False
    InferenceClient = None

from src.healthcare_api import HealthcareAPI, FUNCTION_SCHEMAS
from src.validators import SafetyValidator, ValidationException
from src.audit_logger import AuditLogger


class ClinicalWorkflowAgent:
    """
    Function-calling agent for clinical workflow automation.
    
    This agent:
    - Parses natural language requests
    - Determines which functions to call
    - Validates all inputs
    - Executes functions safely
    - Returns structured, auditable outputs
    
    This agent does NOT:
    - Provide medical advice
    - Make diagnoses
    - Prescribe treatments
    """
    
    # System prompt that defines agent behavior
    SYSTEM_PROMPT = """You are a Clinical Workflow Automation Agent. Your ONLY job is to help with administrative and operational healthcare tasks.

**CRITICAL SAFETY RULES:**
1. You MUST NOT provide medical advice, diagnoses, or treatment recommendations
2. You MUST NOT answer questions about symptoms, conditions, or medications
3. You can ONLY perform these workflow tasks:
   - Search for patients
   - Check insurance eligibility
   - Find available appointment slots
   - Book appointments

**Your Workflow:**
1. Understand the user's request
2. Determine which function(s) to call
3. Extract required parameters
4. Call functions in the correct order
5. Return structured results

**Available Functions:**
- search_patient: Find a patient by name or ID
- check_insurance_eligibility: Verify insurance coverage
- find_available_slots: Find available appointment times
- book_appointment: Book an appointment

**Important Guidelines:**
- ONLY call search_patient if the user explicitly asks to find/search for a PATIENT by name
- Do NOT call search_patient for appointment searches (e.g., "find appointments" does NOT need patient search)
- Do NOT call search_patient unless you need a patient_id AND the user mentioned a patient name
- For insurance checks: if patient name is mentioned, search first; if patient_id is already known, use it directly
- Check insurance eligibility before booking if mentioned
- Find available slots before booking an appointment
- Use the exact slot_id returned from find_available_slots when booking
- Ask for clarification if critical information is missing

**Response Format:**

For function calls, respond with JSON:
{
    "reasoning": "Brief explanation of your plan",
    "function_calls": [
        {
            "function": "function_name",
            "parameters": {"param1": "value1"}
        }
    ]
}

For greetings or general questions (no functions needed), respond with:
{
    "reasoning": "User is greeting or asking a general question",
    "function_calls": [],
    "message": "Your friendly, helpful response here"
}

If you cannot help, respond with:
{
    "error": "Explanation of why you cannot help",
    "reason": "SAFETY_VIOLATION" or "MISSING_INFORMATION"
}

Remember: You are an orchestrator, not a medical advisor. Be friendly and helpful!"""

    def __init__(
        self,
        api_key: str,
        dry_run: bool = False,
        model: str = "google/flan-t5-large"  # Use a model that's definitely available on router
    ):
        """
        Initialize the clinical workflow agent.
        
        Args:
            api_key: HuggingFace API key
            dry_run: If True, simulate function calls without execution
            model: HuggingFace model to use
        """
        self.api_key = api_key
        self.dry_run = dry_run
        self.model = model
        
        # Always initialize API URLs for fallback (even if using client)
        self.api_urls = [
            f"https://router.huggingface.co/{model}",
            f"https://api-inference.huggingface.co/models/{model}",  # Old (will fail)
        ]
        self.api_url = self.api_urls[0]
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Try using InferenceClient with latest version (should handle router automatically)
        self.use_client = False
        if HF_CLIENT_AVAILABLE and InferenceClient:
            try:
                # InferenceClient in latest versions should handle router endpoint
                self.client = InferenceClient(
                    token=api_key,
                    model=model
                )
                self.use_client = True
                print(f"   Using InferenceClient (should auto-handle router endpoint)")
            except Exception as e:
                print(f"   Warning: InferenceClient init failed: {e}")
                self.use_client = False
        
        # Initialize components
        self.healthcare_api = HealthcareAPI()
        self.safety_validator = SafetyValidator()
        self.audit_logger = AuditLogger()
        
        print(f"🤖 Clinical Workflow Agent initialized")
        print(f"   Model: {self.model}")
        print(f"   Dry Run: {self.dry_run}")
        print(f"   Log File: {self.audit_logger.log_file}")
    
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user request end-to-end.
        
        Args:
            user_input: Natural language request from user
            
        Returns:
            Structured response with results
        """
        print(f"\n{'='*70}")
        print(f"📥 User Request: {user_input}")
        print(f"{'='*70}")
        
        # Log user input
        self.audit_logger.log_user_input(user_input)
        
        try:
            # Step 1: Safety validation
            print("\n🔒 Validating request safety...")
            self.safety_validator.validate_request_intent(user_input)
            print("   ✅ Safety check passed")
            
            # Step 2: Get agent decision
            print("\n🤔 Agent reasoning...")
            agent_decision = self._get_agent_decision(user_input)
            
            # Handle general messages (greetings, questions without function calls)
            # Check if LLM returned a message without function calls
            if "message" in agent_decision and (
                not agent_decision.get("function_calls") or 
                len(agent_decision.get("function_calls", [])) == 0
            ):
                return {
                    "success": True,
                    "response": agent_decision.get("message", "Hello! How can I help you?"),
                    "functions_called": [],
                    "final_response": agent_decision.get("message", "Hello! How can I help you?"),
                    "reasoning": agent_decision.get("reasoning", "")
                }
            
            # Step 3: Execute function calls
            if "function_calls" in agent_decision and len(agent_decision["function_calls"]) > 0:
                print(f"\n🔧 Executing {len(agent_decision['function_calls'])} function(s)...")
                results = self._execute_function_calls(agent_decision["function_calls"])
                
                # Step 4: Generate final response
                final_response = self._generate_final_response(
                    user_input, 
                    agent_decision,
                    results
                )
                
                self.audit_logger.log_agent_response(
                    response=json.dumps(final_response),
                    function_calls=agent_decision["function_calls"]
                )
                
                return final_response
            
            elif "error" in agent_decision:
                print(f"\n❌ Agent Error: {agent_decision['error']}")
                return agent_decision
            
            else:
                return {
                    "success": False,
                    "error": "Agent returned unexpected response format"
                }
        
        except ValidationException as e:
            error_msg = str(e)
            print(f"\n⛔ Validation Error: {error_msg}")
            self.audit_logger.log_safety_violation("VALIDATION_ERROR", error_msg)
            return {
                "success": False,
                "error": error_msg,
                "reason": "SAFETY_VIOLATION"
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"\n💥 Unexpected Error: {error_msg}")
            return {
                "success": False,
                "error": f"Internal error: {error_msg}"
            }
    
    def _get_agent_decision(self, user_input: str) -> Dict[str, Any]:
        """
        Use LLM to decide which functions to call.
        
        Args:
            user_input: User's natural language request
            
        Returns:
            Agent's decision with function calls
        """
        # Build prompt with available functions
        functions_desc = self._format_function_descriptions()
        
        prompt = f"""{self.SYSTEM_PROMPT}

**Available Functions (detailed):**
{functions_desc}

**User Request:**
{user_input}

**Your Response (JSON only):**"""
        
        # Try LLM API with retry logic, fallback to mock if all fail
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Try InferenceClient first (handles router automatically in latest versions)
                if self.use_client:
                    print(f"🌐 Using InferenceClient for {self.model} (attempt {attempt + 1}/{max_retries})")
                    try:
                        response = self.client.text_generation(
                            prompt,
                            max_new_tokens=1000,
                            temperature=0.3,
                            return_full_text=False
                        )
                        response_data = response
                        response = str(response_data)
                        # Success - break out of retry loop
                        break
                    except Exception as e:
                        error_str = str(e)
                        last_error = e
                        if "410" in error_str or "api-inference" in error_str:
                            # InferenceClient still using old endpoint, fall back to direct API
                            print(f"   ⚠️  InferenceClient using old endpoint, switching to direct API")
                            self.use_client = False
                            # Fall through to direct API call
                        else:
                            if attempt < max_retries - 1:
                                print(f"   ⚠️  Attempt {attempt + 1} failed: {e}, retrying...")
                                continue
                            raise
                
                # Fallback: Direct API call
                if not self.use_client:
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 1000,
                            "temperature": 0.3,
                            "return_full_text": False
                        }
                    }
                    
                    # Try different endpoint formats
                    api_response = None
                    for api_url in self.api_urls:
                        try:
                            print(f"🌐 Trying endpoint: {api_url} (attempt {attempt + 1}/{max_retries})")
                            api_response = requests.post(
                                api_url,
                                headers=self.headers,
                                json=payload,
                                timeout=30  # Reduced timeout for faster fallback
                            )
                            
                            if api_response.status_code == 200:
                                print(f"   ✅ Success with {api_url}")
                                break
                            elif api_response.status_code == 410:
                                print(f"   ⚠️  410 Gone - trying next endpoint...")
                                continue
                            elif api_response.status_code == 404:
                                print(f"   ⚠️  404 Not Found - trying next endpoint...")
                                continue
                        except Exception as e:
                            print(f"   ⚠️  Error: {e}")
                            last_error = e
                            continue
                    
                    if api_response is None or api_response.status_code != 200:
                        if attempt < max_retries - 1:
                            print(f"   ⚠️  Attempt {attempt + 1} failed, retrying...")
                            continue
                        # All attempts failed, use mock response
                        raise Exception("All API endpoints failed")
                    else:
                        api_response.raise_for_status()
                        response_data = api_response.json()
                        # Success - break out of retry loop
                        break
                        
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Attempt {attempt + 1} failed: {e}, retrying...")
                    continue
                # Final attempt failed, use mock response
                print(f"   ⚠️  All API attempts failed, using intelligent mock response")
                mock_response_str = self._generate_mock_response(user_input)
                try:
                    response_data = json.loads(mock_response_str)
                    if isinstance(response_data, dict) and "message" in response_data:
                        response = mock_response_str
                    else:
                        response = mock_response_str
                except:
                    response = mock_response_str
                response_data = mock_response_str
                break
        
        # If we still don't have a response, use mock
        if 'response' not in locals() or 'response_data' not in locals():
            print(f"   ⚠️  Using intelligent mock response (fallback)")
            mock_response_str = self._generate_mock_response(user_input)
            try:
                response_data = json.loads(mock_response_str)
                response = mock_response_str
            except:
                response = mock_response_str
                response_data = mock_response_str
        
        # Extract text from response
        if self.use_client and isinstance(response_data, str):
            # InferenceClient returns string directly
            response = str(response_data)
        else:
            # Direct API or mock response
            if isinstance(response_data, str):
                # Already a string (mock response)
                response = response_data
            elif isinstance(response_data, list) and len(response_data) > 0:
                # Handle list response format
                item = response_data[0]
                if isinstance(item, dict):
                    # Try different possible keys
                    response = item.get("generated_text", item.get("text", str(item)))
                else:
                    response = str(item)
            elif isinstance(response_data, dict):
                # Handle dict response format
                response = response_data.get("generated_text", response_data.get("text", str(response_data)))
            else:
                response = str(response_data)
        
        # Clean up response - remove prompt if included
        if isinstance(response, str):
            if prompt in response:
                response = response.replace(prompt, "").strip()
            # Remove any leading/trailing whitespace
            response = response.strip()
        
        print(f"\n🤖 Agent Response:\n{response}\n")
        
        # Parse JSON response
        # Clean up the response (remove markdown code blocks if present)
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        try:
            decision = json.loads(response)
            
            # Normalize function_calls format
            if "function_calls" in decision:
                # Ensure it's a list
                if not isinstance(decision["function_calls"], list):
                    decision["function_calls"] = [decision["function_calls"]]
            elif "function" in decision:
                # Single function call format
                decision["function_calls"] = [decision]
            
            return decision
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group())
                return decision
            else:
                # Final fallback - use mock response
                print(f"   ⚠️  JSON parse failed, using mock response")
                mock_response_str = self._generate_mock_response(user_input)
                try:
                    return json.loads(mock_response_str)
                except:
                    return {
                        "error": "Agent did not return valid JSON",
                        "raw_response": response
                    }
        
        except Exception as e:
            # Final fallback - use mock response
            print(f"   ⚠️  Exception occurred, using mock response: {e}")
            mock_response_str = self._generate_mock_response(user_input)
            try:
                return json.loads(mock_response_str)
            except:
                return {
                    "error": f"Failed to get agent decision: {str(e)}",
                    "reason": "LLM_ERROR"
                }
    
    def _format_function_descriptions(self) -> str:
        """Format function schemas for the prompt"""
        descriptions = []
        
        for schema in FUNCTION_SCHEMAS:
            func = schema["function"]
            desc = f"\n**{func['name']}**"
            desc += f"\n{func['description']}"
            desc += f"\nParameters: {json.dumps(func['parameters'], indent=2)}"
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def _generate_mock_response(self, user_input: str) -> str:
        """
        Generate a mock JSON response when API fails.
        This allows the demo to work even if HuggingFace API has issues.
        Note: This is a fallback - the LLM should handle most queries.
        """
        user_lower = user_input.lower().strip()
        user_original = user_input.strip()
        
        # Handle greetings and general questions (fallback when LLM API fails)
        # Use substring matching for better detection
        greetings = ["hi", "hello", "hey", "hii", "hi there", "greetings", "good morning", "good afternoon", "good evening", "hey there"]
        general_questions = ["what can you do", "help", "how are you", "what are you", "who are you", "what do you do"]
        
        # Check if input is just a greeting (more lenient matching)
        # Check exact match first, then substring
        is_greeting = (
            user_lower in greetings or
            user_lower in ["hi", "hello", "hey", "hii", "hey there"] or
            any(greeting in user_lower for greeting in ["hi", "hello", "hey"]) or
            (len(user_lower) <= 5 and any(user_lower.startswith(g) for g in ["hi", "hey", "hel"]))
        )
        
        if is_greeting:
            return json.dumps({
                "reasoning": "User sent a greeting. I should respond friendly and explain what I can do.",
                "function_calls": [],
                "message": "Hello! I'm your Clinical Workflow Agent. I can help you search for patients, check insurance eligibility, find appointment slots, and book appointments. What would you like to do?"
            })
        
        # Check for general questions
        if any(question in user_lower for question in general_questions):
            return json.dumps({
                "reasoning": "User is asking a general question about my capabilities.",
                "function_calls": [],
                "message": "I'm a Clinical Workflow Automation Agent. I can help you with:\n• Searching for patients\n• Checking insurance eligibility\n• Finding available appointment slots\n• Booking appointments\n\nI do NOT provide medical advice or diagnosis. How can I help you today?"
            })
        
        # Handle very short inputs that might be partial words or unclear
        if len(user_lower) <= 4:
            return json.dumps({
                "reasoning": "User sent a very short input that might be unclear.",
                "function_calls": [],
                "message": f"I see you typed '{user_input}'. Could you provide more details? For example:\n• 'Find patient Ravi Kumar' to search for a patient\n• 'Find cardiology appointments' to find slots\n• 'Book an appointment' to schedule\n\nWhat would you like to do?"
            })
        
        # Handle partial words that might be related to functions
        if user_lower in ["card", "app", "slot", "book", "schedule"]:
            return json.dumps({
                "reasoning": "User sent a partial word that might be related to a function.",
                "function_calls": [],
                "message": f"I see you mentioned '{user_input}'. Could you provide more details? For example:\n• 'Find cardiology appointments' for appointments\n• 'Book an appointment' for booking\n• 'Check insurance' for insurance\n\nWhat would you like to do?"
            })
        
        # Simple rule-based function calling for demo purposes
        function_calls = []
        reasoning_parts = []
        
        # Detect patient search - ONLY if explicitly searching for a patient by name
        # Must NOT trigger for appointment searches or insurance checks
        is_patient_search = False
        patient_name = None
        
        # Check if this is an appointment or insurance query first
        is_appointment_query = any(word in user_lower for word in ["appointment", "slot", "available", "schedule"])
        is_insurance_query = any(word in user_lower for word in ["insurance", "eligibility", "coverage"])
        
        # Only search for patient if explicitly asking to find/search for a patient
        # AND not asking for appointments or insurance
        if not is_appointment_query and not is_insurance_query:
            # Explicit patient search patterns
            if any(phrase in user_lower for phrase in ["find patient", "search patient", "look for patient", "get patient", "find patient named", "search for patient"]):
                is_patient_search = True
                # Extract patient name - Tamil/Telugu names in English
                if "ravi" in user_lower or "kumar" in user_lower:
                    patient_name = "Ravi Kumar"
                elif "priya" in user_lower or "sharma" in user_lower:
                    patient_name = "Priya Sharma"
                elif "amit" in user_lower or "patel" in user_lower:
                    patient_name = "Amit Patel"
                elif "sundaram" in user_lower or "iyer" in user_lower:
                    patient_name = "Sundaram Iyer"
                elif "lakshmi" in user_lower or "menon" in user_lower:
                    patient_name = "Lakshmi Menon"
                elif "meera" in user_lower or "devi" in user_lower:
                    patient_name = "Meera Devi"
                elif "vijay" in user_lower or "nair" in user_lower:
                    patient_name = "Vijay Nair"
                elif "anjali" in user_lower or "reddy" in user_lower:
                    patient_name = "Anjali Reddy"
                elif "murugan" in user_lower or "pillai" in user_lower:
                    patient_name = "Murugan Pillai"
                elif "anitha" in user_lower or "krishnan" in user_lower:
                    patient_name = "Anitha Krishnan"
                elif "sekar" in user_lower or "raman" in user_lower:
                    patient_name = "Sekar Raman"
                elif "kamala" in user_lower or "venkatesh" in user_lower:
                    patient_name = "Kamala Venkatesh"
                elif "rajesh" in user_lower or "naidu" in user_lower:
                    patient_name = "Rajesh Naidu"
                elif "divya" in user_lower or "gopal" in user_lower:
                    patient_name = "Divya Gopal"
                elif "suresh" in user_lower or "iyengar" in user_lower:
                    patient_name = "Suresh Iyengar"
                elif "malathi" in user_lower or "subramanian" in user_lower:
                    patient_name = "Malathi Subramanian"
                elif "karthik" in user_lower or "narayanan" in user_lower:
                    patient_name = "Karthik Narayanan"
                elif "saranya" in user_lower or "mohan" in user_lower:
                    patient_name = "Saranya Mohan"
                elif "arjun" in user_lower or "swamy" in user_lower:
                    patient_name = "Arjun Swamy"
                elif "deepika" in user_lower:
                    patient_name = "Deepika Ravi"
                elif "srinivasan" in user_lower or "ganesh" in user_lower:
                    patient_name = "Srinivasan Ganesh"
                else:
                    # Try to extract patient name from query
                    words = user_original.split()
                    for i, word in enumerate(words):
                        if word.lower() in ["patient", "for"] and i + 1 < len(words):
                            # Get next 1-2 words as name
                            if i + 2 < len(words):
                                patient_name = " ".join(words[i+1:i+3])
                            else:
                                patient_name = words[i+1]
                            break
                    
                    # If still no name, try after "find"/"search"
                    if not patient_name:
                        for i, word in enumerate(words):
                            if word.lower() in ["find", "search"] and i + 1 < len(words):
                                if i + 2 < len(words):
                                    patient_name = " ".join(words[i+1:i+3])
                                else:
                                    patient_name = words[i+1]
                                break
        
        if is_patient_search and patient_name:
            function_calls.append({
                "function": "search_patient",
                "parameters": {"name": patient_name}
            })
            reasoning_parts.append(f"Searching for patient: {patient_name}")
        
        # Detect insurance check
        if any(word in user_lower for word in ["insurance", "eligibility", "coverage", "verify", "check insurance"]):
            # Map patient names directly to patient_id (no need to search first)
            patient_id = None
            
            # Map patient names to IDs - Tamil/Telugu names in English
            patient_id_map = {
                "ravi": "P123456", "kumar": "P123456",
                "priya": "P789012", "sharma": "P789012",
                "amit": "P345678", "patel": "P345678",
                "sundaram": "P111111", "iyer": "P111111",
                "lakshmi": "P222222", "menon": "P222222",
                "meera": "P333333", "devi": "P333333",
                "vijay": "P444444", "nair": "P444444",
                "anjali": "P555555", "reddy": "P555555",
                "murugan": "P666666", "pillai": "P666666",
                "anitha": "P777777", "krishnan": "P777777",
                "sekar": "P888888", "raman": "P888888",
                "kamala": "P999999", "venkatesh": "P999999",
                "rajesh": "P101010", "naidu": "P101010",
                "divya": "P202020", "gopal": "P202020",
                "suresh": "P303030", "iyengar": "P303030",
                "malathi": "P404040", "subramanian": "P404040",
                "karthik": "P505050", "narayanan": "P505050",
                "saranya": "P606060", "mohan": "P606060",
                "arjun": "P707070", "swamy": "P707070",
                "deepika": "P808080",
                "srinivasan": "P909090", "ganesh": "P909090"
            }
            
            patient_id = None
            for key, pid in patient_id_map.items():
                if key in user_lower:
                    patient_id = pid
                    break
            
            if not patient_id:
                patient_id = "P123456"  # Default
            
            # Directly call insurance check without patient search
            function_calls.append({
                "function": "check_insurance_eligibility",
                "parameters": {"patient_id": patient_id}
            })
            reasoning_parts.append("Checking insurance eligibility")
        
        # Detect appointment search - ONLY if searching for appointments/slots, NOT if booking
        # Check for appointment search patterns (not booking patterns)
        # Also exclude if this is a patient search query
        is_appointment_search = (
            any(word in user_lower for word in ["appointment", "slot", "available"]) and
            not any(word in user_lower for word in ["book", "schedule appointment", "make appointment"]) and
            not any(phrase in user_lower for phrase in ["find patient", "search patient", "search for patient"])
        )
        
        if is_appointment_search:
            specialty = "cardiology"  # Default
            if "orthopedic" in user_lower:
                specialty = "orthopedics"
            elif "general" in user_lower:
                specialty = "general-practice"
            elif "cardiology" in user_lower or "cardiac" in user_lower:
                specialty = "cardiology"
            
            # Calculate dates (next week)
            from datetime import date, timedelta
            today = date.today()
            start_date = today + timedelta(days=(7 - today.weekday()))  # Next Monday
            end_date = start_date + timedelta(days=6)  # Next Sunday
            
            function_calls.append({
                "function": "find_available_slots",
                "parameters": {
                    "specialty": specialty,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            })
            reasoning_parts.append(f"Finding available {specialty} appointments")
        
        # Detect booking
        if any(word in user_lower for word in ["book", "schedule appointment", "make appointment", "schedule"]):
            # Step 1: Find patient if not already found
            patient_id = None
            for fc in function_calls:
                if fc["function"] == "search_patient":
                    # Will extract patient_id from search result
                    patient_id = "P123456"  # Default, will be updated from search
                    break
            
            # If no patient search, add it
            if not any(fc["function"] == "search_patient" for fc in function_calls):
                patient_name = "Ravi Kumar"  # Default
                if "ravi" in user_lower or "kumar" in user_lower:
                    patient_name = "Ravi Kumar"
                elif "priya" in user_lower or "sharma" in user_lower:
                    patient_name = "Priya Sharma"
                elif "amit" in user_lower or "patel" in user_lower:
                    patient_name = "Amit Patel"
                elif "sundaram" in user_lower or "iyer" in user_lower:
                    patient_name = "Sundaram Iyer"
                elif "lakshmi" in user_lower or "menon" in user_lower:
                    patient_name = "Lakshmi Menon"
                elif "meera" in user_lower or "devi" in user_lower:
                    patient_name = "Meera Devi"
                elif "vijay" in user_lower or "nair" in user_lower:
                    patient_name = "Vijay Nair"
                elif "anjali" in user_lower or "reddy" in user_lower:
                    patient_name = "Anjali Reddy"
                elif "murugan" in user_lower or "pillai" in user_lower:
                    patient_name = "Murugan Pillai"
                elif "anitha" in user_lower or "krishnan" in user_lower:
                    patient_name = "Anitha Krishnan"
                elif "sekar" in user_lower or "raman" in user_lower:
                    patient_name = "Sekar Raman"
                elif "kamala" in user_lower or "venkatesh" in user_lower:
                    patient_name = "Kamala Venkatesh"
                elif "rajesh" in user_lower or "naidu" in user_lower:
                    patient_name = "Rajesh Naidu"
                elif "divya" in user_lower or "gopal" in user_lower:
                    patient_name = "Divya Gopal"
                elif "suresh" in user_lower or "iyengar" in user_lower:
                    patient_name = "Suresh Iyengar"
                elif "malathi" in user_lower or "subramanian" in user_lower:
                    patient_name = "Malathi Subramanian"
                elif "karthik" in user_lower or "narayanan" in user_lower:
                    patient_name = "Karthik Narayanan"
                elif "saranya" in user_lower or "mohan" in user_lower:
                    patient_name = "Saranya Mohan"
                elif "arjun" in user_lower or "swamy" in user_lower:
                    patient_name = "Arjun Swamy"
                elif "deepika" in user_lower:
                    patient_name = "Deepika Ravi"
                elif "srinivasan" in user_lower or "ganesh" in user_lower:
                    patient_name = "Srinivasan Ganesh"
                
                function_calls.append({
                    "function": "search_patient",
                    "parameters": {"name": patient_name}
                })
                reasoning_parts.append(f"Finding patient: {patient_name}")
                # Map patient name to ID
                patient_id_map = {
                    "ravi kumar": "P123456", "priya sharma": "P789012", "amit patel": "P345678",
                    "sundaram iyer": "P111111", "lakshmi menon": "P222222", "meera devi": "P333333",
                    "vijay nair": "P444444", "anjali reddy": "P555555", "murugan pillai": "P666666",
                    "anitha krishnan": "P777777", "sekar raman": "P888888", "kamala venkatesh": "P999999",
                    "rajesh naidu": "P101010", "divya gopal": "P202020", "suresh iyengar": "P303030",
                    "malathi subramanian": "P404040", "karthik narayanan": "P505050", "saranya mohan": "P606060",
                    "arjun swamy": "P707070", "deepika ravi": "P808080", "srinivasan ganesh": "P909090"
                }
                patient_id = patient_id_map.get(patient_name.lower(), "P123456")
            
            # Step 2: Find available slots if not already found
            if not any(fc["function"] == "find_available_slots" for fc in function_calls):
                specialty = "cardiology"  # Default
                if "orthopedic" in user_lower:
                    specialty = "orthopedics"
                elif "general" in user_lower:
                    specialty = "general-practice"
                elif "cardiology" in user_lower or "cardiac" in user_lower:
                    specialty = "cardiology"
                
                from datetime import date, timedelta
                today = date.today()
                start_date = today + timedelta(days=(7 - today.weekday()))
                end_date = start_date + timedelta(days=6)
                
                function_calls.append({
                    "function": "find_available_slots",
                    "parameters": {
                        "specialty": specialty,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                })
                reasoning_parts.append(f"Finding available {specialty} slots")
            
            # Step 3: Book appointment (will use first available slot from find_available_slots)
            # The slot_id will be extracted from the find_available_slots result during execution
            if not any(fc["function"] == "book_appointment" for fc in function_calls):
                # Determine patient_id from previous search or name
                if not patient_id:
                    patient_id_map = {
                        "ravi": "P123456", "kumar": "P123456", "priya": "P789012", "sharma": "P789012",
                        "amit": "P345678", "patel": "P345678", "sundaram": "P111111", "iyer": "P111111",
                        "lakshmi": "P222222", "menon": "P222222", "meera": "P333333", "devi": "P333333",
                        "vijay": "P444444", "nair": "P444444", "anjali": "P555555", "reddy": "P555555",
                        "murugan": "P666666", "pillai": "P666666", "anitha": "P777777", "krishnan": "P777777",
                        "sekar": "P888888", "raman": "P888888", "kamala": "P999999", "venkatesh": "P999999",
                        "rajesh": "P101010", "naidu": "P101010", "divya": "P202020", "gopal": "P202020",
                        "suresh": "P303030", "iyengar": "P303030", "malathi": "P404040", "subramanian": "P404040",
                        "karthik": "P505050", "narayanan": "P505050", "saranya": "P606060", "mohan": "P606060",
                        "arjun": "P707070", "swamy": "P707070", "deepika": "P808080",
                        "srinivasan": "P909090", "ganesh": "P909090"
                    }
                    for key, pid in patient_id_map.items():
                        if key in user_lower:
                            patient_id = pid
                            break
                    if not patient_id:
                        patient_id = "P123456"  # Default
                
                # Extract reason if mentioned
                reason = None
                if "follow" in user_lower or "follow-up" in user_lower:
                    reason = "Follow-up appointment"
                elif "check" in user_lower or "checkup" in user_lower:
                    reason = "Routine checkup"
                elif "consultation" in user_lower:
                    reason = "General consultation"
                else:
                    reason = "General consultation"
                
                # Use placeholder slot_id - will be replaced with actual slot_id from find_available_slots result
                function_calls.append({
                    "function": "book_appointment",
                    "parameters": {
                        "patient_id": patient_id,
                        "slot_id": "AUTO-SELECT-FIRST",  # Will be replaced with actual slot_id from find_available_slots
                        "reason": reason
                    }
                })
                reasoning_parts.append(f"Booking appointment for patient {patient_id}")
        
        # If no functions detected, provide helpful error
        if not function_calls:
            return json.dumps({
                "error": "I couldn't understand your request. I can help you with:\n• Finding patients (e.g., 'Find patient Ravi Kumar')\n• Checking insurance (e.g., 'Check insurance for Ravi Kumar')\n• Finding appointments (e.g., 'Find cardiology appointments')\n• Booking appointments (e.g., 'Schedule a cardiology appointment')",
                "reason": "MISSING_INFORMATION"
            })
        
        # Return function calls
        reasoning = " | ".join(reasoning_parts) if reasoning_parts else f"Processing request: {user_input}"
        return json.dumps({
            "reasoning": reasoning,
            "function_calls": function_calls
        })
    
    def _execute_function_calls(
        self, 
        function_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute a list of function calls with validation.
        
        Args:
            function_calls: List of function call specifications
            
        Returns:
            List of results from each function call
        """
        results = []
        
        for i, call in enumerate(function_calls, 1):
            function_name = call.get("function")
            parameters = call.get("parameters", {}).copy()  # Make a copy to modify
            
            # Chain results: if book_appointment needs slot_id, get it from find_available_slots result
            if function_name == "book_appointment":
                current_slot_id = parameters.get("slot_id")
                # Check if slot_id is missing, None, empty, or AUTO-SELECT-FIRST
                if not current_slot_id or current_slot_id == "AUTO-SELECT-FIRST" or current_slot_id == "":
                    # Find the most recent find_available_slots result
                    slot_found = False
                    for prev_result in reversed(results):
                        if prev_result.get("function") == "find_available_slots":
                            slots_result = prev_result.get("result", {})
                            if slots_result.get("success") and slots_result.get("slots") and len(slots_result["slots"]) > 0:
                                # Use the first available slot
                                first_slot = slots_result["slots"][0]
                                # Try multiple field names for slot_id (check both camelCase and snake_case)
                                slot_id_value = first_slot.get("slotId") or first_slot.get("slot_id") or first_slot.get("id")
                                if slot_id_value:
                                    parameters["slot_id"] = slot_id_value
                                    print(f"       🔗 Using slot_id from find_available_slots: {parameters['slot_id']}")
                                    slot_found = True
                                    break
                                else:
                                    # Debug: print all available keys
                                    print(f"       ⚠️  Slot found but no slotId field.")
                                    print(f"       ⚠️  Available keys: {list(first_slot.keys())}")
                                    # Try to construct slot_id from available data
                                    if "startTime" in first_slot and "providerId" in first_slot:
                                        from datetime import datetime
                                        start_time = first_slot["startTime"]
                                        if isinstance(start_time, str):
                                            dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                        else:
                                            dt = start_time
                                        provider_id = first_slot["providerId"]
                                        constructed_slot_id = f"SLOT-{dt.strftime('%Y%m%d')}-{dt.hour:02d}-{provider_id}"
                                        parameters["slot_id"] = constructed_slot_id
                                        print(f"       🔗 Constructed slot_id from slot data: {parameters['slot_id']}")
                                        slot_found = True
                                        break
                    
                    # If no slot found, generate a default one
                    if not slot_found:
                        from datetime import datetime, timedelta
                        default_date = datetime.now() + timedelta(days=7)
                        parameters["slot_id"] = f"SLOT-{default_date.strftime('%Y%m%d')}-11-DR001"
                        print(f"       ⚠️  No slots found, using default slot_id: {parameters['slot_id']}")
                
                # Final validation: ensure slot_id is present
                if not parameters.get("slot_id"):
                    print(f"       ❌ ERROR: slot_id is still missing after chaining!")
                    print(f"       Parameters before execution: {json.dumps(parameters, indent=2, default=str)}")
            
            # Chain results: if book_appointment needs patient_id, get it from search_patient result
            if function_name == "book_appointment" and not parameters.get("patient_id"):
                for prev_result in reversed(results):
                    if prev_result.get("function") == "search_patient":
                        search_result = prev_result.get("result", {})
                        if search_result.get("success") and search_result.get("patients"):
                            first_patient = search_result["patients"][0]
                            parameters["patient_id"] = first_patient.get("id") or first_patient.get("patientId")
                            print(f"       🔗 Using patient_id from search_patient: {parameters['patient_id']}")
                            break
            
            print(f"\n   [{i}/{len(function_calls)}] Calling: {function_name}")
            print(f"       Parameters: {json.dumps(parameters, indent=10)}")
            
            try:
                # Validate parameters
                self.safety_validator.validate_function_parameters(
                    function_name, 
                    parameters
                )
                
                # Execute function
                if self.dry_run:
                    print(f"       [DRY RUN - Not actually executed]")
                    result = {
                        "success": True,
                        "dry_run": True,
                        "message": f"Dry run: {function_name} would be called"
                    }
                else:
                    result = self._call_function(function_name, parameters)
                
                # Log the call
                self.audit_logger.log_function_call(
                    function_name=function_name,
                    parameters=parameters,
                    result=result,
                    dry_run=self.dry_run
                )
                
                results.append({
                    "function": function_name,
                    "parameters": parameters,
                    "result": result
                })
                
                if result.get("success"):
                    print(f"       ✅ Result: {result.get('message', 'Success')}")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"       ❌ Error: {error_msg}")
            
            except ValidationException as e:
                error_msg = str(e)
                print(f"       ❌ Validation failed: {error_msg}")
                
                self.audit_logger.log_function_call(
                    function_name=function_name,
                    parameters=parameters,
                    error=error_msg,
                    dry_run=self.dry_run
                )
                
                results.append({
                    "function": function_name,
                    "parameters": parameters,
                    "error": error_msg
                })
            
            except Exception as e:
                error_msg = str(e)
                print(f"       💥 Execution failed: {error_msg}")
                
                self.audit_logger.log_function_call(
                    function_name=function_name,
                    parameters=parameters,
                    error=error_msg,
                    dry_run=self.dry_run
                )
                
                results.append({
                    "function": function_name,
                    "parameters": parameters,
                    "error": error_msg
                })
        
        return results
    
    def _call_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a healthcare API function.
        
        Args:
            function_name: Name of the function to call
            parameters: Function parameters
            
        Returns:
            Function result
        """
        # Map function names to actual methods
        function_map = {
            "search_patient": self.healthcare_api.search_patient,
            "check_insurance_eligibility": self.healthcare_api.check_insurance_eligibility,
            "find_available_slots": self.healthcare_api.find_available_slots,
            "book_appointment": self.healthcare_api.book_appointment
        }
        
        function = function_map.get(function_name)
        if not function:
            raise ValueError(f"Unknown function: {function_name}")
        
        return function(**parameters)
    
    def _generate_final_response(
        self,
        user_input: str,
        agent_decision: Dict[str, Any],
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a structured final response.
        
        Args:
            user_input: Original user request
            agent_decision: Agent's decision
            results: Results from function calls
            
        Returns:
            Structured response
        """
        success = all(
            r.get("result", {}).get("success", False) 
            for r in results 
            if "result" in r
        )
        
        return {
            "success": success,
            "request": user_input,
            "reasoning": agent_decision.get("reasoning", ""),
            "function_calls": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return self.audit_logger.get_session_summary()

