# Performance Analytics System

Complete guide to tracking trading performance, identifying patterns, and getting improvement suggestions.

---

## Overview

The Performance Analytics System provides comprehensive metrics tracking and analysis for your trading bot:

- **Symbol-Level Performance**: Track win rates, PnL, risk/reward ratios, and hold times for each symbol
- **Trading Flow Analysis**: Identify patterns by time of day, day of week, and trade direction
- **AI-Driven Suggestions**: Get prioritized recommendations to improve trading performance
- **Periodic Monitoring**: Schedule automated reports and alerts

---

## API Endpoints

All endpoints support a `days` query parameter (default: 30) to specify the analysis period.

### 1. Symbol Performance

Get performance metrics for a specific symbol:

```http
GET /api/performance/symbol/{symbol}?days=30
```

**Example Response:**
```json
{
  "symbol": "BTCUSD",
  "period_days": 30,
  "total_trades": 25,
  "winning_trades": 18,
  "losing_trades": 6,
  "open_trades": 1,
  "win_rate": 75.0,
  "total_pnl": 1250.50,
  "avg_win": 120.30,
  "avg_loss": -85.20,
  "risk_reward_ratio": 1.41,
  "avg_hold_time_minutes": 145.5
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/performance/symbol/BTCUSD?days=7
```

---

### 2. All Symbols Performance

Get performance for all traded symbols (sorted by PnL):

```http
GET /api/performance/all?days=30
```

**Example Response:**
```json
{
  "period_days": 30,
  "total_symbols": 10,
  "symbols": [
    {
      "symbol": "BTCUSD",
      "win_rate": 70.0,
      "total_pnl": 1500.00,
      "total_trades": 30
    },
    {
      "symbol": "ETHUSD",
      "win_rate": 45.0,
      "total_pnl": -150.00,
      "total_trades": 20
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/performance/all?days=14
```

---

### 3. Trading Flows

Identify patterns by hour, day, and direction:

```http
GET /api/performance/flows?days=30
```

**Example Response:**
```json
{
  "period_days": 30,
  "total_trades_analyzed": 100,
  "by_hour": {
    "9": {
      "count": 15,
      "wins": 12,
      "total_pnl": 450.00,
      "win_rate": 80.0
    },
    "14": {
      "count": 10,
      "wins": 4,
      "total_pnl": -200.00,
      "win_rate": 40.0
    }
  },
  "by_day": {
    "Monday": {
      "count": 25,
      "wins": 18,
      "total_pnl": 500.00,
      "win_rate": 72.0
    },
    "Friday": {
      "count": 20,
      "wins": 8,
      "total_pnl": -100.00,
      "win_rate": 40.0
    }
  },
  "by_action": {
    "long": {
      "count": 60,
      "wins": 42,
      "total_pnl": 800.00,
      "win_rate": 70.0
    },
    "short": {
      "count": 40,
      "wins": 22,
      "total_pnl": 200.00,
      "win_rate": 55.0
    }
  }
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/performance/flows?days=30
```

---

### 4. Improvement Suggestions

Get prioritized recommendations:

```http
GET /api/performance/suggestions?days=30
```

**Example Response:**
```json
{
  "period_days": 30,
  "total_suggestions": 5,
  "suggestions": [
    {
      "priority": "high",
      "category": "Win Rate",
      "suggestion": "Consider avoiding symbols with consistently low win rates",
      "details": "Symbols with <40% win rate: DOGEUSD (35%), SHIBUSD (30%)",
      "affected_symbols": ["DOGEUSD", "SHIBUSD"],
      "metric": "win_rate"
    },
    {
      "priority": "medium",
      "category": "Timing",
      "suggestion": "Avoid trading during low-performance hours",
      "details": "Hours with <50% win rate: 14 (40%), 18 (35%)",
      "affected_symbols": [],
      "metric": "time_pattern"
    },
    {
      "priority": "low",
      "category": "Opportunity",
      "suggestion": "Consider increasing position size on best performers",
      "details": "Top performers: BTCUSD (75% WR), ETHUSD (70% WR)",
      "affected_symbols": ["BTCUSD", "ETHUSD"],
      "metric": "win_rate"
    }
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/performance/suggestions?days=30
```

---

### 5. Performance Dashboard

Get comprehensive dashboard with all analytics:

```http
GET /api/performance/dashboard?days=30
```

**Example Response:**
```json
{
  "period_days": 30,
  "summary": {
    "total_symbols": 10,
    "total_trades": 150,
    "overall_pnl": 2500.50,
    "overall_win_rate": 62.5
  },
  "top_performers": [
    {
      "symbol": "BTCUSD",
      "win_rate": 75.0,
      "total_pnl": 1500.00
    }
  ],
  "worst_performers": [
    {
      "symbol": "DOGEUSD",
      "win_rate": 35.0,
      "total_pnl": -300.00
    }
  ],
  "flows": { "by_hour": {...}, "by_day": {...}, "by_action": {...} },
  "suggestions": [...]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/performance/dashboard?days=7
```

---

## Metrics Explained

### Win Rate
Percentage of trades that resulted in profit. Formula: `(winning_trades / total_trades) * 100`

**Interpretation:**
- **>60%**: Excellent - Strong strategy performance
- **50-60%**: Good - Strategy working well
- **40-50%**: Acceptable - Room for improvement
- **<40%**: Poor - Review strategy or avoid symbol

### Risk/Reward Ratio
Average win size compared to average loss size. Formula: `avg_win / abs(avg_loss)`

**Interpretation:**
- **>2.0**: Excellent - Large wins, small losses
- **1.5-2.0**: Good - Favorable risk/reward
- **1.0-1.5**: Acceptable - Balanced
- **<1.0**: Poor - Losses larger than wins

### Total PnL (Profit and Loss)
Sum of all realized profits and losses for a symbol over the period.

**Usage:**
- Positive: Symbol is profitable
- Negative: Symbol is losing money
- Sort symbols by PnL to find best/worst performers

### Average Hold Time
Average duration (in minutes) from entry to exit for closed trades.

**Usage:**
- Compare to strategy expectations
- Identify scalping vs swing trading patterns
- Optimize for symbol volatility

---

## Usage Examples

### PowerShell Examples

```powershell
# Get last 7 days performance for BTCUSD
Invoke-RestMethod -Uri "http://localhost:5000/api/performance/symbol/BTCUSD?days=7" | ConvertTo-Json -Depth 5

# Get all symbols performance
Invoke-RestMethod -Uri "http://localhost:5000/api/performance/all?days=30" | ConvertTo-Json -Depth 5

# Get trading patterns
Invoke-RestMethod -Uri "http://localhost:5000/api/performance/flows?days=14" | ConvertTo-Json -Depth 5

# Get improvement suggestions
Invoke-RestMethod -Uri "http://localhost:5000/api/performance/suggestions?days=30" | ConvertTo-Json -Depth 5

# Get full dashboard
Invoke-RestMethod -Uri "http://localhost:5000/api/performance/dashboard?days=7" | ConvertTo-Json -Depth 5
```

### Python Examples

```python
import requests

BASE_URL = "http://localhost:5000"

# Symbol performance
response = requests.get(f"{BASE_URL}/api/performance/symbol/BTCUSD?days=7")
data = response.json()
print(f"BTCUSD Win Rate: {data['win_rate']}%")
print(f"Total PnL: ${data['total_pnl']}")

# All symbols
response = requests.get(f"{BASE_URL}/api/performance/all?days=30")
symbols = response.json()['symbols']
print(f"Total symbols traded: {len(symbols)}")

# Trading flows
response = requests.get(f"{BASE_URL}/api/performance/flows?days=30")
flows = response.json()
best_hour = max(flows['by_hour'].items(), key=lambda x: x[1]['win_rate'])
print(f"Best trading hour: {best_hour[0]} with {best_hour[1]['win_rate']}% WR")

# Suggestions
response = requests.get(f"{BASE_URL}/api/performance/suggestions?days=30")
suggestions = response.json()['suggestions']
high_priority = [s for s in suggestions if s['priority'] == 'high']
print(f"High priority suggestions: {len(high_priority)}")
```

---

## Automation Ideas

### 1. Daily Performance Report

**PowerShell Script (daily_report.ps1):**
```powershell
# Get yesterday's performance
$dashboard = Invoke-RestMethod "http://localhost:5000/api/performance/dashboard?days=1"

# Format email body
$body = @"
Daily Trading Performance Report

Summary:
- Total Trades: $($dashboard.summary.total_trades)
- Overall PnL: $($dashboard.summary.overall_pnl)
- Win Rate: $($dashboard.summary.overall_win_rate)%

Top 3 Performers:
$($dashboard.top_performers[0..2] | ForEach-Object { "- $($_.symbol): $$($_.total_pnl)" })

High Priority Actions:
$($dashboard.suggestions | Where-Object { $_.priority -eq 'high' } | ForEach-Object { "- $($_.suggestion)" })
"@

# Send email or save to file
$body | Out-File -FilePath "reports\daily_$(Get-Date -Format 'yyyy-MM-dd').txt"
```

**Schedule with Task Scheduler:**
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\path\to\daily_report.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 11:59PM
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "DailyTradingReport"
```

### 2. Weekly Analysis Email

**Python Script (weekly_analysis.py):**
```python
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def send_weekly_report():
    # Get 7-day performance
    response = requests.get("http://localhost:5000/api/performance/dashboard?days=7")
    data = response.json()
    
    # Create report
    report = f"""
    Weekly Trading Analysis - {datetime.now().strftime('%Y-%m-%d')}
    
    Overall Performance:
    - Total Trades: {data['summary']['total_trades']}
    - Win Rate: {data['summary']['overall_win_rate']:.2f}%
    - Total PnL: ${data['summary']['overall_pnl']:.2f}
    
    Top 5 Performers:
    {chr(10).join(f"- {s['symbol']}: ${s['total_pnl']:.2f} ({s['win_rate']:.1f}% WR)" 
                  for s in data['top_performers'])}
    
    Improvement Suggestions:
    {chr(10).join(f"- [{s['priority'].upper()}] {s['suggestion']}" 
                  for s in data['suggestions'][:5])}
    """
    
    # Send email
    msg = MIMEText(report)
    msg['Subject'] = f"Weekly Trading Report - {datetime.now().strftime('%Y-%m-%d')}"
    msg['From'] = "trading-bot@example.com"
    msg['To'] = "your-email@example.com"
    
    # Configure SMTP settings
    # smtp.send_message(msg)
    
    print(report)

if __name__ == "__main__":
    send_weekly_report()
```

### 3. Real-Time Alerts

Monitor performance and send alerts for critical issues:

```python
import requests
import time

def check_performance_alerts():
    """Check for performance issues every hour"""
    while True:
        # Get suggestions
        response = requests.get("http://localhost:5000/api/performance/suggestions?days=1")
        suggestions = response.json()['suggestions']
        
        # Alert on high priority issues
        high_priority = [s for s in suggestions if s['priority'] == 'high']
        
        if high_priority:
            for issue in high_priority:
                send_alert(f"[URGENT] {issue['suggestion']}: {issue['details']}")
        
        # Sleep for 1 hour
        time.sleep(3600)

def send_alert(message):
    """Send alert via Telegram/Email/SMS"""
    # Implement your alert mechanism
    print(f"[ALERT] {message}")

if __name__ == "__main__":
    check_performance_alerts()
```

---

## Integration with Existing System

The performance analytics system automatically integrates with your existing trading data:

1. **Trades Table**: Analyzes entry/exit times, PnL, directions
2. **Signals Table**: Tracks signal generation and execution
3. **HistoricalPrice Table**: Uses for price context and analysis

No additional data collection needed - it works with data already being captured.

---

## Best Practices

### 1. Choose Appropriate Time Periods

- **1 day**: Quick daily review, recent changes
- **7 days**: Weekly patterns, strategy validation
- **30 days**: Month-long trends, stable metrics
- **90 days**: Quarterly review, long-term patterns

### 2. Act on High Priority Suggestions

Focus on high priority suggestions first:
- Disable symbols with <40% win rate
- Avoid trading during low-performance hours
- Review strategy for symbols with negative PnL

### 3. Monitor Regularly

Set up automated reports:
- Daily: Quick overview, immediate issues
- Weekly: Detailed analysis, pattern review
- Monthly: Strategic adjustments, long-term trends

### 4. Track Changes

Compare periods before/after making adjustments:
```python
# Before adjustment
before = requests.get("http://localhost:5000/api/performance/symbol/BTCUSD?days=30").json()

# Make adjustment (e.g., change strategy parameter)

# After adjustment (wait 7 days)
after = requests.get("http://localhost:5000/api/performance/symbol/BTCUSD?days=7").json()

# Compare
print(f"Win Rate: {before['win_rate']}% -> {after['win_rate']}%")
print(f"R/R Ratio: {before['risk_reward_ratio']:.2f} -> {after['risk_reward_ratio']:.2f}")
```

---

## Troubleshooting

### No Data Returned

**Problem**: API returns empty arrays or zero trades

**Solutions:**
1. Verify trades exist in database:
   ```sql
   SELECT COUNT(*) FROM trades WHERE created_at > NOW() - INTERVAL '30 days';
   ```

2. Check if signals are being generated:
   ```sql
   SELECT COUNT(*) FROM signals WHERE created_at > NOW() - INTERVAL '30 days';
   ```

3. Ensure historical price collection is running:
   ```sql
   SELECT COUNT(*) FROM historical_prices WHERE timestamp > NOW() - INTERVAL '1 hour';
   ```

### Unexpected Win Rates

**Problem**: Win rates seem incorrect

**Solutions:**
1. Check for open trades (not included in win rate calculation)
2. Verify exit prices are being recorded correctly
3. Review trade status field (should be 'closed' for analysis)

### Slow Performance

**Problem**: API responses are slow

**Solutions:**
1. Reduce `days` parameter (e.g., use 7 instead of 90)
2. Add database indexes:
   ```sql
   CREATE INDEX idx_trades_created_at ON trades(created_at);
   CREATE INDEX idx_trades_symbol ON trades(symbol);
   ```
3. Archive old data (>6 months)

---

## Next Steps

1. **Test the APIs**: Use the cURL examples to verify everything works
2. **Create a Dashboard**: Build a web UI or use Grafana to visualize metrics
3. **Set Up Automation**: Schedule daily/weekly reports
4. **Monitor & Adjust**: Review suggestions regularly and make improvements

---

## Support

For issues or questions:
- Check logs in `logs/app.log`
- Review database tables: `trades`, `signals`, `historical_prices`
- Test endpoints with cURL or Postman
- Verify Flask app is running on port 5000
