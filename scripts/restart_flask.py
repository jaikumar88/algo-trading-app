# Quick restart script for Flask
# This ensures the latest code changes are loaded

import subprocess
import sys
import os

print("🔄 Restarting Flask server with updated CORS settings...\n")

# Kill any existing Flask processes on port 5000
print("1️⃣ Checking for existing Flask processes...")
try:
    if sys.platform == 'win32':
        subprocess.run(['powershell', '-Command', 
                       "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | "
                       "ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"],
                      capture_output=True)
        print("   ✅ Stopped existing Flask processes\n")
except Exception as e:
    print(f"   ⚠️  Could not stop processes: {e}\n")

# Start Flask
print("2️⃣ Starting Flask server...")
print("   Location: http://localhost:5000")
print("   CORS: Enabled for http://localhost:5173")
print("\n📝 Logs will appear below:")
print("=" * 60)

os.system("python app.py")
