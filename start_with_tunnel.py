"""
Combined Flask App + LocalTunnel Startup Script
Starts Flask backend and LocalTunnel in parallel
"""
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

# Process handles
flask_process = None
tunnel_process = None

def cleanup(signum=None, frame=None):
    """Clean up processes on exit"""
    print("\n\n🛑 Shutting down services...")
    
    if flask_process:
        print("  - Stopping Flask app...")
        flask_process.terminate()
        try:
            flask_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            flask_process.kill()
    
    if tunnel_process:
        print("  - Stopping LocalTunnel...")
        tunnel_process.terminate()
        try:
            tunnel_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            tunnel_process.kill()
    
    print("✅ Services stopped\n")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def check_localtunnel():
    """Check if localtunnel is installed"""
    try:
        result = subprocess.run(['lt', '--version'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_localtunnel():
    """Install localtunnel via npm"""
    print("\n📦 LocalTunnel not found. Installing...")
    try:
        subprocess.run(['npm', 'install', '-g', 'localtunnel'], 
                      check=True,
                      timeout=120)
        print("✅ LocalTunnel installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install localtunnel")
        print("   Please install Node.js first: https://nodejs.org/")
        return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js: https://nodejs.org/")
        return False

def start_flask():
    """Start Flask application"""
    global flask_process
    
    print("\n[1/2] 🚀 Starting Flask application on port 5000...")
    
    # Use Python from virtual environment if available
    python_exe = sys.executable
    app_path = Path(__file__).parent / 'app.py'
    
    flask_process = subprocess.Popen(
        [python_exe, str(app_path)],
        stdout=open('flask_stdout.log', 'w'),
        stderr=open('flask_stderr.log', 'w'),
        cwd=Path(__file__).parent
    )
    
    print("   ⏳ Waiting for Flask to initialize...")
    time.sleep(8)  # Give Flask time to start
    
    if flask_process.poll() is not None:
        print("   ❌ Flask failed to start. Check flask_stderr.log for errors")
        return False
    
    print("   ✅ Flask app started successfully")
    return True

def start_localtunnel():
    """Start LocalTunnel"""
    global tunnel_process
    
    print("\n[2/2] 🌐 Starting LocalTunnel with subdomain 'trading-backend'...")
    
    tunnel_process = subprocess.Popen(
        ['lt', '--port', '5000', '--subdomain', 'trading-backend'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Wait a bit and check if tunnel started
    time.sleep(3)
    
    if tunnel_process.poll() is not None:
        print("   ❌ LocalTunnel failed to start")
        return False
    
    print("   ✅ LocalTunnel started successfully")
    return True

def main():
    """Main startup routine"""
    print("=" * 60)
    print("  🚀 RAG Trading System with LocalTunnel")
    print("=" * 60)
    
    # Check and install localtunnel if needed
    if not check_localtunnel():
        if not install_localtunnel():
            sys.exit(1)
    
    # Start Flask
    if not start_flask():
        cleanup()
        sys.exit(1)
    
    # Start LocalTunnel
    if not start_localtunnel():
        cleanup()
        sys.exit(1)
    
    # Display success message
    print("\n" + "=" * 60)
    print("  ✅ Services Running Successfully!")
    print("=" * 60)
    print(f"  📍 Local:        http://localhost:5000")
    print(f"  🌍 Public URL:   https://trading-backend.loca.lt")
    print("=" * 60)
    print("\n💡 Tips:")
    print("  - First time? Visit the public URL and click 'Continue'")
    print("  - Check flask_stdout.log for Flask logs")
    print("  - Press Ctrl+C to stop both services")
    print("\n⏳ Services running... (Press Ctrl+C to stop)\n")
    
    # Monitor tunnel output
    try:
        while True:
            if tunnel_process.poll() is not None:
                print("\n⚠️  LocalTunnel stopped unexpectedly")
                break
            
            if flask_process.poll() is not None:
                print("\n⚠️  Flask app stopped unexpectedly")
                break
            
            # Read and display tunnel output
            line = tunnel_process.stdout.readline()
            if line:
                print(f"[LocalTunnel] {line.strip()}")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        cleanup()
        sys.exit(1)
