#!/usr/bin/env python3
"""
Flask API server for The Talking Heads UI
Serves the React app and provides API endpoints for the frontend
"""

import os
import sys
from pathlib import Path
import threading
import uuid
from datetime import datetime

# Fix Windows Unicode encoding
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from flask import Flask, jsonify, request, send_from_directory, make_response
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("[WARN] flask-cors not installed. CORS will not work properly.")
import yaml
import json

# Add project root to path
# In Docker, server.py is at /app/server.py, but project is mounted at /workspace
if Path('/workspace').exists():
    project_root = Path('/workspace')
else:
    project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.pipeline import Pipeline
from src.core.script_parser import ScriptParser
from src.utils.config_loader import load_config

app = Flask(__name__, static_folder='build', static_url_path='')
# Configure CORS - Use ONLY manual headers (Flask-CORS disabled to avoid conflicts)
# Flask-CORS can interfere with manual headers, so we handle everything manually
print("[INFO] Using manual CORS headers (Flask-CORS disabled)")

# ALWAYS add CORS headers to ALL responses
@app.after_request
def add_cors_headers_always(response):
    # CRITICAL: Set CORS headers on EVERY response, including errors
    try:
        # Debug: Log when headers are added
        origin = request.headers.get('Origin', 'none')
        path = request.path
        method = request.method
        print(f"[CORS DEBUG] Adding headers to {method} {path} (Origin: {origin})")
        
        # CRITICAL: Set headers BEFORE any other operations
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Type'
        response.headers['Access-Control-Max-Age'] = '3600'
        
        # Verify headers were set
        print(f"[CORS DEBUG] Headers set: Allow-Origin={response.headers.get('Access-Control-Allow-Origin')}, Status={response.status_code}")
    except Exception as e:
        # If there's an error, log it but don't fail the request
        print(f"[CORS ERROR] Failed to add CORS headers: {e}")
        import traceback
        traceback.print_exc()
    return response

# Handle OPTIONS preflight requests explicitly BEFORE route handlers
# CRITICAL: This must run FIRST to catch all OPTIONS requests
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        print(f"[CORS DEBUG] before_request handling OPTIONS for {request.path}")
        # Create response with CORS headers
        response = make_response()
        response.status_code = 200
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        print(f"[CORS DEBUG] before_request OPTIONS response: Allow-Origin={response.headers.get('Access-Control-Allow-Origin')}")
        return response

# Configuration
API_PORT = int(os.getenv('UI_API_PORT', 8001))  # Use 8001 to avoid conflicts with exponis-local (8000)
REACT_PORT = 3001  # Use 3001 to avoid conflicts with exponis-local (3000)
SCRIPTS_DIR = project_root / 'examples' / 'scripts'
PERSONAS_CONFIG = project_root / 'config' / 'personas.yaml'
CONFIG_FILE = project_root / 'config' / 'config.yaml'
PROGRESS_LOG = project_root / '.cache' / 'progress.log'

# Job storage for async video generation (thread-safe)
generation_jobs = {}  # {job_id: {'status': 'processing'|'completed'|'failed', 'progress': 0-100, 'log': [], 'error': None, 'video_path': None}}
generation_jobs_lock = threading.Lock()

# Load base config
try:
    base_config = load_config(CONFIG_FILE)
except Exception as e:
    print(f"Warning: Could not load config: {e}")
    base_config = {}

# API Routes

@app.route('/api/scripts', methods=['GET'])
def get_scripts():
    """Get list of available scripts."""
    scripts = []
    if SCRIPTS_DIR.exists():
        for script_file in SCRIPTS_DIR.glob('*.txt'):
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse script to get metadata
                parser = ScriptParser()
                parsed = parser.parse(content)
                
                scripts.append({
                    'filename': script_file.name,
                    'name': script_file.stem.replace('_', ' ').title(),
                    'path': str(script_file.relative_to(project_root)),
                    'modified': datetime.fromtimestamp(script_file.stat().st_mtime).isoformat(),
                    'segments': len(parsed.segments),
                    'personas': list(parsed.personas),
                    'preview': content[:200] + '...' if len(content) > 200 else content,
                    'content': content,
                })
            except Exception as e:
                print(f"Error reading script {script_file.name}: {e}")
                continue
    
    return jsonify(scripts)

@app.route('/api/scripts/<filename>', methods=['GET'])
def get_script(filename):
    """Get specific script content."""
    script_file = SCRIPTS_DIR / filename
    if not script_file.exists():
        return jsonify({'error': 'Script not found'}), 404
    
    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = ScriptParser()
        parsed = parser.parse(content)
        
        return jsonify({
            'filename': filename,
            'content': content,
            'segments': len(parsed.segments),
            'personas': list(parsed.personas),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/personas', methods=['GET'])
def get_personas():
    """Get list of available personas."""
    personas = []
    
    try:
        if not PERSONAS_CONFIG.exists():
            print(f"Personas config file not found at: {PERSONAS_CONFIG}")
            return jsonify(personas)
        
        print(f"Loading personas from: {PERSONAS_CONFIG}")
        with open(PERSONAS_CONFIG, 'r', encoding='utf-8') as f:
            personas_data = yaml.safe_load(f)
        
        if not personas_data or 'personas' not in personas_data:
            print("No 'personas' key found in config file")
            return jsonify(personas)
        
        for key, data in personas_data.get('personas', {}).items():
            personas.append({
                'key': key,
                'name': data.get('name', key.title()),
                'description': data.get('description', ''),
                'voice': data.get('voice', {}),
                'avatar': data.get('avatar', {}),
            })
        
        print(f"Loaded {len(personas)} personas")
    except Exception as e:
        import traceback
        print(f"Error loading personas: {e}")
        print(traceback.format_exc())
    
    return jsonify(personas)

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    return jsonify(base_config)

@app.route('/api/config', methods=['POST'])
def update_config_endpoint():
    """Update configuration."""
    global base_config
    try:
        new_config = request.json
        base_config = {**base_config, **new_config}
        
        # Save to file
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(base_config, f, default_flow_style=False, sort_keys=False)
        
        return jsonify({'success': True, 'config': base_config})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_generation(job_id, script_content, script_filename, personas, config_dict, temp_script):
    """Run video generation in background thread."""
    try:
        with generation_jobs_lock:
            generation_jobs[job_id]['status'] = 'processing'
            generation_jobs[job_id]['progress'] = 0
        
        # Initialize pipeline
        pipeline = Pipeline(config_dict, project_root=project_root)
        
        # Set up progress callback (thread-safe)
        def progress_callback(message, progress):
            # Ensure progress is between 0 and 1
            # Handle None or invalid progress values
            if progress is None:
                progress = 0.0
            try:
                progress_value = max(0.0, min(1.0, float(progress)))
            except (ValueError, TypeError):
                progress_value = 0.0
            
            progress_percent = int(progress_value * 100)
            
            # Update job status atomically (thread-safe)
            # Ensure progress never goes backwards
            with generation_jobs_lock:
                if job_id in generation_jobs:
                    current_job_progress = generation_jobs[job_id].get('progress', 0)
                    # Only update if progress increased or is the same
                    if progress_percent >= current_job_progress:
                        generation_jobs[job_id]['log'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'message': message,
                            'progress': progress_percent
                        })
                        generation_jobs[job_id]['progress'] = progress_percent
                        
                        # Debug: Print progress updates
                        print(f"[Job {job_id[:8]}] Progress: {progress_percent}% - {message}")
                    else:
                        # Progress went backwards - log but don't update
                        print(f"[WARN] Job {job_id[:8]} progress regression prevented: {current_job_progress}% -> {progress_percent}% (keeping {current_job_progress}%)")
                        # Still log the message but keep the higher progress
                        generation_jobs[job_id]['log'].append({
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'message': message,
                            'progress': current_job_progress  # Keep the higher progress
                        })
                else:
                    print(f"[WARN] Job {job_id[:8]} not found in generation_jobs when updating progress")
        
        pipeline.set_progress_callback(progress_callback)
        
        # Generate video
        output_path = pipeline.create_podcast(
            script_path=temp_script,
            scene_name='studio',
            cleanup_temp=False
        )
        
        with generation_jobs_lock:
            generation_jobs[job_id]['status'] = 'completed'
            generation_jobs[job_id]['progress'] = 100
            generation_jobs[job_id]['video_path'] = str(output_path.relative_to(project_root))
            generation_jobs[job_id]['video_id'] = output_path.stem
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        
        # Provide more helpful error messages
        if 'ffmpeg' in error_msg.lower() or 'ffprobe' in error_msg.lower():
            error_msg = "FFmpeg is not installed or not found in PATH. FFmpeg is required for audio/video processing."
        elif 'api' in error_msg.lower() and ('key' in error_msg.lower() or 'auth' in error_msg.lower()):
            error_msg = f"API authentication error: {error_msg}"
        elif 'persona' in error_msg.lower():
            error_msg = f"Persona configuration error: {error_msg}"
        elif 'script' in error_msg.lower():
            error_msg = f"Script parsing error: {error_msg}"
        
        print(f"Error generating video: {error_msg}")
        print(f"Traceback:\n{error_trace}")
        
        with generation_jobs_lock:
            generation_jobs[job_id]['status'] = 'failed'
            generation_jobs[job_id]['error'] = error_msg
            generation_jobs[job_id]['error_type'] = type(e).__name__
    finally:
        # Clean up temp script
        if temp_script.exists():
            temp_script.unlink()

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
def generate_video():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    """Start video generation asynchronously."""
    try:
        data = request.json
        script_content = data.get('script_content')
        script_filename = data.get('script_filename', 'custom_script.txt')
        personas = data.get('personas', [])
        config = data.get('config', base_config)
        
        if not script_content:
            return jsonify({'error': 'Script content is required'}), 400
        
        if not personas:
            return jsonify({'error': 'At least one persona is required'}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create temporary script file
        temp_script = SCRIPTS_DIR / f'temp_{job_id}.txt'
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Initialize job status (thread-safe)
        with generation_jobs_lock:
            generation_jobs[job_id] = {
                'status': 'queued',
                'progress': 0,
                'log': [],
                'error': None,
                'error_type': None,
                'video_path': None,
                'video_id': None,
                'created_at': datetime.now().isoformat()
            }
        
        # Start generation in background thread
        # CRITICAL: Use daemon=False so thread survives backend restarts during development
        # This ensures video generation completes even if we restart the backend
        thread = threading.Thread(
            target=run_generation,
            args=(job_id, script_content, script_filename, personas, config, temp_script),
            daemon=False  # Changed from True to False - jobs now survive restarts
        )
        thread.start()
        
        # Return immediately with job ID
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': 'queued',
            'message': 'Video generation started. Use /api/status/<job_id> to check progress.'
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        print(f"Error in generate_video endpoint: {error_msg}")
        print(f"Traceback:\n{error_trace}")
        return jsonify({
            'error': error_msg,
            'error_type': type(e).__name__,
        }), 500

@app.route('/api/status/<job_id>', methods=['GET', 'OPTIONS'])
def get_video_status(job_id):
    """Get status of a video generation job."""
    # Handle OPTIONS preflight FIRST (before_request might not catch it in all cases)
    if request.method == 'OPTIONS':
        print(f"[CORS DEBUG] Handling OPTIONS for /api/status/{job_id[:8]}")
        response = make_response()
        response.status_code = 200
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Max-Age'] = '3600'
        print(f"[CORS DEBUG] OPTIONS response headers: Allow-Origin={response.headers.get('Access-Control-Allow-Origin')}")
        return response
    
    # CRITICAL: Use lock to safely access generation_jobs
    # Make a copy of the job data while holding the lock to avoid race conditions
    try:
        with generation_jobs_lock:
            if job_id not in generation_jobs:
                available_job_ids = list(generation_jobs.keys())
                print(f"[Status API] Job {job_id[:8]} not found in generation_jobs.")
                print(f"[Status API] Available jobs: {[j[:8] for j in available_job_ids[:10]]}")
                print(f"[Status API] Total jobs: {len(available_job_ids)}")
                # 404 response - CORS headers will be added by after_request
                response = jsonify({
                    'error': 'Job not found', 
                    'job_id': job_id[:8],
                    'available_jobs': [j[:8] for j in available_job_ids[:5]],
                    'total_jobs': len(available_job_ids)
                })
                return response, 404
            
            # CRITICAL: Make a deep copy while holding the lock
            import copy
            job = copy.deepcopy(generation_jobs[job_id])
    except Exception as e:
        print(f"[Status API] Error accessing job {job_id[:8]}: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({'error': 'Internal server error accessing job'})
        return response, 500
        print(f"[Status API] Job {job_id[:8]}: status={job.get('status', 'unknown')}, progress={job.get('progress', 0)}%, log_entries={len(job.get('log', []))}")
    
    # Get the latest progress - ensure it never goes backwards
    # Use the maximum of current progress and all log entries to prevent regression
    current_progress = job.get('progress', 0)
    latest_progress = current_progress
    
    if job['log']:
        # Find the highest progress value from log entries
        log_progresses = [entry.get('progress', 0) for entry in job['log'] if isinstance(entry.get('progress'), (int, float))]
        if log_progresses:
            max_log_progress = max(log_progresses)
            # Use the maximum to ensure progress never goes backwards
            latest_progress = max(current_progress, max_log_progress)
            # Update the job's progress field to keep it in sync (only if it increased)
            if latest_progress > current_progress:
                with generation_jobs_lock:
                    if job_id in generation_jobs:
                        generation_jobs[job_id]['progress'] = latest_progress
    
    response = {
        'status': job['status'],
        'progress': latest_progress,
        'log_entries': job['log'][-20:],  # Last 20 entries
        'job_id': job_id,  # Include job_id in response
    }
    
    # Debug logging
    print(f"[Status API] Job {job_id[:8]}: status={job['status']}, progress={latest_progress}%, log_entries={len(job['log'])}")
    
    
    if job['status'] == 'completed':
        response['video_id'] = job['video_id']
        response['video_url'] = f'/api/videos/{Path(job["video_path"]).name}' if job['video_path'] else None
        response['output_path'] = job['video_path']
    elif job['status'] == 'failed':
        response['error'] = job['error']
        response['error_type'] = job['error_type']
    
    return jsonify(response)

@app.route('/api/voice-sample', methods=['POST'])
def generate_voice_sample():
    """Generate a voice sample for a persona."""
    try:
        data = request.json
        persona_key = data.get('persona_key')
        text = data.get('text', 'Hello, this is a sample of my voice.')
        
        # Load persona
        with open(PERSONAS_CONFIG, 'r', encoding='utf-8') as f:
            personas_data = yaml.safe_load(f)
        
        persona = personas_data.get('personas', {}).get(persona_key)
        if not persona:
            return jsonify({'error': 'Persona not found'}), 404
        
        # Generate audio sample (simplified - would use TTS engine)
        # For now, return placeholder
        return jsonify({
            'audio_url': f'/api/voice-samples/{persona_key}.mp3',
            'text': text,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/avatar-image/<provider>/<avatar_id>', methods=['GET'])
def get_avatar_image(provider, avatar_id):
    """Get avatar preview image."""
    # Return a placeholder image URL for now
    # In production, this would fetch from provider API
    # Using a data URI for a simple placeholder
    placeholder_svg = f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="200" fill="#e0e0e0"/>
        <text x="50%" y="50%" font-family="Arial" font-size="16" fill="#666" text-anchor="middle" dominant-baseline="middle">
            {avatar_id[:10]}
        </text>
    </svg>'''
    import base64
    svg_encoded = base64.b64encode(placeholder_svg.encode('utf-8')).decode('utf-8')
    image_url = f'data:image/svg+xml;base64,{svg_encoded}'
    
    return jsonify({
        'image_url': image_url,
        'provider': provider,
        'avatar_id': avatar_id,
    })

@app.route('/api/avatar-images/<provider>/<avatar_id>', methods=['GET'])
def serve_avatar_image(provider, avatar_id):
    """Serve avatar preview image (legacy route for compatibility)."""
    # Return a placeholder SVG image directly
    from flask import Response
    placeholder_svg = f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="200" fill="#e0e0e0"/>
        <text x="50%" y="50%" font-family="Arial" font-size="16" fill="#666" text-anchor="middle" dominant-baseline="middle">
            {avatar_id[:10]}
        </text>
    </svg>'''
    return Response(placeholder_svg, mimetype='image/svg+xml')

# Handle favicon requests (prevent 500 errors)
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content, but successful

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Skip API routes
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    if path != "" and path != 'favicon.ico' and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    try:
        print("The Talking Heads UI Server")
        print("=" * 40)
        print(f"API Server: http://localhost:{API_PORT}/api")
        print(f"Frontend:   http://localhost:{REACT_PORT}")
        print(f"Scripts:    {SCRIPTS_DIR}")
        print(f"Personas:   {PERSONAS_CONFIG}")
        print("=" * 40)
        print(f"\nStarting Flask API server on port {API_PORT}...")
        print(f"Note: Start the React dev server separately with: npm start")
        print(f"\n")
    except UnicodeEncodeError:
        # Fallback for Windows console
        pass
    
    # Test endpoint to verify CORS is working
    @app.route('/api/test-cors', methods=['GET', 'OPTIONS'])
    def test_cors():
        """Test endpoint to verify CORS headers are being sent correctly."""
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
        return jsonify({
            'message': 'CORS test successful',
            'origin': request.headers.get('Origin', 'none'),
            'headers_present': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS'
            }
        })
        print("The Talking Heads UI Server")
        print("=" * 40)
        print(f"API Server: http://localhost:{API_PORT}/api")
        print(f"Frontend:   http://localhost:{REACT_PORT}")
        print(f"Scripts:    {SCRIPTS_DIR}")
        print(f"Personas:   {PERSONAS_CONFIG}")
        print("=" * 40)
        print(f"\nStarting Flask API server on port {API_PORT}...")
        print(f"Note: Start the React dev server separately with: npm start")
        print(f"\n")
    
    app.run(host='0.0.0.0', port=API_PORT, debug=True)

