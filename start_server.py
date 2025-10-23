#!/usr/bin/env python3
"""
RAG Trading System - Combined Startup Script
Starts both Flask app and ngrok tunnel
"""
import subprocess
import time
import sys
import os
import signal
import requests
import json
from pathlib import Path

def print_colored(text, color="white"):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m", 
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def check_ngrok():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split()[2] if len(result.stdout.split()) > 2 else "unknown"
            print_colored(f"✅ ngrok is installed: {version}", "green")
            return True
    except FileNotFoundError:
        pass
    
    print_colored("❌ ngrok is not installed or not in PATH", "red")
    print_colored("Please install ngrok from https://ngrok.com/download", "yellow")
    print_colored("After installation, run: ngrok config add-authtoken YOUR_TOKEN", "yellow")
    return False

def kill_existing_processes():
    """Kill any existing Flask or ngrok processes"""
    print_colored("🧹 Cleaning up existing processes...", "yellow")
    
    # Kill Flask processes
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, check=False)
        else:  # Unix-like
            subprocess.run(['pkill', '-f', 'app.py'], 
                         capture_output=True, check=False)
    except:
        pass
    
    # Kill ngrok processes
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/f', '/im', 'ngrok.exe'], 
                         capture_output=True, check=False)
        else:  # Unix-like
            subprocess.run(['pkill', '-f', 'ngrok'], 
                         capture_output=True, check=False)
    except:
        pass
    
    time.sleep(2)

def start_flask():
    """Start Flask application"""
    print_colored("🐍 Starting Flask application...", "cyan")
    
    # Determine Python executable
    venv_python = None
    if os.name == 'nt':  # Windows
        venv_python = Path('.venv/Scripts/python.exe')
    else:  # Unix-like
        venv_python = Path('.venv/bin/python')
    
    if venv_python.exists():
        python_cmd = str(venv_python)
    else:
        python_cmd = sys.executable
    
    # Start Flask
    flask_process = subprocess.Popen(
        [python_cmd, 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for Flask to start
    print_colored("⏳ Waiting for Flask to start...", "yellow")
    
    for i in range(15):  # Wait up to 15 seconds
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=2)
            if response.status_code == 200:
                print_colored("✅ Flask application is running on http://localhost:5000", "green")
                return flask_process
        except:
            time.sleep(1)
    
    print_colored("❌ Flask failed to start properly", "red")
    print_colored("Check logs for errors", "yellow")
    try:
        flask_process.terminate()
    except:
        pass
    return None

def start_ngrok():
    """Start ngrok tunnel"""
    print_colored("🌐 Starting ngrok tunnel...", "cyan")
    
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', '5000', '--log=stdout'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for ngrok to start
    time.sleep(3)
    
    return ngrok_process

def get_ngrok_url():
    """Get ngrok tunnel URL"""
    print_colored("🔍 Getting ngrok tunnel URL...", "yellow")
    
    for i in range(10):
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
            data = response.json()
            
            for tunnel in data.get('tunnels', []):
                if tunnel.get('proto') == 'https':
                    return tunnel.get('public_url')
        except:
            time.sleep(1)
    
    return None

def print_startup_info(tunnel_url):
    """Print startup information"""
    print_colored("\n🎉 RAG Trading System is now running!", "green")
    print()
    print_colored("📱 Local URLs:", "cyan")
    print(f"   Dashboard: http://localhost:5000/dashboard")
    print(f"   Signals:   http://localhost:5000/signals")
    print(f"   API:       http://localhost:5000/api/trading/trades")
    print()
    
    if tunnel_url:
        print_colored("🌍 Public URLs (for TradingView):", "cyan")
        print_colored(f"   Webhook:   {tunnel_url}/webhook", "green")
        print(f"   Dashboard: {tunnel_url}/dashboard")
        print()
        print_colored("📋 TradingView Webhook Configuration:", "yellow")
        print_colored(f"   URL: {tunnel_url}/webhook", "green")
        print("   Method: POST")
        print("   Content-Type: application/json")
        print()
    else:
        print_colored("⚠️  Could not retrieve ngrok tunnel URL", "yellow")
        print("Check ngrok status at http://localhost:4040")
        print()
    
    print_colored("🔧 ngrok Web Interface: http://localhost:4040", "magenta")
    print()
    print_colored("📝 Example TradingView Alert Message:", "yellow")
    print('   {"action": "buy", "symbol": "{{ticker}}", "price": {{close}}, "volume": 0.1}')
    print()

def main():
    print_colored("🚀 Starting RAG Trading System...", "green")
    
    # Check prerequisites
    if not check_ngrok():
        sys.exit(1)
    
    # Cleanup existing processes
    kill_existing_processes()
    
    # Start Flask
    flask_process = start_flask()
    if not flask_process:
        sys.exit(1)
    
    # Start ngrok
    ngrok_process = start_ngrok()
    
    # Get tunnel URL
    tunnel_url = get_ngrok_url()
    
    # Print startup info
    print_startup_info(tunnel_url)
    
    # Monitor services
    print_colored("🔄 Monitoring services... Press Ctrl+C to stop all services", "cyan")
    print()
    
    def signal_handler(sig, frame):
        print_colored("\n🛑 Shutting down services...", "yellow")
        try:
            flask_process.terminate()
            ngrok_process.terminate()
        except:
            pass
        
        # Force kill if needed
        time.sleep(2)
        kill_existing_processes()
        print_colored("✅ All services stopped", "green")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while True:
            # Check if processes are still running
            if flask_process.poll() is not None:
                print_colored("❌ Flask application stopped unexpectedly", "red")
                break
            
            if ngrok_process.poll() is not None:
                print_colored("❌ ngrok tunnel stopped unexpectedly", "red")
                break
            
            time.sleep(5)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == '__main__':
    main()