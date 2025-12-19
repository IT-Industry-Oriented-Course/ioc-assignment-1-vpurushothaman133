"""Command-Line Interface for the Clinical Workflow Agent

Provides an interactive interface for healthcare professionals to interact
with the agent.
"""

import os
import sys
import json
from typing import Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich library not available - using basic output")

from src.agent import ClinicalWorkflowAgent


class ClinicalAgentCLI:
    """Interactive CLI for the Clinical Workflow Agent"""
    
    def __init__(self, agent: ClinicalWorkflowAgent):
        """
        Initialize the CLI.
        
        Args:
            agent: Initialized ClinicalWorkflowAgent instance
        """
        self.agent = agent
        
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
    
    def print(self, message: str, style: Optional[str] = None):
        """Print with optional rich formatting"""
        if self.console and style:
            self.console.print(message, style=style)
        else:
            print(message)
    
    def print_panel(self, content: str, title: str, style: str = "cyan"):
        """Print a panel with rich formatting"""
        if self.console:
            self.console.print(Panel(content, title=title, border_style=style))
        else:
            print(f"\n{'='*70}")
            print(f"{title}")
            print('='*70)
            print(content)
            print('='*70)
    
    def print_welcome(self):
        """Print welcome message"""
        welcome_text = """
🏥 Clinical Workflow Automation Agent

This agent helps with administrative healthcare tasks:
  • Patient search
  • Insurance eligibility verification
  • Appointment scheduling
  • Slot availability checking

⚠️  IMPORTANT: This agent does NOT provide medical advice,
   diagnoses, or treatment recommendations.

Type 'help' for example commands, or 'quit' to exit.
"""
        if self.console:
            self.console.print(Panel(
                welcome_text,
                title="Welcome",
                border_style="green",
                box=box.DOUBLE
            ))
        else:
            print(welcome_text)
    
    def print_help(self):
        """Print help information with examples"""
        help_text = """
**Example Commands:**

1. **Search for a patient:**
   "Find patient Ravi Kumar"
   "Search for patient with ID P123456"

2. **Check insurance:**
   "Check insurance eligibility for Ravi Kumar"
   "Verify coverage for patient P123456"

3. **Find appointment slots:**
   "Find cardiology appointments next week"
   "Show available neurology slots"

4. **Book appointment:**
   "Schedule a cardiology follow-up for patient Ravi Kumar next week and check insurance"
   "Book appointment for patient P123456 in cardiology"

**Special Commands:**
  • help - Show this help message
  • summary - Show session summary
  • quit/exit - Exit the application
  • dry-run [on/off] - Toggle dry-run mode

**Dry-Run Mode:**
When enabled, the agent will show what it would do without actually
executing the actions. Useful for testing and validation.
"""
        if self.console:
            md = Markdown(help_text)
            self.console.print(Panel(md, title="Help & Examples", border_style="yellow"))
        else:
            print(help_text)
    
    def print_summary(self):
        """Print session summary"""
        summary = self.agent.get_session_summary()
        
        if self.console:
            table = Table(title="Session Summary", box=box.ROUNDED)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Session ID", summary["session_id"])
            table.add_row("Log File", str(summary["log_file"]))
            table.add_row("Total Function Calls", str(summary["total_function_calls"]))
            table.add_row("Successful Calls", str(summary["successful_calls"]))
            table.add_row("Failed Calls", str(summary["failed_calls"]))
            table.add_row("Dry Runs", str(summary["dry_runs"]))
            
            self.console.print(table)
        else:
            print("\n" + "="*70)
            print("Session Summary")
            print("="*70)
            for key, value in summary.items():
                print(f"{key}: {value}")
            print("="*70)
    
    def print_response(self, response: dict):
        """Print agent response in a formatted way"""
        if not self.console:
            print("\n" + json.dumps(response, indent=2, default=str))
            return
        
        # Check if it's an error response
        if not response.get("success", True):
            self.console.print(Panel(
                f"❌ {response.get('error', 'Unknown error')}",
                title="Error",
                border_style="red"
            ))
            return
        
        # Build formatted response
        output = []
        
        if response.get("reasoning"):
            output.append(f"**Reasoning:** {response['reasoning']}\n")
        
        # Show results
        results = response.get("results", [])
        if results:
            output.append(f"**Executed {len(results)} function(s):**\n")
            
            for i, result in enumerate(results, 1):
                func_name = result.get("function", "unknown")
                output.append(f"\n{i}. **{func_name}**")
                
                if "error" in result:
                    output.append(f"   ❌ Error: {result['error']}")
                elif "result" in result:
                    res = result["result"]
                    
                    if res.get("success"):
                        output.append(f"   ✅ {res.get('message', 'Success')}")
                        
                        # Add specific details based on function
                        if func_name == "search_patient" and "patient" in res:
                            p = res["patient"]
                            output.append(f"      • Name: {p.get('name')}")
                            output.append(f"      • ID: {p.get('id')}")
                            output.append(f"      • Phone: {p.get('phone', 'N/A')}")
                        
                        elif func_name == "search_patient" and "patients" in res:
                            output.append(f"      • Found {res['count']} patient(s)")
                            for p in res["patients"][:3]:  # Show max 3
                                output.append(f"        - {p.get('name')} (ID: {p.get('id')})")
                        
                        elif func_name == "check_insurance_eligibility":
                            eligible = res.get("eligible", False)
                            status_icon = "✅" if eligible else "❌"
                            output.append(f"      • Eligible: {status_icon}")
                            if "coverage" in res:
                                cov = res["coverage"]
                                output.append(f"      • Payer: {cov.get('payer')}")
                                output.append(f"      • Plan: {cov.get('planName')}")
                                output.append(f"      • Copay: ${cov.get('copayAmount', 0):.2f}")
                        
                        elif func_name == "find_available_slots":
                            slots = res.get("slots", [])
                            output.append(f"      • Found {len(slots)} available slot(s)")
                            for slot in slots[:3]:  # Show max 3
                                start_time = slot.get("startTime", "")
                                provider = slot.get("providerName", "")
                                output.append(f"        - {start_time}: {provider}")
                                output.append(f"          Slot ID: {slot.get('slotId')}")
                        
                        elif func_name == "book_appointment" and "appointment" in res:
                            apt = res["appointment"]
                            output.append(f"      • Appointment ID: {apt.get('id')}")
                            output.append(f"      • Provider: {apt.get('providerName')}")
                            output.append(f"      • Time: {apt.get('startTime')}")
                            output.append(f"      • Location: {apt.get('location')}")
                    else:
                        output.append(f"   ❌ {res.get('error', 'Failed')}")
        
        if response.get("dry_run"):
            output.append("\n⚠️  **DRY RUN MODE** - No actual changes were made")
        
        md = Markdown("\n".join(output))
        self.console.print(Panel(
            md,
            title="Response",
            border_style="green",
            box=box.ROUNDED
        ))
    
    def run(self):
        """Run the interactive CLI loop"""
        self.print_welcome()
        
        while True:
            try:
                # Get user input
                if self.console:
                    user_input = self.console.input("\n[bold cyan]You:[/bold cyan] ").strip()
                else:
                    user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit']:
                    self.print("\n👋 Goodbye! Check your logs for audit trail.", style="yellow")
                    self.print_summary()
                    break
                
                elif user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                elif user_input.lower() == 'summary':
                    self.print_summary()
                    continue
                
                elif user_input.lower().startswith('dry-run'):
                    parts = user_input.split()
                    if len(parts) > 1:
                        mode = parts[1].lower()
                        if mode in ['on', 'true', '1']:
                            self.agent.dry_run = True
                            self.print("✅ Dry-run mode enabled", style="green")
                        elif mode in ['off', 'false', '0']:
                            self.agent.dry_run = False
                            self.print("✅ Dry-run mode disabled", style="green")
                        else:
                            self.print("❌ Use 'dry-run on' or 'dry-run off'", style="red")
                    else:
                        status = "enabled" if self.agent.dry_run else "disabled"
                        self.print(f"Dry-run mode is currently {status}", style="cyan")
                    continue
                
                # Process the request
                response = self.agent.process_request(user_input)
                
                # Display the response
                self.print_response(response)
            
            except KeyboardInterrupt:
                self.print("\n\n👋 Interrupted. Goodbye!", style="yellow")
                self.print_summary()
                break
            
            except Exception as e:
                self.print(f"\n💥 Unexpected error: {str(e)}", style="red")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point for the CLI"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    dry_run = os.getenv("DRY_RUN_MODE", "false").lower() in ["true", "1", "yes"]
    
    if not api_key:
        print("❌ Error: HUGGINGFACE_API_KEY not found in environment")
        print("Please set it in your .env file or as an environment variable")
        sys.exit(1)
    
    # Parse command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python -m src.cli [--dry-run]")
            print("\nOptions:")
            print("  --dry-run    Enable dry-run mode (simulate without executing)")
            print("  -h, --help   Show this help message")
            sys.exit(0)
        elif sys.argv[1] == "--dry-run":
            dry_run = True
    
    # Initialize agent
    try:
        agent = ClinicalWorkflowAgent(
            api_key=api_key,
            dry_run=dry_run
        )
        
        # Create and run CLI
        cli = ClinicalAgentCLI(agent)
        cli.run()
    
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

