#!/usr/bin/env python3
"""
Flask-only launcher - runs just the trading backend on port 5000
Use this in combination with separate tunneling services
"""

import os
import sys
import signal
import subprocess
from pathlib import Path

class FlaskLauncher:
    def __init__(self):
        self.flask_process = None
        self.base_dir = Path(__file__).parent
        self.venv_python = self.base_dir / ".venv" / "Scripts" / "python.exe"
        self.app_file = self.base_dir / "app.py"
        
    def setup_environment(self):
        """Set up environment variables"""
        os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/trading"
        os.environ["FLASK_ENV"] = "development"
        os.environ["FLASK_DEBUG"] = "1"
        
    def start_flask(self):
        """Start Flask application"""
        print("[FLASK] Starting Flask trading backend...")
        print("[FLASK] Local URL: http://localhost:5000")
        print("[FLASK] Press Ctrl+C to stop")
        print("=" * 60)
        
        os.chdir(self.base_dir)
        
        # Start Flask process with direct output
        self.flask_process = subprocess.Popen(
            [str(self.venv_python), str(self.app_file)],
            env=os.environ.copy()
        )
        
        return self.flask_process
    
    def cleanup(self, signum=None, frame=None):
        """Clean up Flask process"""
        print("\n[FLASK] Shutting down...")
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
                print("[FLASK] Stopped successfully")
            except subprocess.TimeoutExpired:
                print("[FLASK] Force killing...")
                self.flask_process.kill()
            except Exception as e:
                print(f"[FLASK] Error stopping: {e}")
        sys.exit(0)
    
    def run(self):
        """Main execution"""
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        try:
            self.setup_environment()
            process = self.start_flask()
            
            # Wait for process to complete
            process.wait()
            
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            print(f"[FLASK] Error: {e}")
            self.cleanup()

if __name__ == "__main__":
    print("🔵 FLASK TRADING BACKEND")
    print("=" * 60)
    launcher = FlaskLauncher()
    launcher.run()