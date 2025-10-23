# Enhanced Logging Guide

## Overview
Comprehensive logging has been added throughout the Delta Exchange integration to help monitor what's happening at every step of the trading process.

## Logging Levels

The system uses Python's logging module with these levels:

- **INFO**: Normal operation events (signals received, orders placed, etc.)
- **WARNING**: Potential issues (price mismatches, duplicate events, etc.)
- **ERROR**: Failures that need attention (order failures, API errors, etc.)
- **DEBUG**: Detailed information for troubleshooting
- **EXCEPTION**: Caught exceptions with full stack traces

## Log Locations

### 1. Delta Exchange Service (`src/services/delta_exchange_service.py`)

#### Initialization
```
INFO: Initializing DeltaExchangeTrader...
INFO: Trading enabled: false
INFO: API key configured: True
INFO: API secret configured: True
INFO: ✅ Creating Delta Exchange client with provided credentials
INFO: ✅ Delta Exchange client initialized successfully
```

#### Price Verification
```
INFO: 🔍 Verifying price for BTCUSD: expected=$108000.00, tolerance=2.0%
DEBUG: Fetching orderbook for BTCUSD...
DEBUG: Orderbook retrieved: 50 buy orders, 50 sell orders
INFO: 📊 Market data for BTCUSD: Bid=$107979.50, Ask=$107980.50, Mid=$107980.00
INFO: ✅ Price verified for BTCUSD: signal=$108000.00, market=$107980.00, diff=0.02%
```

or on failure:
```
WARNING: ⚠️ Price verification FAILED for BTCUSD: expected $108000.00, current $105000.00 (diff: 2.86% > 2.0%)
```

#### Product ID Lookup
```
DEBUG: Looking up product ID for symbol: BTCUSD
INFO: ✅ Found product ID for BTCUSD via mapping: 27
```

or via API:
```
DEBUG: Symbol ETHUSD not in mapping, searching products API...
DEBUG: Searching 1264 products for ETHUSD...
INFO: ✅ Found product ID for ETHUSD via API search: 139
```

#### Order Placement (Dry Run)
```
INFO: 📤 Place order request: BUY 1 BTCUSD @ $108000.00
WARNING: 🔧 Trading is DISABLED - order will not be placed (dry run mode)
```

#### Order Placement (Live Trading)
```
INFO: 📤 Place order request: BUY 1 BTCUSD @ $108000.00
INFO: Step 1/3: Getting product ID for BTCUSD...
INFO: ✅ Product ID found: 27
INFO: Step 2/3: Verifying price for BTCUSD...
INFO: ✅ Price verified for BTCUSD: signal=$108000.00, market=$107980.00, diff=0.02%
INFO: Step 3/3: Placing order on Delta Exchange...
INFO: 📋 Order details: side=buy, size=1, price=$108000.00, product_id=27
INFO: ✅ ORDER PLACED SUCCESSFULLY!
INFO:    Order ID: 12345678
INFO:    Status: open
INFO:    Side: BUY
INFO:    Symbol: BTCUSD
INFO:    Size: 1
INFO:    Price: $108000.00
INFO:    Verified Market Price: $107980.00
```

#### Order Failures
```
ERROR: ❌ ORDER PLACEMENT FAILED!
ERROR:    Symbol: BTCUSD
ERROR:    Side: BUY
ERROR:    Price: $108000.00
ERROR:    Error: Unauthorized
```

### 2. Webhook Endpoint (`src/api/webhook.py`)

#### Incoming Webhook
```
INFO: ================================================================================
INFO: 📥 INCOMING WEBHOOK REQUEST
INFO: ================================================================================
INFO: Headers: {'Content-Type': 'application/json', 'X-Webhook-Secret': '...'}
INFO: Body: {"action":"buy","symbol":"BTCUSD","price":108000.0}
INFO: --------------------------------------------------------------------------------
DEBUG: Saved webhook body to data/last_webhook.txt
INFO: Extracting signal data from webhook...
INFO: Extracted signal: action=buy, symbol=BTCUSD, price=108000.0
```

#### Idempotency Check
```
DEBUG: Computing event key for idempotency check...
INFO: ✅ New event (not duplicate)
```

or for duplicates:
```
WARNING: ⚠️ Duplicate event detected: abc123def456
```

#### Signal Processing
```
INFO: 🔄 Processing trade signal...
INFO: ================================================================================
INFO: 🔄 PROCESSING TRADE SIGNAL
INFO: ================================================================================
INFO: Signal details: action=buy, symbol=BTCUSD, price=108000.0
DEBUG: Importing trading services...
INFO: Initializing trading manager...
INFO: Getting Delta Exchange trader...
INFO: Calling TradingManager.handle_signal: side=BUY, symbol=BTCUSD, price=108000.0
INFO: TradingManager result: action=opened, message=No existing trades - opened new BUY position
INFO: --------------------------------------------------------------------------------
INFO: Trade action determined: opened
```

#### Delta Exchange Integration
```
INFO: ================================================================================
INFO: 💹 PLACING ORDER ON DELTA EXCHANGE
INFO: ================================================================================
INFO: Order request: BUY BTCUSD @ $108000.0
[... price verification and order placement logs ...]
INFO: ================================================================================
INFO: ✅ DELTA EXCHANGE ORDER PLACED SUCCESSFULLY
INFO: ================================================================================
INFO: Order ID: 12345678
INFO: Status: open
INFO: Message: Order placed: buy 1 BTCUSD @ 108000.0
INFO: ================================================================================
```

or for dry run:
```
INFO: ================================================================================
INFO: 🔧 DELTA EXCHANGE TRADING DISABLED (DRY RUN)
INFO: ================================================================================
INFO: Message: Delta Exchange trading is disabled (set DELTA_TRADING_ENABLED=true to enable)
INFO: ================================================================================
```

#### Telegram Notification
```
DEBUG: Forwarding to Telegram...
INFO: ✅ Forwarded to Telegram
```

## Log Symbols

For easy scanning of logs:

- ✅ Success / Completed
- ❌ Error / Failed
- ⚠️ Warning / Skipped
- 🔧 Dry Run / Disabled
- 📥 Incoming Request
- 📤 Outgoing Request
- 🔄 Processing
- 💹 Trading Action
- 📊 Market Data
- 🔍 Verification
- 📈 Trade Opened
- 📋 Details

## Viewing Logs

### Console Output
Run the Flask server and watch real-time logs:
```bash
python app.py
```

### Test with Detailed Logging
```bash
python tools\test_delta_integration.py --full
```

### File Logging (Optional)
Add to your Flask app initialization:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
```

## Common Log Patterns

### Successful Trade Flow
```
📥 INCOMING WEBHOOK REQUEST
🔄 PROCESSING TRADE SIGNAL
✅ New event (not duplicate)
✅ Signal persisted to database
📈 Opened new BUY trade
💹 PLACING ORDER ON DELTA EXCHANGE
🔍 Verifying price: ✅ Price verified
📋 Order details: side=buy, size=1, price=$108000.00
✅ ORDER PLACED SUCCESSFULLY!
✅ Forwarded to Telegram
```

### Ignored Signal (Same Direction)
```
📥 INCOMING WEBHOOK REQUEST
🔄 PROCESSING TRADE SIGNAL
⚠️ Signal IGNORED: Same direction trade exists
No Delta Exchange order needed (action: ignored)
✅ Forwarded to Telegram
```

### Price Verification Failed
```
📥 INCOMING WEBHOOK REQUEST
🔄 PROCESSING TRADE SIGNAL
💹 PLACING ORDER ON DELTA EXCHANGE
🔍 Verifying price: ⚠️ Price verification FAILED
❌ DELTA EXCHANGE ORDER FAILED
Message: Price verification failed: expected $108000.00, current $105000.00 (diff: 2.86% > 2.0%)
```

### Duplicate Event
```
📥 INCOMING WEBHOOK REQUEST
⚠️ Duplicate event detected: abc123def456
[Request terminated - no processing]
```

## Troubleshooting with Logs

### Issue: Orders Not Being Placed

Look for:
```
🔧 Trading is DISABLED - order will not be placed (dry run mode)
```
**Solution**: Set `DELTA_TRADING_ENABLED=true` in `.env`

### Issue: Price Verification Failing

Look for:
```
⚠️ Price verification FAILED for BTCUSD: expected $108000.00, current $105000.00 (diff: 2.86% > 2.0%)
```
**Solution**: Check if TradingView signal price is stale or adjust tolerance

### Issue: Symbol Not Found

Look for:
```
⚠️ Product ID not found for symbol: XXXUSD
```
**Solution**: Add symbol mapping in `get_product_id()` method

### Issue: API Authentication Failed

Look for:
```
❌ ORDER PLACEMENT FAILED!
Error: Unauthorized
```
**Solution**: Check API credentials and IP whitelisting

### Issue: Missing Signal Data

Look for:
```
⚠️ Incomplete signal data, skipping trade processing
Missing: action=True, symbol=True, price=False
```
**Solution**: Check TradingView webhook format

## Log Analysis

### Count Orders Placed Today
```bash
grep "ORDER PLACED SUCCESSFULLY" trading.log | wc -l
```

### Find Failed Orders
```bash
grep "ORDER PLACEMENT FAILED" trading.log
```

### Check Price Verification Issues
```bash
grep "Price verification FAILED" trading.log
```

### Monitor Duplicate Events
```bash
grep "Duplicate event detected" trading.log
```

## Debug Mode

To enable more detailed DEBUG logs, set in your Flask app:
```python
import logging
logging.getLogger('src.services.delta_exchange_service').setLevel(logging.DEBUG)
logging.getLogger('src.api.webhook').setLevel(logging.DEBUG)
```

This will show additional details like:
- Orderbook fetch operations
- Product API searches
- Event key computations
- Database operations

## Performance Monitoring

Key timing points logged:
1. Webhook received
2. Signal extracted
3. Trade processed
4. Price verified
5. Order placed
6. Telegram notified

Watch for gaps between these to identify bottlenecks.

## Log Cleanup

Logs can grow large. Consider:
- Using rotating file handlers
- Setting up log aggregation (ELK stack, CloudWatch, etc.)
- Archiving old logs periodically
- Filtering noise in production (set level to WARNING)

---

**Remember**: In production, consider setting log level to WARNING to reduce noise while keeping critical information visible.
