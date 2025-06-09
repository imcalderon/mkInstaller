"""
Helper script to start the Flask web API
"""
import os
import sys
import subprocess

def main():
    """Start the Flask web API"""
    # Add current directory to path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    print("Starting Flask web API...")
    
    # Check if requirements are installed
    try:
        import flask
        import flask_cors
    except ImportError:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Import from web_api directory
    from web_api.app import app
    
    # Start Flask app
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()
