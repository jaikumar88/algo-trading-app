#!/usr/bin/env python3
"""
LocalTunnel launcher with auto-reconnect
Runs independently and reconnects automatically if tunnel breaks
"""

import os
import sys
import time
import signal
import subprocess
import threading
import requests
from pathlib import Path

class LocalTunnelLauncher:
    def __init__(self):
        self.tunnel_process = None
        self.monitoring = True
        self.flask_port = 5000
        self.current_url = None
        self.reconnect_delay = 5  # seconds
        self.max_retries = 3
        
    def check_tunnel_tools(self):
        """Check what tunneling tools are available"""
        print("[TUNNEL] Checking available tunneling tools...")
        
        tools = {}
        
        # Check for npx/LocalTunnel
        try:
            result = subprocess.run(['npx', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                tools['npx'] = result.stdout.strip()
                print(f"[TUNNEL] ✅ npx found: {tools['npx']}")
            else:
                print(f"[TUNNEL] ❌ npx not working")
        except:
            print(f"[TUNNEL] ❌ npx not found")
        
        # Check for ngrok
        try:
            result = subprocess.run(['ngrok', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                tools['ngrok'] = result.stdout.strip()
                print(f"[TUNNEL] ✅ ngrok found: {tools['ngrok']}")
            else:
                print(f"[TUNNEL] ❌ ngrok not working")
        except:
            print(f"[TUNNEL] ❌ ngrok not found")
        
        if not tools:
            print("[TUNNEL] ❌ No tunneling tools found!")
            print("[TUNNEL] Please install one of:")
            print("[TUNNEL]   - Node.js + npm: npm install -g localtunnel")
            print("[TUNNEL]   - ngrok: https://ngrok.com/download")
            return False
        
        return True
        
    def check_flask_running(self):
        """Check if Flask is running on port 5000"""
        print(f"[TUNNEL] Checking Flask on port {self.flask_port}...")
        
        try:
            # Try health endpoint first
            print("[TUNNEL] Trying /health endpoint...")
            response = requests.get(f"http://localhost:{self.flask_port}/health", timeout=2)
            print(f"[TUNNEL] Health endpoint response: {response.status_code}")
            if response.status_code == 200:
                return True
        except Exception as e:
            print(f"[TUNNEL] Health endpoint failed: {e}")
        
        try:
            # Try root endpoint as fallback
            print("[TUNNEL] Trying root endpoint...")
            response = requests.get(f"http://localhost:{self.flask_port}/", timeout=2)
            print(f"[TUNNEL] Root endpoint response: {response.status_code}")
            return response.status_code in [200, 404, 405]  # Any response means Flask is running
        except Exception as e:
            print(f"[TUNNEL] Root endpoint failed: {e}")
        
        try:
            # Try webhook endpoint as last resort
            print("[TUNNEL] Trying /webhook endpoint...")
            response = requests.get(f"http://localhost:{self.flask_port}/webhook", timeout=2)
            print(f"[TUNNEL] Webhook endpoint response: {response.status_code}")
            return response.status_code in [200, 404, 405, 400, 500]  # Any response means Flask is running
        except Exception as e:
            print(f"[TUNNEL] Webhook endpoint failed: {e}")
            return False
    
    def start_tunnel(self, subdomain=None, attempt=1):
        """Start LocalTunnel with optional subdomain"""
        try:
            # Try LocalTunnel first
            if self._try_localtunnel(subdomain, attempt):
                return True
                
            # Fall back to ngrok if LocalTunnel fails
            print(f"[TUNNEL] LocalTunnel failed, trying ngrok...")
            if self._try_ngrok(attempt):
                return True
                
            print(f"[TUNNEL] ❌ Both LocalTunnel and ngrok failed (attempt {attempt})")
            return False
            
        except Exception as e:
            print(f"[TUNNEL] ❌ Error starting tunnel: {e}")
            return False
    
    def _try_localtunnel(self, subdomain=None, attempt=1):
        """Try to start LocalTunnel"""
        try:
            if subdomain and attempt <= 2:
                print(f"[TUNNEL] Starting LocalTunnel with subdomain: {subdomain} (attempt {attempt})")
                cmd = ['npx', 'localtunnel', '--port', str(self.flask_port), '--subdomain', subdomain]
            else:
                print(f"[TUNNEL] Starting LocalTunnel with random subdomain (attempt {attempt})")
                cmd = ['npx', 'localtunnel', '--port', str(self.flask_port)]
            
            self.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return self._wait_for_localtunnel_url()
            
        except FileNotFoundError:
            print(f"[TUNNEL] ⚠️ npx/LocalTunnel not found")
            return False
        except Exception as e:
            print(f"[TUNNEL] ⚠️ LocalTunnel error: {e}")
            return False
    
    def _wait_for_localtunnel_url(self):
        """Wait for LocalTunnel URL specifically"""
        start_time = time.time()
        while time.time() - start_time < 30:
            if self.tunnel_process.poll() is not None:
                # Process died
                stderr = self.tunnel_process.stderr.read() if self.tunnel_process.stderr else ""
                print(f"[TUNNEL] ❌ LocalTunnel process died: {stderr}")
                break
                
            line = self.tunnel_process.stdout.readline()
            if line:
                line = line.strip()
                print(f"[TUNNEL] LocalTunnel: {line}")
                
                # LocalTunnel format: "your url is: https://..."
                if 'https://' in line:
                    self.current_url = line.split()[-1]
                    print(f"[TUNNEL] ✅ LocalTunnel Connected: {self.current_url}")
                    print(f"[TUNNEL] Flask backend: http://localhost:{self.flask_port}")
                    print(f"[TUNNEL] Public access: {self.current_url}")
                    return True
            
            time.sleep(0.5)
        
        print(f"[TUNNEL] ❌ Failed to get LocalTunnel URL")
        return False
    
    def _try_ngrok(self, attempt=1):
        """Try to start ngrok"""
        try:
            print(f"[TUNNEL] Starting ngrok (attempt {attempt})")
            cmd = ['ngrok', 'http', str(self.flask_port), '--log=stdout']
            
            self.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            return self._wait_for_ngrok_url()
            
        except FileNotFoundError:
            print(f"[TUNNEL] ⚠️ ngrok not found")
            return False
        except Exception as e:
            print(f"[TUNNEL] ⚠️ ngrok error: {e}")
            return False
    
    def _wait_for_ngrok_url(self):
        """Wait for ngrok URL specifically"""
        print("[TUNNEL] Waiting for ngrok to establish tunnel...")
        start_time = time.time()
        
        while time.time() - start_time < 30:
            if self.tunnel_process.poll() is not None:
                # Process died
                stderr_output = ""
                if self.tunnel_process.stderr:
                    stderr_output = self.tunnel_process.stderr.read()
                print(f"[TUNNEL] ❌ ngrok process died")
                if stderr_output:
                    print(f"[TUNNEL] Error: {stderr_output}")
                return False
            
            # Check if we can read a line
            try:
                line = self.tunnel_process.stdout.readline()
                if line:
                    line = line.strip()
                    if line:  # Only print non-empty lines
                        print(f"[TUNNEL] ngrok: {line}")
                    
                    # Look for ngrok URL patterns
                    if 'started tunnel' in line.lower() or 'forwarding' in line.lower():
                        # Extract URL from ngrok output
                        import re
                        url_match = re.search(r'https://[a-zA-Z0-9\-]+\.ngrok[a-zA-Z0-9\-\.]*', line)
                        if url_match:
                            self.current_url = url_match.group()
                            print(f"[TUNNEL] ✅ ngrok Connected: {self.current_url}")
                            print(f"[TUNNEL] Flask backend: http://localhost:{self.flask_port}")
                            print(f"[TUNNEL] Public access: {self.current_url}")
                            return True
                    
                    # Alternative pattern for newer ngrok versions
                    if 'https://' in line and 'ngrok' in line:
                        import re
                        url_match = re.search(r'https://[^\s]+', line)
                        if url_match:
                            potential_url = url_match.group()
                            if 'ngrok' in potential_url:
                                self.current_url = potential_url
                                print(f"[TUNNEL] ✅ ngrok Connected: {self.current_url}")
                                print(f"[TUNNEL] Flask backend: http://localhost:{self.flask_port}")
                                print(f"[TUNNEL] Public access: {self.current_url}")
                                return True
                                
            except Exception as e:
                print(f"[TUNNEL] Error reading ngrok output: {e}")
                break
            
            # Try to get URL from ngrok API as fallback
            if time.time() - start_time > 10:  # After 10 seconds, try API
                try:
                    api_response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
                    if api_response.status_code == 200:
                        data = api_response.json()
                        for tunnel in data.get('tunnels', []):
                            if tunnel.get('proto') == 'https':
                                self.current_url = tunnel.get('public_url')
                                if self.current_url:
                                    print(f"[TUNNEL] ✅ ngrok Connected (via API): {self.current_url}")
                                    print(f"[TUNNEL] Flask backend: http://localhost:{self.flask_port}")
                                    print(f"[TUNNEL] Public access: {self.current_url}")
                                    return True
                except:
                    pass  # API not available yet
            
            time.sleep(0.1)
        
        print("[TUNNEL] ❌ Failed to get ngrok URL within timeout")
        return False
    
    def monitor_tunnel(self):
        """Monitor tunnel and restart if it breaks"""
        while self.monitoring:
            time.sleep(10)  # Check every 10 seconds
            
            if not self.monitoring:
                break
                
            # Check if tunnel process is still running
            if self.tunnel_process and self.tunnel_process.poll() is not None:
                print("[TUNNEL] ⚠️ Tunnel process died, restarting...")
                self.restart_tunnel()
                continue
            
            # Check if tunnel is actually working
            if self.current_url:
                try:
                    # Try health endpoint first, then root as fallback
                    response = requests.get(f"{self.current_url}/health", timeout=5)
                    if response.status_code not in [200, 404, 405]:
                        response = requests.get(f"{self.current_url}/", timeout=5)
                        if response.status_code not in [200, 404, 405]:
                            print("[TUNNEL] ⚠️ Tunnel not responding, restarting...")
                            self.restart_tunnel()
                except:
                    print("[TUNNEL] ⚠️ Tunnel health check failed, restarting...")
                    self.restart_tunnel()
    
    def restart_tunnel(self):
        """Restart the tunnel with retry logic"""
        print("[TUNNEL] 🔄 Restarting tunnel...")
        
        # Stop current tunnel
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
            except:
                try:
                    self.tunnel_process.kill()
                except:
                    pass
        
        # Wait before restart
        time.sleep(self.reconnect_delay)
        
        # Try to restart with different strategies
        for attempt in range(1, self.max_retries + 1):
            if not self.monitoring:
                break
                
            # Try with original subdomain first, then random
            if self.start_tunnel(subdomain="trading-backend" if attempt == 1 else None, attempt=attempt):
                print("[TUNNEL] ✅ Tunnel restarted successfully")
                return
            
            if attempt < self.max_retries:
                print(f"[TUNNEL] Waiting {self.reconnect_delay} seconds before retry...")
                time.sleep(self.reconnect_delay)
        
        print("[TUNNEL] ❌ Failed to restart tunnel after all attempts")
    
    def cleanup(self, signum=None, frame=None):
        """Clean up tunnel process"""
        print("\n[TUNNEL] Shutting down...")
        self.monitoring = False
        
        if self.tunnel_process:
            try:
                self.tunnel_process.terminate()
                self.tunnel_process.wait(timeout=5)
                print("[TUNNEL] Stopped successfully")
            except subprocess.TimeoutExpired:
                print("[TUNNEL] Force killing...")
                self.tunnel_process.kill()
            except Exception as e:
                print(f"[TUNNEL] Error stopping: {e}")
        
        sys.exit(0)
    
    def run(self):
        """Main execution"""
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        # Check available tunneling tools
        if not self.check_tunnel_tools():
            return
        
        # Check if Flask is running
        if not self.check_flask_running():
            print("[TUNNEL] ❌ Flask backend not running on port 5000")
            print("[TUNNEL] Please start Flask first: python start_flask.py")
            return
        
        print("[TUNNEL] ✅ Flask backend detected on port 5000")
        
        # Start initial tunnel
        if not self.start_tunnel(subdomain="trading-backend"):
            print("[TUNNEL] ❌ Failed to start tunnel")
            return
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_tunnel, daemon=True)
        monitor_thread.start()
        
        print("[TUNNEL] 🔄 Auto-reconnect monitoring active")
        print("[TUNNEL] Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            # Keep main thread alive
            while self.monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

if __name__ == "__main__":
    print("🌐 LOCALTUNNEL AUTO-RECONNECT")
    print("=" * 60)
    launcher = LocalTunnelLauncher()
    launcher.run()