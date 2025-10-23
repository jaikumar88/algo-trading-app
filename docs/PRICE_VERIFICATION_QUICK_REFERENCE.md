# Quick Reference: Real-Time Price Verification

## What to Look For in Logs

### When Flask App Starts
```
✅ Trade monitor started
🚀 TRADE MONITOR STARTED
```

### When Webhook Receives Signal
```
================================================================================
📥 INCOMING WEBHOOK REQUEST
================================================================================
```

### When Price is Being Checked (YOU WILL SEE THIS NOW!)
```
================================================================================
📊 STEP 1: VERIFYING REAL-TIME PRICE FROM DELTA EXCHANGE
================================================================================
Signal Price: $108450.0
Checking current market price for BTCUSD...
🔍 Verifying price for BTCUSD: expected=$108450.00, tolerance=2.0%
📊 Market data for BTCUSD: Bid=$108449.00, Ask=$108451.00, Mid=$108450.00
```

### When Price Verification PASSES ✅
```
✅ Price verified for BTCUSD: signal=$108450.00, market=$108450.00, diff=0.00%
================================================================================
✅ PRICE VERIFICATION PASSED
================================================================================
✅ Proceeding with trade processing...
```

### When Price Verification FAILS 🚫
```
⚠️ Price verification FAILED for BTCUSD: diff=3.28% > 2.0%
================================================================================
❌ PRICE VERIFICATION FAILED - TRADE BLOCKED
================================================================================
❌ Trade will NOT be opened without price confirmation
```

## Telegram Message Examples

### ✅ Trade Opened (Price Verified)
```
📊 TradingView Signal

🟢 BUY 📈 OPENED
_Opened new BUY position_

💹 Delta Exchange Order Placed
Order ID: `12345678`
Status: `open`
Verified Price: `108450.00`

Symbol: `BTCUSD`
Price: `108450.0`
```

### 🚫 Trade Blocked (Price Mismatch)
```
📊 TradingView Signal

🟢 BUY 🚫 BLOCKED

🚫 Price Verification Failed
Signal Price: `$105000.0`
Market Price: `$108450.00`
❌ Trade blocked for safety

_Price verification failed: Price mismatch..._

Symbol: `BTCUSD`
Price: `105000.0`
```

## Quick Commands

### Start Flask App
```bash
python app.py
```

### Test Price Verification
```bash
python tools\test_webhook_price_verification.py
```

### Send Manual Test Signal
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"action":"BUY","symbol":"BTCUSD","price":108450.0}'
```

## Key Points

1. **Every Signal is Verified** ✅
   - No exceptions
   - Happens before trade logic
   - Blocks trades if price doesn't match

2. **Tolerance is 2%** 📊
   - Signal price vs market price
   - Adjustable if needed
   - Protects against slippage

3. **Full Logging** 📝
   - See every price check
   - Clear pass/fail indicators
   - Detailed comparison data

4. **Safety First** 🛡️
   - Failed verification = NO TRADE
   - No assumptions
   - Better safe than sorry

## Monitoring Checklist

- [ ] Flask app running
- [ ] Logs showing webhook requests
- [ ] Price verification step visible
- [ ] Pass/fail status clear
- [ ] Telegram notifications working
- [ ] Blocked trades showing correctly

---

**Ready to Test!** 🚀

Send a test signal and watch for the price verification logs!
