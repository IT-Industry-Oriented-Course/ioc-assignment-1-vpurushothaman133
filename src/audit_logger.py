"""Audit logging system for compliance and traceability.

All function calls, parameters, and results are logged for regulatory compliance.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager

from src.schemas import FunctionCallLog


class AuditLogger:
    """
    Comprehensive audit logging for all agent actions.
    
    Logs are written in JSON Lines format for easy parsing and analysis.
    Each log entry is immutable and timestamped.
    """
    
    def __init__(self, log_dir: str = "logs", session_id: Optional[str] = None):
        """
        Initialize the audit logger.
        
        Args:
            log_dir: Directory to store log files
            session_id: Unique session identifier
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.session_id = session_id or self._generate_session_id()
        self.log_file = self.log_dir / f"audit_{self.session_id}.jsonl"
        
        # Create session log file
        self._initialize_log_file()
    
    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _initialize_log_file(self):
        """Initialize the log file with session metadata"""
        try:
            metadata = {
                "event_type": "session_start",
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            # Convert Path to string for Windows compatibility
            log_file_path = str(self.log_file)
            
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metadata) + '\n')
        except Exception as e:
            print(f"Warning: Could not initialize log file {self.log_file}: {e}")
            # Continue without logging if file operations fail
    
    def log_function_call(
        self,
        function_name: str,
        parameters: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        dry_run: bool = False,
        user_id: Optional[str] = None
    ):
        """
        Log a function call with all details.
        
        Args:
            function_name: Name of the function called
            parameters: Input parameters
            result: Function result (if successful)
            error: Error message (if failed)
            dry_run: Whether this was a dry run
            user_id: User who initiated the call
        """
        log_entry = FunctionCallLog(
            timestamp=datetime.now(),
            function_name=function_name,
            parameters=parameters,
            result=result,
            error=error,
            dry_run=dry_run,
            user_id=user_id,
            session_id=self.session_id
        )
        
        # Write to log file
        try:
            # Convert Path to string for Windows compatibility
            log_file_path = str(self.log_file)
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_entry.model_dump_json() + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file {self.log_file}: {e}")
            # Continue without logging if file operations fail
        
        # Also write to console in development
        self._log_to_console(log_entry)
    
    def _log_to_console(self, log_entry: FunctionCallLog):
        """Print log entry to console with formatting"""
        status = "✅ SUCCESS" if log_entry.result else "❌ ERROR" if log_entry.error else "⏳ CALL"
        dry_run_label = " [DRY RUN]" if log_entry.dry_run else ""
        
        print(f"\n{'='*70}")
        print(f"[{log_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {status}{dry_run_label}")
        print(f"Function: {log_entry.function_name}")
        print(f"Parameters: {json.dumps(log_entry.parameters, indent=2)}")
        
        if log_entry.result:
            print(f"Result: {json.dumps(log_entry.result, indent=2, default=str)}")
        
        if log_entry.error:
            print(f"Error: {log_entry.error}")
        
        print('='*70)
    
    def log_user_input(self, user_input: str, intent: Optional[str] = None):
        """Log user input for audit trail"""
        log_entry = {
            "event_type": "user_input",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "input": user_input,
            "intent": intent
        }
        
        try:
            log_file_path = str(self.log_file)
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Warning: Could not write user input to log file: {e}")
    
    def log_agent_response(self, response: str, function_calls: Optional[list] = None):
        """Log agent response"""
        log_entry = {
            "event_type": "agent_response",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "response": response,
            "function_calls": function_calls or []
        }
        
        try:
            log_file_path = str(self.log_file)
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Warning: Could not write agent response to log file: {e}")
    
    def log_safety_violation(self, violation_type: str, details: str):
        """Log safety violations for compliance"""
        log_entry = {
            "event_type": "safety_violation",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "violation_type": violation_type,
            "details": details
        }
        
        try:
            log_file_path = str(self.log_file)
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Warning: Could not write safety violation to log file: {e}")
        
        print(f"\n⚠️  SAFETY VIOLATION LOGGED: {violation_type}")
        print(f"Details: {details}\n")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the current session"""
        total_calls = 0
        successful_calls = 0
        failed_calls = 0
        dry_runs = 0
        
        try:
            log_file_path = str(self.log_file)
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get('function_name'):
                            total_calls += 1
                            if entry.get('dry_run'):
                                dry_runs += 1
                            if entry.get('result'):
                                successful_calls += 1
                            elif entry.get('error'):
                                failed_calls += 1
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        
        return {
            "session_id": self.session_id,
            "log_file": str(self.log_file),
            "total_function_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "dry_runs": dry_runs
        }
    
    @contextmanager
    def function_call_context(
        self,
        function_name: str,
        parameters: Dict[str, Any],
        dry_run: bool = False
    ):
        """
        Context manager for function calls with automatic logging.
        
        Usage:
            with logger.function_call_context('search_patient', params) as ctx:
                result = search_patient(**params)
                ctx.set_result(result)
        """
        class FunctionContext:
            def __init__(self, logger_instance):
                self.logger = logger_instance
                self.result = None
                self.error = None
            
            def set_result(self, result):
                self.result = result
            
            def set_error(self, error):
                self.error = error
        
        ctx = FunctionContext(self)
        
        try:
            yield ctx
        except Exception as e:
            ctx.error = str(e)
            raise
        finally:
            self.log_function_call(
                function_name=function_name,
                parameters=parameters,
                result=ctx.result,
                error=ctx.error,
                dry_run=dry_run
            )

