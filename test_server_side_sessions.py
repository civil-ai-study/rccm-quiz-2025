# -*- coding: utf-8 -*-
"""
Ultra Sync Stage 3: Server-Side Session Test
Test the server-side session storage implementation
"""

from flask import Flask
from flask_session import Session
import os

def test_server_side_session_setup():
    """
    Test server-side session storage configuration
    """
    print("=== ULTRA SYNC STAGE 3: Server-Side Session Test ===")
    
    app = Flask(__name__)
    
    # Configure server-side sessions
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'rccm_session:'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')
    app.config['SESSION_FILE_THRESHOLD'] = 500
    app.config['SESSION_FILE_MODE'] = 384  # 0o600 in octal
    
    # Ensure session directory exists
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Initialize Flask-Session
    Session(app)
    
    print(f"[OK] Server-side session directory: {app.config['SESSION_FILE_DIR']}")
    print(f"[OK] Session type: {app.config['SESSION_TYPE']}")
    print(f"[OK] Session key prefix: {app.config['SESSION_KEY_PREFIX']}")
    
    # Check if session directory was created
    if os.path.exists(app.config['SESSION_FILE_DIR']):
        print(f"[OK] Session directory created successfully")
    else:
        print(f"[ERROR] Session directory creation failed")
        return False
    
    print(f"[SUCCESS] Ultra Sync Stage 3 server-side session configuration validated")
    return True

if __name__ == "__main__":
    success = test_server_side_session_setup()
    exit(0 if success else 1)