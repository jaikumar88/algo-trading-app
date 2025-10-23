"""
Simple Flask starter without health check dependencies
"""

import os
import sys
import time
import signal
import subprocess
import threading
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('startup.log')
    ]
)
logger = logging.getLogger(__name__)

class SimpleFlaskLauncher:
    def __init__(self):
        self.flask_process = None
        self.flask_port = 5000
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
        try:
            logger.info("[STARTUP] Starting Flask application...")
            
            # Change to project directory
            os.chdir(self.base_dir)
            
            # Start Flask process
            self.flask_process = subprocess.Popen(
                [str(self.venv_python), str(self.app_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ.copy()
            )
            
            logger.info("[STARTUP] Flask process started, waiting 10 seconds for initialization...")
            time.sleep(10)  # Give Flask time to start
            
            if self.flask_process.poll() is None:
                logger.info("[SUCCESS] Flask application started successfully!")
                return True
            else:
                logger.error("[ERROR] Flask process exited unexpectedly")
                return False
            
        except Exception as e:
            logger.error(f"[ERROR] Error starting Flask: {e}")
            return False
    
    def monitor_flask(self):
        """Monitor Flask process output"""
        if not self.flask_process:
            return
            
        def read_output(stream, prefix):
            try:
                for line in iter(stream.readline, ''):
                    if line.strip():
                        logger.info(f"{prefix}: {line.strip()}")
            except:
                pass
        
        # Start output monitoring threads
        threading.Thread(
            target=read_output, 
            args=(self.flask_process.stdout, "FLASK"),
            daemon=True
        ).start()
        
        threading.Thread(
            target=read_output, 
            args=(self.flask_process.stderr, "FLASK-ERR"),
            daemon=True
        ).start()
    
    def cleanup(self, signum=None, frame=None):
        """Clean up processes"""
        logger.info("[CLEANUP] Cleaning up...")
        
        # Terminate Flask process
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
                logger.info("[SUCCESS] Flask process terminated")
            except subprocess.TimeoutExpired:
                logger.warning("[WARNING] Flask process didn't terminate, killing...")
                self.flask_process.kill()
            except Exception as e:
                logger.warning(f"[WARNING] Error terminating Flask: {e}")
        
        logger.info("[DONE] Cleanup complete")
        sys.exit(0)
    
    def run(self):
        """Main execution function"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        try:
            logger.info("[SETUP] Setting up environment...")
            self.setup_environment()
            
            # Start Flask
            if not self.start_flask():
                logger.error("[ERROR] Failed to start Flask application")
                return False
            
            # Start monitoring
            self.monitor_flask()
            
            logger.info("[SUCCESS] Flask started successfully!")
            logger.info("Your trading backend is accessible at:")
            logger.info(f"   [LOCAL] http://localhost:{self.flask_port}")
            logger.info("")
            logger.info("API Endpoints:")
            logger.info(f"   • Health:      http://localhost:{self.flask_port}/health")
            logger.info(f"   • Instruments: http://localhost:{self.flask_port}/api/trading/instruments")
            logger.info(f"   • Positions:   http://localhost:{self.flask_port}/api/trading/positions")
            logger.info("")
            logger.info("[INFO] Now you can run a tunneling service separately if needed:")
            logger.info("   npx localtunnel --port 5000")
            logger.info("   or")
            logger.info("   ngrok http 5000")
            logger.info("")
            logger.info("[INFO] Press Ctrl+C to stop Flask")
            
            # Keep running
            while True:
                time.sleep(1)
                
                # Check if Flask is still running
                if self.flask_process.poll() is not None:
                    logger.error("[ERROR] Flask process died unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            logger.info("[STOP] Received interrupt signal")
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error: {e}")
        finally:
            self.cleanup()
        
        return True

def main():
    """Entry point"""
    print("[LAUNCHER] Simple Flask Launcher")
    print("=" * 50)
    
    launcher = SimpleFlaskLauncher()
    success = launcher.run()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()