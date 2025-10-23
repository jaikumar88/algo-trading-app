# 🚀 Quick Start - Live Trading

## Current Status
- ✅ Delta Exchange API: Connected
- ✅ Price Verification: Working ($108,038 BTCUSD)
- ✅ Enhanced Signal Logic: Active
- ✅ Telegram Notifications: Configured
- 🔧 Trading Mode: DRY RUN (safe testing)

## Enable Live Trading (3 Steps)

### 1. Edit .env
```bash
DELTA_TRADING_ENABLED=true
```

### 2. Restart Server
```bash
quick_start.cmd
```

### 3. Monitor
Watch console & Telegram for order confirmations

## Trading Logic

| Scenario | Action |
|----------|--------|
| BUY signal + existing BUY | ⚠️ IGNORED |
| SELL signal + existing SELL | ⚠️ IGNORED |
| BUY signal + existing SELL | 🔄 CLOSE SELL + OPEN BUY |
| SELL signal + existing BUY | 🔄 CLOSE BUY + OPEN SELL |
| First signal (no trades) | 📈 OPEN NEW |

## Test Commands
```bash
# Full integration test
python tools\test_delta_integration.py --full

# Check live price
python tools\check_btc_price.py

# View balance
python tools\TradingClient.py
```

## Webhook URL
```
https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook
```

## Current Symbols
- BTCUSD → Product ID 27 ✅
- ETHUSD → Product ID 139 ✅
- BTCUSDT → Maps to BTCUSD ✅

## Order Details
- Type: Limit Order
- Quantity: 1 (fixed)
- Price: Verified against live orderbook
- Tolerance: ±2%

## Safety
- Price must match market within 2%
- Fixed quantity of 1 per order
- Full error handling & logging
- Dry run mode available

---
**Balance**: $1.18 USD | **Ready**: ✅ | **Mode**: 🔧 Dry Run
