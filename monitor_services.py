#!/usr/bin/env python3
"""
Service status monitor
Shows real-time status of Flask and Tunnel services
"""

import os
import time
import requests
import subprocess
import threading
from datetime import datetime

class ServiceMonitor:
    def __init__(self):
        self.flask_port = 5000
        self.monitoring = True
        
    def check_flask_status(self):
        """Check Flask service status"""
        try:
            response = requests.get(f"http://localhost:{self.flask_port}/health", timeout=2)
            return {
                'status': '✅ RUNNING',
                'port': self.flask_port,
                'response_time': response.elapsed.total_seconds() * 1000,
                'last_check': datetime.now().strftime('%H:%M:%S')
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': '❌ NOT RUNNING',
                'port': self.flask_port,
                'response_time': None,
                'last_check': datetime.now().strftime('%H:%M:%S')
            }
        except Exception as e:
            return {
                'status': f'⚠️ ERROR: {str(e)[:30]}',
                'port': self.flask_port,
                'response_time': None,
                'last_check': datetime.now().strftime('%H:%M:%S')
            }
    
    def check_tunnel_status(self):
        """Check if tunnel process is running"""
        try:
            # Check for localtunnel process
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq node.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if 'node.exe' in result.stdout and 'localtunnel' in result.stdout.lower():
                return {
                    'status': '✅ RUNNING',
                    'process': 'LocalTunnel',
                    'last_check': datetime.now().strftime('%H:%M:%S')
                }
            else:
                return {
                    'status': '❌ NOT RUNNING',
                    'process': 'LocalTunnel',
                    'last_check': datetime.now().strftime('%H:%M:%S')
                }
                
        except Exception as e:
            return {
                'status': f'⚠️ ERROR: {str(e)[:30]}',
                'process': 'Unknown',
                'last_check': datetime.now().strftime('%H:%M:%S')
            }
    
    def get_system_info(self):
        """Get basic system information"""
        try:
            # Check Python processes
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True,
                shell=True
            )
            
            python_count = result.stdout.count('python.exe')
            
            return {
                'python_processes': python_count,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except:
            return {
                'python_processes': 'Unknown',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def display_status(self):
        """Display real-time status"""
        while self.monitoring:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🔍 SERVICE STATUS MONITOR")
            print("=" * 60)
            
            # Flask status
            flask_status = self.check_flask_status()
            print(f"\n📱 FLASK BACKEND")
            print(f"   Status: {flask_status['status']}")
            print(f"   Port: {flask_status['port']}")
            if flask_status['response_time']:
                print(f"   Response: {flask_status['response_time']:.1f}ms")
            print(f"   Last Check: {flask_status['last_check']}")
            
            # Tunnel status
            tunnel_status = self.check_tunnel_status()
            print(f"\n🌐 TUNNEL SERVICE")
            print(f"   Status: {tunnel_status['status']}")
            print(f"   Process: {tunnel_status['process']}")
            print(f"   Last Check: {tunnel_status['last_check']}")
            
            # System info
            sys_info = self.get_system_info()
            print(f"\n💻 SYSTEM INFO")
            print(f"   Python Processes: {sys_info['python_processes']}")
            print(f"   Timestamp: {sys_info['timestamp']}")
            
            # Instructions
            print(f"\n📋 QUICK ACTIONS")
            print(f"   Start Flask: python start_flask.py")
            print(f"   Start Tunnel: python start_tunnel.py")
            print(f"   View Logs: tail -f logs/app.log")
            
            print(f"\n⏱️ Refreshing every 3 seconds... (Ctrl+C to stop)")
            print("=" * 60)
            
            time.sleep(3)
    
    def run(self):
        """Start monitoring"""
        try:
            self.display_status()
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped")
            self.monitoring = False

if __name__ == "__main__":
    monitor = ServiceMonitor()
    monitor.run()