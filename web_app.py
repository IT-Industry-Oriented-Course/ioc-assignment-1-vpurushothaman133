"""
Flask Web Application for Clinical Workflow Agent
Provides a web-based UI for testing the agent
"""
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime, date
import uuid

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.agent import ClinicalWorkflowAgent

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
CORS(app)

# Initialize agent
agent = None

def init_agent():
    """Initialize the agent with API key"""
    global agent
    api_key = os.getenv("HUGGINGFACE_API_KEY", "purushoth_api_key")
    try:
        agent = ClinicalWorkflowAgent(
            api_key=api_key,
            model="google/flan-t5-large",  # Using a model that works with router endpoint
            dry_run=False
        )
        print("✓ Agent initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}")
        return False

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the user"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'}), 400
            
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Empty message'}), 400
        
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not initialized. Please restart the server.'}), 500
        
        # Process the message through the agent
        response = agent.process_request(user_message)
        
        # Ensure all date objects are serialized to strings
        def serialize_dates(obj):
            """Recursively convert date/datetime objects to ISO strings"""
            try:
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, date):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: serialize_dates(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_dates(item) for item in obj]
                return obj
            except Exception as e:
                print(f"Warning: Error serializing date object: {e}")
                return str(obj)
        
        response = serialize_dates(response)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in /api/chat: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'details': error_details if app.debug else None
        }), 500

@app.route('/meta.json', methods=['GET'])
def meta():
    """Meta information endpoint (fixes 404)"""
    return jsonify({
        'name': 'Clinical Workflow Agent',
        'version': '1.0.0'
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'agent_ready': agent is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent audit logs"""
    try:
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            return jsonify({'logs': []})
        
        # Get the most recent log file (supports both .json and .jsonl)
        log_files = [f for f in os.listdir(logs_dir) if f.startswith('audit_') and (f.endswith('.json') or f.endswith('.jsonl'))]
        if not log_files:
            return jsonify({'logs': []})
        
        # Sort by modification time
        log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)
        
        # Read the most recent log file
        log_file_path = os.path.join(logs_dir, log_files[0])
        
        # Handle JSONL format (one JSON object per line)
        logs = []
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                if log_file_path.endswith('.jsonl'):
                    # Read JSONL format
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                logs.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
                else:
                    # Read JSON format
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
        except Exception as e:
            print(f"Error reading log file: {e}")
            return jsonify({'logs': [], 'error': str(e)})
        
        return jsonify({'logs': logs[-10:]})  # Return last 10 entries
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in /api/logs: {error_details}")
        return jsonify({'error': str(e), 'details': error_details}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Clinical Workflow Automation Agent - Web Interface")
    print("=" * 60)
    print()
    
    # Initialize the agent
    if init_agent():
        print()
        print("🌐 Starting web server...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print()
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    else:
        print("❌ Failed to initialize agent. Please check your configuration.")
        sys.exit(1)

