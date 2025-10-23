"""
Robust startup script for Flask with multiple tunneling options.
Falls back gracefully if one tunneling method fails.
"""

import os
import sys
import time
import signal
import subprocess
import threading
import logging
import json
from pathlib import Path
import requests

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

class FlaskTunnelLauncher:
    def __init__(self):
        self.flask_process = None
        self.tunnel_process = None
        self.flask_port = 5000
        self.base_dir = Path(__file__).parent
        self.venv_python = self.base_dir / ".venv" / "Scripts" / "python.exe"
        self.app_file = self.base_dir / "app.py"
        self.public_url = None
        
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
            
            # Wait for Flask to start
            logger.info("[STARTUP] Waiting for Flask to start...")
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    response = requests.get(f"http://localhost:{self.flask_port}/health", timeout=2)
                    if response.status_code == 200:
                        logger.info("[SUCCESS] Flask application started successfully!")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
                    if attempt % 5 == 0:
                        logger.info(f"   Attempt {attempt + 1}/{max_attempts}...")
            
            logger.error("[ERROR] Flask failed to start within 30 seconds")
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] Error starting Flask: {e}")
            return False
    
    def check_npm_localtunnel(self):
        """Check if localtunnel is available via npm"""
        try:
            result = subprocess.run(['npm', 'list', '-g', 'localtunnel'], 
                                    capture_output=True, text=True, timeout=10)
            return 'localtunnel@' in result.stdout
        except:
            return False
    
    def install_localtunnel(self):
        """Install localtunnel globally"""
        try:
            logger.info("[INSTALL] Installing LocalTunnel...")
            result = subprocess.run(['npm', 'install', '-g', 'localtunnel'], 
                                    capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                logger.info("[SUCCESS] LocalTunnel installed successfully")
                return True
            else:
                logger.error(f"[ERROR] Failed to install LocalTunnel: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"[ERROR] Error installing LocalTunnel: {e}")
            return False
    
    def start_localtunnel(self):
        """Start LocalTunnel"""
        try:
            logger.info("[TUNNEL] Starting LocalTunnel...")
            
            # Check if localtunnel is available
            if not self.check_npm_localtunnel():
                logger.info("[INSTALL] LocalTunnel not found, installing...")
                if not self.install_localtunnel():
                    return None
            
            # Start tunnel with random subdomain first (more likely to work)
            logger.info("[TUNNEL] Trying with random subdomain...")
            self.tunnel_process = subprocess.Popen(
                ['npx', 'localtunnel', '--port', str(self.flask_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for tunnel URL
            start_time = time.time()
            while time.time() - start_time < 30:
                if self.tunnel_process.poll() is not None:
                    # Process died
                    break
                    
                line = self.tunnel_process.stdout.readline()
                if line and 'https://' in line:
                    self.public_url = line.strip().split()[-1]
                    logger.info(f"[SUCCESS] LocalTunnel established!")
                    logger.info(f"[PUBLIC] Public URL: {self.public_url}")
                    logger.info(f"[LOCAL] Local URL: http://localhost:{self.flask_port}")
                    return self.public_url
                
                time.sleep(0.5)
            
            logger.error("[ERROR] LocalTunnel failed to start")
            return None
            
        except Exception as e:
            logger.error(f"[ERROR] Error starting LocalTunnel: {e}")
            return None
    
    def start_tunnel_with_subdomain(self, subdomain="trading-backend"):
        """Try to start tunnel with specific subdomain"""
        try:
            logger.info(f"[TUNNEL] Trying LocalTunnel with subdomain: {subdomain}")
            
            if self.tunnel_process:
                self.tunnel_process.terminate()
                time.sleep(2)
            
            self.tunnel_process = subprocess.Popen(
                ['npx', 'localtunnel', '--port', str(self.flask_port), '--subdomain', subdomain],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for tunnel URL
            start_time = time.time()
            while time.time() - start_time < 15:
                if self.tunnel_process.poll() is not None:
                    break
                    
                line = self.tunnel_process.stdout.readline()
                if line and 'https://' in line:
                    self.public_url = line.strip().split()[-1]
                    logger.info(f"[SUCCESS] LocalTunnel with subdomain established!")
                    logger.info(f"[PUBLIC] Public URL: {self.public_url}")
                    return self.public_url
                
                time.sleep(0.5)
            
            return None
            
        except Exception as e:
            logger.error(f"[ERROR] Error starting LocalTunnel with subdomain: {e}")
            return None
    
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
        
        # Terminate tunnel process
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
                logger.info("[SUCCESS] Tunnel process terminated")
            except subprocess.TimeoutExpired:
                logger.warning("[WARNING] Tunnel process didn't terminate, killing...")
                self.tunnel_process.kill()
            except Exception as e:
                logger.warning(f"[WARNING] Error terminating tunnel: {e}")
        
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
            
            # Try different tunneling approaches
            tunnel_url = None
            
            # Method 1: Random subdomain (most likely to work)
            tunnel_url = self.start_localtunnel()
            
            # Method 2: Try with custom subdomain if random failed
            if not tunnel_url:
                logger.info("[TUNNEL] Random subdomain failed, trying custom subdomain...")
                tunnel_url = self.start_tunnel_with_subdomain("trading-backend")
            
            # Method 3: Try different subdomain
            if not tunnel_url:
                logger.info("[TUNNEL] Custom subdomain failed, trying alternative...")
                tunnel_url = self.start_tunnel_with_subdomain("flask-trading")
            
            if tunnel_url:
                logger.info("[SUCCESS] All services started successfully!")
                logger.info("Your trading backend is now accessible at:")
                logger.info(f"   [PUBLIC] {tunnel_url}")
                logger.info(f"   [LOCAL]  http://localhost:{self.flask_port}")
                logger.info("")
                logger.info("API Endpoints:")
                logger.info(f"   • Health:      {tunnel_url}/health")
                logger.info(f"   • Instruments: {tunnel_url}/api/trading/instruments")
                logger.info(f"   • Positions:   {tunnel_url}/api/trading/positions")
                logger.info("")
            else:
                logger.warning("[WARNING] Tunneling failed, but Flask is running locally")
                logger.info("Flask is accessible at:")
                logger.info(f"   [LOCAL] http://localhost:{self.flask_port}")
                logger.info("")
                logger.info("Local API Endpoints:")
                logger.info(f"   • Health:      http://localhost:{self.flask_port}/health")
                logger.info(f"   • Instruments: http://localhost:{self.flask_port}/api/trading/instruments")
                logger.info(f"   • Positions:   http://localhost:{self.flask_port}/api/trading/positions")
                logger.info("")
                logger.info("Troubleshooting:")
                logger.info("1. Check your firewall settings")
                logger.info("2. Try manually running: npx localtunnel --port 5000")
                logger.info("3. Consider using ngrok instead: https://ngrok.com/download")
            
            logger.info("[INFO] Press Ctrl+C to stop all services")
            
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
    print("[LAUNCHER] Flask + Tunnel Launcher")
    print("=" * 50)
    
    launcher = FlaskTunnelLauncher()
    success = launcher.run()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()