# Enhanced Trade Monitoring & Risk Management

## Overview
Your trade monitoring system now **properly monitors current prices** and automatically closes trades when they hit Stop Loss, Take Profit, or Trailing Stop Loss levels.

## ✅ What's Working

### 1. **Real-Time Price Monitoring**
- **Monitor Frequency**: Every 5 seconds
- **Price Source**: Delta Exchange API orderbook (mid price between bid/ask)
- **Symbols Tracked**: All symbols with open trades
- **Validation**: Rejects prices ≤ $0 and logs IP whitelist errors

### 2. **Stop Loss Detection**
Trades are automatically closed when price hits Stop Loss:

**For BUY trades:**
- SL is below entry price
- Closes when: `current_price <= stop_loss`
- Example: Entry $3,745, SL $3,707 → Closes at $3,707 or below

**For SELL trades:**
- SL is above entry price  
- Closes when: `current_price >= stop_loss`
- Example: Entry $3,745, SL $3,783 → Closes at $3,783 or above

### 3. **Take Profit Detection**
Trades are automatically closed when price hits Take Profit:

**For BUY trades:**
- TP is above entry price
- Closes when: `current_price >= take_profit`
- Example: Entry $3,745, TP $3,820 → Closes at $3,820 or above

**For SELL trades:**
- TP is below entry price
- Closes when: `current_price <= take_profit`
- Example: Entry $3,745, TP $3,670 → Closes at $3,670 or below

### 4. **Trailing Stop Loss (NEW!)**
Protects profits by trailing the stop loss as price moves in your favor:

**Two Modes:**

#### A. **Percentage-Based Trailing**
- Trails by a percentage of price movement
- Default: 0.5%
- Example (BUY trade):
  - Entry: $3,745
  - Price rises to $4,000 (new high)
  - Trailing SL: $4,000 - (0.5%) = $3,980
  - Closes if price drops to $3,980
  - If price rises to $4,100, SL moves to $4,079.50
  
#### B. **Fixed Amount Trailing**
- Trails by a fixed dollar amount
- Default: $50
- Example (BUY trade):
  - Entry: $3,745
  - Price rises to $4,000 (new high)
  - Trailing SL: $4,000 - $50 = $3,950
  - Closes if price drops to $3,950
  - If price rises to $4,100, SL moves to $4,050

**How It Works:**
1. Trailing only activates when trade is in profit
2. Tracks the highest price (BUY) or lowest price (SELL) reached
3. Calculates stop based on the peak/trough
4. Closes when price retraces by the trailing amount

### 5. **Emergency Spike Protection**
- Closes trade if price moves >10% in any direction
- Protects against flash crashes or pumps
- Example: Entry $3,745, closes if price hits $4,119.50 or $3,370.50

## 🎛️ Risk Management Settings

### Access Settings:
1. Navigate to **Risk Management** page in UI
2. All settings auto-save to database
3. Changes take effect immediately

### Available Settings:

**Basic:**
- Stop Loss %: Default 1%
- Take Profit %: Default 2%
- Max Position Size: Default 100
- Max Daily Loss: Default $1,000
- Max Daily Trades: Default 50

**Advanced Trailing Stop:**
- ✅ Enable Trailing Stop Loss (checkbox)
- Trailing Stop Type: 
  - **Percentage** (e.g., 0.5%)
  - **Fixed Amount** (e.g., $50)
- Trailing Stop Value: Set your preferred value

## 📊 How Trades Are Monitored

### Monitor Flow:

```
Every 5 seconds:
1. Fetch current prices from Delta Exchange
2. For each open trade:
   a. Check if current_price <= stop_loss → CLOSE
   b. Check if current_price >= take_profit → CLOSE
   c. If trailing enabled and in profit:
      - Track highest/lowest price
      - Check if retraced by trailing amount → CLOSE
   d. Check for emergency spike (>10%) → CLOSE
3. Close trades that hit any limit
4. Log results
```

### Example Log Output:

```
================================================================================
🔍 CHECKING ALL OPEN TRADES FOR RISK MANAGEMENT
================================================================================
Found 1 open trade(s) to check

Checking: ETHUSD SELL @ $3745.59
Current price: $3820.00
Stop Loss: $3783.05
================================================================================
[WARN] CLOSING TRADE: ETHUSD SELL
Entry: $3,745.59, Current: $3,820.00
P&L: -1.99% ($-74.41)
Reason: Stop loss hit: $3,820.00 >= $3,783.05 (loss: -1.99%)
Exit Type: stop_loss
================================================================================
```

## 🔧 Configuration Files

### Backend:
- `src/services/risk_management_service.py` - Core risk logic
- `src/services/trade_monitor_service.py` - Background monitoring
- `src/services/trading_service.py` - SL/TP calculation on trade creation

### Frontend:
- `client/src/features/risk/components/RiskManagement.jsx` - UI controls
- Settings section for trailing stop configuration

### Database:
- `system_settings` table stores all risk settings
- Settings persist across restarts
- Loaded automatically by RiskManager

## 🎯 Trade Lifecycle

### 1. Trade Created:
```python
# In trading_service.py
stop_loss = price * (1 - 0.01)  # 1% below for BUY
take_profit = price * (1 + 0.02)  # 2% above for BUY

# Saved to database
trade.stop_loss = stop_loss
trade.take_profit = take_profit
```

### 2. Monitor Checks (every 5 seconds):
```python
# In risk_management_service.py
if current_price <= trade.stop_loss:  # BUY example
    close_trade(trade, reason="Stop loss hit")
```

### 3. Trade Closed:
```python
trade.status = 'CLOSED'
trade.close_price = current_price
trade.close_time = now()
trade.stop_loss_triggered = True  # if SL hit
trade.profit_loss = calculated_pnl
```

## 📈 UI Display

### Trade History Page:
Shows for each open trade:
- **Stop Loss**: Red value or "Not Set"
- **Target Price**: Green value or "Not Set"  
- **Unrealized P&L**: Live calculation with %
- **Risk Management Card**: Shows how many trades have SL/TP set

### Risk Management Page:
Configure all risk parameters:
- Basic SL/TP percentages
- Trailing stop enable/disable
- Trailing stop type (% or $)
- Trailing stop value
- Emergency controls

## 🚀 Testing Your Setup

### 1. Check Current Trade:
```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/trading"
.venv\Scripts\python.exe -c "from src.database.session import SessionLocal; from src.models.base import Trade; s = SessionLocal(); t = s.get(Trade, 128); print(f'Trade: {t.symbol} {t.action}'); print(f'Entry: \${t.open_price}'); print(f'SL: \${t.stop_loss}'); print(f'TP: \${t.take_profit}'); s.close()"
```

### 2. Check Monitor Status:
```powershell
# Check if monitor is running
# Look in logs/app.log for:
# "[START] TRADE MONITOR STARTED"
# "[CHART] Monitor Check #X"
```

### 3. Verify Risk Settings:
```powershell
curl http://localhost:5000/api/risk/settings
```

### 4. Simulate Price Check:
Watch the logs to see price fetching:
```
[OK] ETHUSD: $3,745.59 (Bid: $3,745.50, Ask: $3,745.68)
[OK] Trade OK: ETHUSD SELL - P&L: 0.00%
```

## ⚙️ Configuration Examples

### Example 1: Conservative (Tight Stops)
```json
{
  "stop_loss_percent": 0.5,
  "take_profit_percent": 1.0,
  "trailing_stop_enabled": true,
  "trailing_stop_type": "percent",
  "trailing_stop_percent": 0.3
}
```

### Example 2: Aggressive (Wide Stops)
```json
{
  "stop_loss_percent": 3.0,
  "take_profit_percent": 10.0,
  "trailing_stop_enabled": true,
  "trailing_stop_type": "amount",
  "trailing_stop_amount": 200
}
```

### Example 3: Day Trading (Fixed Dollar)
```json
{
  "stop_loss_percent": 1.0,
  "take_profit_percent": 2.0,
  "trailing_stop_enabled": true,
  "trailing_stop_type": "amount",
  "trailing_stop_amount": 50
}
```

## 🔍 Troubleshooting

### Issue: Prices showing as $0
**Solution:** IP not whitelisted
- Go to https://www.delta.exchange/app/api-management
- Add IP: `2600:8804:9c09:9500:fcf3:1506:25c8:a52b`

### Issue: Trades not closing at SL/TP
**Check:**
1. Is monitor running? Look for "TRADE MONITOR STARTED" in logs
2. Are prices being fetched? Look for "Fetching real-time prices"
3. Is trade status 'OPEN'? (not 'open' lowercase)
4. Are SL/TP values set? Check database

### Issue: Trailing stop not working
**Check:**
1. Is trailing_stop_enabled = true in settings?
2. Is trade in profit? (Trailing only works in profit)
3. Check logs for "New high/low" messages
4. Verify trailing amount is not too small

## 📝 Summary

✅ **Price Monitoring**: Every 5 seconds from Delta Exchange
✅ **Stop Loss**: Automatically closes when hit
✅ **Take Profit**: Automatically closes when hit  
✅ **Trailing Stop**: Protects profits (by % or $)
✅ **Emergency Spike**: 10% protection
✅ **UI Controls**: Full configuration in Risk Management page
✅ **Database Persistence**: All settings saved
✅ **Real-Time Updates**: Settings apply immediately

Your trading system is now fully protected with automatic risk management!
