# Service Management Scripts

This directory contains independent service launchers for better reliability and control.

## 🚀 Quick Start

### Start Services Independently

```bash
# Terminal 1 - Start Flask Backend
python start_flask.py

# Terminal 2 - Start Tunnel Service  
python start_tunnel.py

# Terminal 3 - Monitor Services (optional)
python monitor_services.py
```

## 📋 Service Scripts

### 1. `start_flask.py` - Flask Backend Only
- **Purpose**: Run Flask backend on port 5000
- **Features**: 
  - Production-ready WSGI server
  - Environment variable loading
  - Graceful shutdown handling
  - Health check endpoint
- **Usage**: `python start_flask.py`
- **Logs**: Console output + `logs/app.log`

### 2. `start_tunnel.py` - Tunnel Service Only  
- **Purpose**: Run LocalTunnel with auto-reconnect
- **Features**:
  - Automatic tunnel reconnection
  - Health monitoring every 10 seconds
  - Subdomain preference (trading-backend)
  - Flask backend detection
- **Usage**: `python start_tunnel.py`
- **Prerequisites**: Flask must be running on port 5000

### 3. `monitor_services.py` - Status Monitor
- **Purpose**: Real-time service status monitoring
- **Features**:
  - Flask health checks with response times
  - Tunnel process monitoring
  - System information display
  - 3-second refresh rate
- **Usage**: `python monitor_services.py`

## 🔄 Service Management Workflow

### Normal Operation
1. **Start Flask**: `python start_flask.py`
2. **Verify Flask**: Check `http://localhost:5000/health`
3. **Start Tunnel**: `python start_tunnel.py`
4. **Monitor**: `python monitor_services.py` (optional)

### When Tunnel Breaks
- **Problem**: TradingView webhooks fail, tunnel URL not accessible
- **Solution**: Tunnel service auto-restarts (no manual intervention)
- **Manual Restart**: Stop tunnel (`Ctrl+C`) and restart (`python start_tunnel.py`)

### When Flask Crashes
- **Problem**: API endpoints return 500 errors, webhook processing stops
- **Solution**: Restart Flask service only
- **Steps**: 
  1. Stop Flask (`Ctrl+C` in Flask terminal)
  2. Restart Flask (`python start_flask.py`)
  3. Tunnel continues running, reconnects automatically

## 🛠️ Troubleshooting

### Common Issues

#### Flask Won't Start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill processes using port 5000
taskkill /PID <process_id> /F
```

#### Tunnel Connection Failed
```bash
# Check if Flask is running
curl http://localhost:5000/health

# Check network connectivity
ping google.com

# Try manual tunnel
npx localtunnel --port 5000
```

#### Services Not Detected
```bash
# Check Python processes
tasklist | findstr python.exe

# Check Node.js processes (for tunnel)
tasklist | findstr node.exe
```

### Service Dependencies

```
[TradingView] --webhook--> [Tunnel] --proxy--> [Flask:5000]
                              ↓
                         [Auto-Reconnect]
```

- **Flask**: Independent, runs on port 5000
- **Tunnel**: Depends on Flask, proxies to port 5000
- **Monitor**: Depends on both, read-only status checks

## 📊 Monitoring & Logs

### Log Files
- **Flask Logs**: `logs/app.log` (UTF-8 encoded)
- **Console Logs**: Terminal output for each service
- **Webhook Logs**: Included in Flask logs with [INCOMING] markers

### Health Endpoints
- **Flask Health**: `http://localhost:5000/health`
- **Public Health**: `https://your-tunnel-url.loca.lt/health`

### Status Indicators
- **✅ RUNNING**: Service operational
- **❌ NOT RUNNING**: Service stopped
- **⚠️ ERROR**: Service in error state
- **🔄 RESTARTING**: Auto-reconnect in progress

## 🎯 Benefits of Separation

### Before (Combined Scripts)
- Single point of failure
- Tunnel breaks = restart everything
- Mixed logs and processes
- Difficult to debug issues

### After (Separate Services)
- Independent operation
- Tunnel breaks = only tunnel restarts
- Clear separation of concerns
- Flask stays running during tunnel issues
- Better debugging and monitoring
- Webhook processing continues even during tunnel reconnection

## 💡 Advanced Usage

### Custom Tunnel Subdomain
```python
# Edit start_tunnel.py, line 45
subdomain="your-custom-name"
```

### Production Flask Config
```python
# Edit start_flask.py, add production config
app.config['ENV'] = 'production'
app.config['DEBUG'] = False
```

### Monitoring Automation
```bash
# Create scheduled task for monitoring
schtasks /create /tn "Trading Monitor" /tr "python monitor_services.py" /sc minute /mo 5
```

## 🚨 Emergency Procedures

### Complete Service Restart
```bash
# Stop all Python processes
taskkill /IM python.exe /F

# Stop all Node.js processes  
taskkill /IM node.exe /F

# Restart services
python start_flask.py    # Terminal 1
python start_tunnel.py   # Terminal 2
```

### Lost Webhook Connectivity
1. Check Flask health: `http://localhost:5000/health`
2. Check tunnel URL in tunnel terminal output
3. Update TradingView webhook URL if changed
4. Test webhook: `curl -X POST your-tunnel-url/webhook`

### Database Connection Issues
1. Check PostgreSQL service: `net start postgresql-x64-13`
2. Check connection string in environment variables
3. Restart Flask service: `python start_flask.py`