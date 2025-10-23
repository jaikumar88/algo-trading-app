# RAG Trading System - Startup Scripts

This directory contains several startup scripts to launch both the Flask application and ngrok tunnel together.

## Quick Start

### Windows Users

**Option 1: PowerShell Script (Recommended)**
```powershell
.\start_server.ps1
```

**Option 2: Batch File**
```cmd
start_server.bat
```

### Cross-Platform (Python Script)

```bash
python start_server.py
```

## What the Scripts Do

1. **Check Prerequisites**: Verify ngrok is installed and accessible
2. **Clean Up**: Kill any existing Flask/ngrok processes
3. **Start Flask**: Launch the Flask application on http://localhost:5000
4. **Start ngrok**: Create a public tunnel to your local server
5. **Display URLs**: Show both local and public URLs for testing
6. **Monitor**: Keep both services running until you press Ctrl+C

## Expected Output

When successfully started, you'll see:

```
🎉 RAG Trading System is now running!

📱 Local URLs:
   Dashboard: http://localhost:5000/dashboard
   Signals:   http://localhost:5000/signals
   API:       http://localhost:5000/api/trading/trades

🌍 Public URLs (for TradingView):
   Webhook:   https://abc123.ngrok-free.app/webhook
   Dashboard: https://abc123.ngrok-free.app/dashboard

📋 TradingView Webhook Configuration:
   URL: https://abc123.ngrok-free.app/webhook
   Method: POST
   Content-Type: application/json

🔧 ngrok Web Interface: http://localhost:4040
```

## TradingView Configuration

Use the public webhook URL (e.g., `https://abc123.ngrok-free.app/webhook`) in your TradingView alerts.

### Example Alert Message
```json
{
  "action": "buy",
  "symbol": "{{ticker}}",
  "price": {{close}},
  "volume": 0.1
}
```

## Prerequisites

1. **ngrok**: Download and install from https://ngrok.com/download
2. **ngrok auth**: Run `ngrok config add-authtoken YOUR_TOKEN` with your auth token
3. **Python Environment**: Virtual environment should be set up in `.venv`
4. **Dependencies**: All Python packages should be installed

## Troubleshooting

### "ngrok not found"
- Install ngrok from https://ngrok.com/download
- Add ngrok to your system PATH
- Restart your terminal

### "Flask failed to start"
- Check `flask_stderr.log` for errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify database is accessible

### "Could not retrieve ngrok tunnel URL"
- Check if ngrok auth token is configured: `ngrok config check`
- Visit http://localhost:4040 to see ngrok web interface
- Ensure you have a free ngrok account and tunnel limit not exceeded

## Manual Start (Alternative)

If you prefer to start services manually:

1. **Start Flask**:
   ```bash
   python app.py
   ```

2. **Start ngrok** (in another terminal):
   ```bash
   ngrok http 5000
   ```

3. **Get tunnel URL**: Visit http://localhost:4040 or check terminal output

## Stopping Services

- Press `Ctrl+C` in the script terminal
- Or run the cleanup: `Get-Process python | Stop-Process -Force; Get-Process ngrok | Stop-Process -Force`