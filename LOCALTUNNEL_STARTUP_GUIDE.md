# Combined Flask + LocalTunnel Startup Guide

## Quick Start

### Option 1: Batch Script (Windows) - Recommended
```cmd
start-with-tunnel.bat
```

### Option 2: Python Script (Cross-platform)
```cmd
python start_with_tunnel.py
```

### Option 3: PowerShell Script (Windows)
```powershell
.\start-with-tunnel.ps1
```

## What It Does

Each script does the following automatically:

1. ✅ Activates Python virtual environment
2. ✅ Cleans up any existing processes
3. ✅ Checks/installs LocalTunnel (if needed)
4. ✅ Starts Flask app on port 5000
5. ✅ Starts LocalTunnel with subdomain 'trading-backend'
6. ✅ Displays both local and public URLs
7. ✅ Handles cleanup when you press Ctrl+C

## URLs

After successful startup, your application will be accessible at:

- **Local**: http://localhost:5000
- **Public**: https://trading-backend.loca.lt

## First Time Setup

### Install Node.js (for LocalTunnel)
If you don't have Node.js installed:
1. Download from: https://nodejs.org/
2. Install (recommended: LTS version)
3. Restart terminal

### Install LocalTunnel
LocalTunnel will be auto-installed by the scripts, but you can install manually:
```cmd
npm install -g localtunnel
```

## Using LocalTunnel

### First Visit
When you first visit https://trading-backend.loca.lt:
1. You'll see a warning page
2. Click "Continue"
3. Your app will load

### Custom Subdomain
The scripts use `trading-backend` as the subdomain. To change it:

**In batch file:**
```bat
lt --port 5000 --subdomain your-custom-name
```

**In Python file:**
Edit this line:
```python
['lt', '--port', '5000', '--subdomain', 'your-custom-name']
```

**In PowerShell:**
```powershell
lt --port 5000 --subdomain your-custom-name
```

## Stopping Services

Press **Ctrl+C** in the terminal window to stop both services.

All scripts handle cleanup automatically:
- Stops Flask app
- Stops LocalTunnel
- Cleans up processes

## Logs

- **Flask stdout**: `flask_stdout.log`
- **Flask stderr**: `flask_stderr.log`

Check these files if Flask fails to start.

## Troubleshooting

### LocalTunnel Not Found
```
Error: 'lt' is not recognized
```
**Solution**: Install Node.js from https://nodejs.org/

### Port Already in Use
```
Error: Port 5000 is already in use
```
**Solution**: 
1. Stop the script (Ctrl+C)
2. Kill existing processes:
   ```cmd
   taskkill /f /im python.exe
   ```
3. Restart the script

### Flask Fails to Start
**Solution**:
1. Check `flask_stderr.log` for errors
2. Make sure PostgreSQL is running
3. Check database connection in `.env`

### Subdomain Unavailable
```
Error: Subdomain is already in use
```
**Solution**: Choose a different subdomain name

## Advanced Options

### Change Port
To run on a different port (e.g., 8080):

1. Update Flask to run on port 8080
2. Change LocalTunnel command:
   ```cmd
   lt --port 8080 --subdomain trading-backend
   ```

### Use Random Subdomain
Remove `--subdomain` flag for a random subdomain:
```cmd
lt --port 5000
```

### LocalTunnel Options
```cmd
lt --help
```

Common options:
- `--port`: Port to tunnel (required)
- `--subdomain`: Request specific subdomain
- `--local-host`: Local host to tunnel (default: localhost)

## Security Notes

⚠️ **Important**: LocalTunnel exposes your local server to the internet!

- Only use for development/testing
- Don't share sensitive data
- Use authentication/authorization
- Consider using ngrok for production with custom domains
- Tunnel closes when script stops

## Comparison: LocalTunnel vs ngrok

| Feature | LocalTunnel | ngrok |
|---------|------------|-------|
| Free | ✅ Yes | ✅ Yes (limited) |
| Custom Subdomain | ✅ Yes | ⚠️ Paid only |
| Installation | npm | Download binary |
| Speed | Fast | Faster |
| Reliability | Good | Better |
| HTTPS | ✅ Yes | ✅ Yes |

## Alternative: Manual Start

If you prefer to start services separately:

**Terminal 1 - Flask:**
```cmd
python app.py
```

**Terminal 2 - LocalTunnel:**
```cmd
lt --port 5000 --subdomain trading-backend
```

## Production Deployment

For production, consider:
- Proper hosting (AWS, Azure, DigitalOcean)
- Domain with SSL certificate
- ngrok Pro with custom domain
- Cloudflare Tunnel (free, more reliable)

## Scripts Summary

| Script | Platform | Best For |
|--------|----------|----------|
| `start-with-tunnel.bat` | Windows | Quick Windows startup |
| `start_with_tunnel.py` | Cross-platform | Advanced control |
| `start-with-tunnel.ps1` | Windows PowerShell | PowerShell users |

Choose the one that works best for your workflow!
