# ✅ TradingView Webhook Integration - Complete Setup!

## 🎯 Status: FULLY OPERATIONAL

Your TradingView webhook endpoint is now live and ready to receive alerts!

**Webhook URL**: `https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook`

---

## 📊 What Was Done

### 1. **Created Webhook API** (`src/api/webhook.py`)
- ✅ Complete webhook endpoint implementation
- ✅ TradingView alert parsing (JSON and text)
- ✅ Signal extraction (action, symbol, price, size, SL, TP)
- ✅ Idempotency protection (prevent duplicate processing)
- ✅ Database persistence (Signal table)
- ✅ Telegram notifications (optional)
- ✅ Trade processing integration

### 2. **Fixed Import Issues**
- ✅ Fixed `trading_service.py` imports (added `src.` prefix)
- ✅ Registered webhook blueprint in `app.py`
- ✅ All modules properly referenced

### 3. **Started ngrok Tunnel**
- ✅ ngrok running on port 5000
- ✅ Public URL: `https://uncurdling-joane-pantomimical.ngrok-free.dev`
- ✅ Webhook endpoint: `/webhook`

---

## 🚀 TradingView Alert Setup

### **Step 1: Create Alert in TradingView**

1. Open your chart on TradingView
2. Click the **Alert** button (🔔) or press `Alt + A`
3. Configure your alert conditions

### **Step 2: Configure Webhook**

In the **Notifications** tab:

1. Check **Webhook URL**
2. Enter: `https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook`

### **Step 3: Alert Message Format**

Use JSON format for best results:

#### **Option 1: Simple JSON** (Recommended)
```json
{
  "action": "{{strategy.order.action}}",
  "symbol": "{{ticker}}",
  "price": {{close}},
  "message": "{{strategy.order.alert_message}}"
}
```

#### **Option 2: Detailed JSON**
```json
{
  "action": "BUY",
  "symbol": "BTCUSDT",
  "price": 43250.50,
  "size": 0.001,
  "stop_loss": 42500,
  "take_profit": 44000,
  "timestamp": "{{time}}",
  "timeframe": "{{interval}}"
}
```

#### **Option 3: Simple Text**
```
Action: BUY
Symbol: BTCUSDT
Price: 43250.50
```

---

## 📝 Supported Alert Fields

The webhook automatically extracts:

| Field | JSON Keys | Description |
|-------|-----------|-------------|
| **Action** | `action`, `side`, `type`, `order_action`, `signal` | BUY, SELL, LONG, SHORT |
| **Symbol** | `symbol`, `ticker`, `pair`, `instrument` | Trading pair (e.g., BTCUSDT) |
| **Price** | `price`, `close`, `entry_price`, `signal_price` | Entry price |
| **Size** | `size`, `quantity`, `amount` | Position size |
| **Stop Loss** | `stop_loss`, `sl` | Stop loss price |
| **Take Profit** | `take_profit`, `tp` | Take profit price |

---

## 🔐 Security (Optional)

### **Add Webhook Secret**

1. Add to your `.env` file:
   ```bash
   WEBHOOK_SECRET=your_secret_key_here
   ```

2. In TradingView alert, add header or URL parameter:
   - **Header**: `X-WEBHOOK-SECRET: your_secret_key_here`
   - **URL**: `https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook?secret=your_secret_key_here`

---

## 📊 Webhook Flow

```
TradingView Alert
        ↓
     ngrok Tunnel
        ↓
   Flask App (/webhook)
        ↓
   Extract Signal Data
        ↓
   Idempotency Check (prevent duplicates)
        ↓
   Save to Database (Signal table)
        ↓
   Send to Telegram (if configured)
        ↓
   Process Trade (create/close positions)
        ↓
   Return Success Response
```

---

## 🧪 Testing Your Webhook

### **Method 1: TradingView Test**
1. Create an alert with your webhook URL
2. Click "Test" button in TradingView
3. Check your application logs

### **Method 2: Manual POST Request**

```powershell
# PowerShell
$body = @{
    action = "BUY"
    symbol = "BTCUSDT"
    price = 43250.50
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook" -Method POST -Body $body -ContentType "application/json"
```

```bash
# cURL
curl -X POST https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook \
  -H "Content-Type: application/json" \
  -d '{"action":"BUY","symbol":"BTCUSDT","price":43250.50}'
```

### **Method 3: Use Test Script**

```powershell
.\tools\post_webhook.py
```

---

## 📱 Telegram Integration (Optional)

To receive alerts in Telegram:

1. **Set Environment Variables** in `.env`:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

2. **Restart Application**

3. **Test**: Send a webhook, check Telegram for notification

---

## 📋 Monitoring Webhooks

### **Check Application Logs**

The Flask server logs all incoming webhooks:
```
Incoming webhook headers: {...}
Incoming webhook body: {"action":"BUY","symbol":"BTCUSDT",...}
Signal persisted: BUY BTCUSDT @ 43250.50
Telegram forward status: 200
```

### **Check Database**

```python
# Python
from src.database.session import SessionLocal
from src.models.base import Signal

session = SessionLocal()
signals = session.query(Signal).order_by(Signal.created_at.desc()).limit(10).all()
for sig in signals:
    print(f"{sig.action} {sig.symbol} @ {sig.price} - {sig.created_at}")
```

### **Check Saved Webhook**

Last webhook is saved to: `data/last_webhook.txt`

---

## 🔄 Restarting ngrok

If ngrok disconnects or you need a new URL:

```powershell
# Start ngrok
.\scripts\start_ngrok.ps1

# Check ngrok status
.\scripts\check_ngrok.ps1
```

**Note**: ngrok free tier generates a new URL each time. You'll need to update TradingView alerts with the new URL.

---

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | Receive TradingView alerts |
| `/api/trading/trades` | GET | List all trades |
| `/api/trading/positions` | GET | Get open positions |
| `/api/trading/instruments` | GET | List allowed instruments |
| `/health` | GET | Health check |

---

## 🐛 Troubleshooting

### **Webhook Not Receiving Alerts**

1. **Check ngrok is running**:
   ```powershell
   .\scripts\check_ngrok.ps1
   ```

2. **Check Flask server is running**:
   ```powershell
   # Should show "Running on http://127.0.0.1:5000"
   ```

3. **Test webhook manually**:
   ```powershell
   Invoke-RestMethod -Uri "https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook" -Method POST -Body '{"test":"data"}' -ContentType "application/json"
   ```

4. **Check TradingView alert logs** for errors

### **Duplicate Events**

The webhook has built-in idempotency:
- Each webhook generates a unique event key
- Duplicate requests are automatically ignored
- Check logs for "Duplicate event detected" message

### **Import Errors**

If you see "ModuleNotFoundError":
- Ensure all imports use `src.` prefix
- Check `trading_service.py` imports are fixed
- Restart Flask server to reload modules

---

## 📊 Database Tables

### **Signal Table**
Stores all incoming webhook signals:
- `id` - Unique identifier
- `source` - Always "webhook"
- `symbol` - Trading pair
- `action` - BUY or SELL
- `price` - Entry price
- `raw` - Raw webhook body
- `created_at` - Timestamp

### **IdempotencyKey Table**
Prevents duplicate processing:
- `key` - Unique event identifier
- `created_at` - First seen timestamp

### **Trade Table**
Stores executed trades:
- `symbol`, `action`, `entry_price`, `exit_price`
- `status` - OPEN or CLOSED
- `profit_loss` - P&L calculation

---

## 🚀 Start Everything

### **Terminal 1: Flask Server**
```powershell
python app.py
```

### **Terminal 2: ngrok Tunnel**
```powershell
.\scripts\start_ngrok.ps1
```

### **Or Use Start All Script**
```powershell
.\scripts\start_all.ps1
```

---

## 📚 Example TradingView Strategies

### **Simple Moving Average Crossover**

```pine
//@version=5
strategy("SMA Crossover", overlay=true)

fast = ta.sma(close, 20)
slow = ta.sma(close, 50)

if ta.crossover(fast, slow)
    strategy.entry("Long", strategy.long)
    alert('{"action":"BUY","symbol":"' + syminfo.ticker + '","price":' + str.tostring(close) + '}', alert.freq_once_per_bar_close)

if ta.crossunder(fast, slow)
    strategy.entry("Short", strategy.short)
    alert('{"action":"SELL","symbol":"' + syminfo.ticker + '","price":' + str.tostring(close) + '}', alert.freq_once_per_bar_close)
```

---

## 🎊 Summary

Your TradingView webhook integration is **COMPLETE and OPERATIONAL**!

- ✅ **Webhook endpoint**: `https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook`
- ✅ **Flask server**: Running on port 5000
- ✅ **ngrok tunnel**: Active and forwarding
- ✅ **Database**: Persisting signals
- ✅ **Telegram**: Ready (if configured)
- ✅ **Trade processing**: Integrated

**Next Steps**:
1. Create alerts in TradingView
2. Use the webhook URL above
3. Test with sample alerts
4. Monitor logs and database
5. Refine your trading strategy

---

**Important**: ngrok free tier URLs change on restart. For production, consider:
- ngrok paid plan (static domain)
- Cloud hosting (AWS, Azure, Heroku)
- VPS with static IP

---

**Created**: October 15, 2025  
**Webhook URL**: `https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook`  
**Status**: ✅ Active and Ready
