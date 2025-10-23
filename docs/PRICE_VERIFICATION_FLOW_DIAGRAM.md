# Real-Time Price Verification Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                        TRADINGVIEW SIGNAL                          │
│                   {"action": "BUY", "symbol": "BTCUSD",            │
│                         "price": 108450.0}                         │
└────────────────────┬───────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────────┐
│                       WEBHOOK ENDPOINT                             │
│                     (src/api/webhook.py)                           │
│                                                                    │
│  📥 INCOMING WEBHOOK REQUEST                                       │
│  - Parse JSON data                                                 │
│  - Extract: action, symbol, price                                  │
│  - Check for duplicates                                            │
│  - Persist to database                                             │
└────────────────────┬───────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────────┐
│                    🔄 PROCESS TRADE SIGNAL                         │
└────────────────────┬───────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────────┐
│             📊 STEP 1: VERIFY REAL-TIME PRICE                      │
│                  (ADDED IN THIS UPDATE!)                           │
│                                                                    │
│  1. Initialize Delta Exchange client                               │
│  2. Call: verify_price(symbol, expected_price)                     │
│     ↓                                                              │
│  3. Fetch orderbook from Delta Exchange                            │
│     GET https://api.delta.exchange/orderbook?symbol=BTCUSD        │
│     ↓                                                              │
│  4. Extract best bid & ask                                         │
│     best_bid = 108449.0                                            │
│     best_ask = 108451.0                                            │
│     ↓                                                              │
│  5. Calculate mid-price                                            │
│     mid_price = (108449.0 + 108451.0) / 2 = 108450.0              │
│     ↓                                                              │
│  6. Compare prices                                                 │
│     difference = |108450.0 - 108450.0| / 108450.0                 │
│                = 0.00% < 2% tolerance ✅                           │
└────────────────────┬───────────────────────────────────────────────┘
                     │
                     ├─────────── VERIFICATION PASSED ────────────┐
                     │                                             │
                     ▼                                             │
        ┌────────────────────────────┐              ┌─────────────┴─────────────┐
        │  ❌ VERIFICATION FAILED     │              │  ✅ VERIFICATION PASSED    │
        │                            │              │                           │
        │  - Log detailed reason     │              │  - Log success            │
        │  - Return 'blocked' action │              │  - Continue processing    │
        │  - No trade opened         │              │                           │
        │  - Notify Telegram         │              │                           │
        └────────────┬───────────────┘              └─────────────┬─────────────┘
                     │                                             │
                     ▼                                             ▼
        ┌────────────────────────────┐              ┌─────────────────────────────┐
        │  🚫 TELEGRAM NOTIFICATION   │              │  📈 HANDLE SIGNAL           │
        │                            │              │                             │
        │  🟢 BUY 🚫 BLOCKED         │              │  - Check open positions     │
        │                            │              │  - Apply trade logic        │
        │  🚫 Price Verification     │              │  - Determine action:        │
        │      Failed                │              │    • opened                 │
        │  Signal: $105000.0         │              │    • closed_and_opened      │
        │  Market: $108450.00        │              │    • ignored                │
        │  ❌ Trade blocked           │              │                             │
        └────────────────────────────┘              └─────────────┬───────────────┘
                                                                  │
                                                                  ▼
                                                     ┌─────────────────────────────┐
                                                     │  💹 PLACE ORDER ON          │
                                                     │     DELTA EXCHANGE          │
                                                     │                             │
                                                     │  - side: BUY                │
                                                     │  - symbol: BTCUSD           │
                                                     │  - price: 108450.0          │
                                                     │  - size: 1                  │
                                                     │                             │
                                                     │  ✅ Order placed            │
                                                     │  Order ID: 12345678         │
                                                     └─────────────┬───────────────┘
                                                                  │
                                                                  ▼
                                                     ┌─────────────────────────────┐
                                                     │  📱 TELEGRAM NOTIFICATION    │
                                                     │                             │
                                                     │  🟢 BUY 📈 OPENED           │
                                                     │                             │
                                                     │  💹 Delta Exchange Order    │
                                                     │     Placed                  │
                                                     │  Order ID: 12345678         │
                                                     │  Verified Price: 108450.00  │
                                                     └─────────────────────────────┘
```

## Key Changes

### Before This Update ❌
```
Signal → Extract Data → Handle Signal → Place Order
                         (No price check!)
```

### After This Update ✅
```
Signal → Extract Data → ✅ VERIFY PRICE → Handle Signal → Place Order
                         (Real-time check!)
                         
                         If price mismatch:
                         🚫 BLOCK TRADE
                         (No order placed)
```

## Why This is Important

1. **Prevents Stale Signals**
   - TradingView might send delayed alerts
   - Market moves fast
   - Price from 5 minutes ago is outdated

2. **Protects Against Slippage**
   - Signal says $108,000
   - Market is at $110,000
   - 2% difference = Don't trade!

3. **Safety Net**
   - Double-check before every trade
   - Better to miss a trade than take a bad one
   - No assumptions, only verification

## What You'll See in Logs

### NEW Section (Added)
```
================================================================================
📊 STEP 1: VERIFYING REAL-TIME PRICE FROM DELTA EXCHANGE
================================================================================
Signal Price: $108450.0
Checking current market price for BTCUSD...
🔍 Verifying price for BTCUSD: expected=$108450.00, tolerance=2.0%
📊 Market data for BTCUSD: Bid=$108449.00, Ask=$108451.00, Mid=$108450.00
✅ Price verified for BTCUSD: signal=$108450.00, market=$108450.00, diff=0.00%
================================================================================
✅ PRICE VERIFICATION PASSED
================================================================================
```

This section appears **BEFORE** any trade processing happens!
