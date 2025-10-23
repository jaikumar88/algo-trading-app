# Delta Exchange Live Trading Integration

## Overview
The system now integrates with Delta Exchange API to place real orders when TradingView signals are received.

## Features
- ✅ Real-time price verification against Delta Exchange orderbook
- ✅ Automatic order placement with quantity = 1
- ✅ Limit orders at verified market price
- ✅ Enhanced Telegram notifications with order status
- ✅ Safe dry-run mode for testing
- ✅ Symbol mapping (BTCUSD, ETHUSD, etc.)

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Delta Exchange API Credentials
DELTA_API_KEY=j2ydI3WbKAuIF6GrXJhUO8y05qknh6
DELTA_API_SECRET=vY13i5LGd3v3s6TWnRZy9fvdjK1HvfiwgK6SjdKjJMROjpIgeeglrLXSN3MK

# Enable/Disable Live Trading
DELTA_TRADING_ENABLED=false  # Set to 'true' to enable live trading

# Telegram Bot (for notifications)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### IP Whitelisting
Ensure these IPs are whitelisted on Delta Exchange:
- IPv4: `72.221.33.241`
- IPv6: `2600:8804:9c09:9500:dc89:8c92:ed56:cbc0`

## How It Works

### 1. Signal Received
TradingView webhook sends signal:
```json
{
  "action": "buy",
  "symbol": "BTCUSD",
  "price": 108000.0,
  "size": 1
}
```

### 2. Enhanced Signal Handling
The system applies smart logic:
- **Same direction signal**: IGNORED (no action taken)
- **Opposite direction signal**: CLOSE existing trade + OPEN new trade
- **No existing trade**: OPEN new trade

### 3. Delta Exchange Integration
If action is `opened` or `closed_and_opened`:

a) **Symbol Mapping**
   - Maps TradingView symbol to Delta Exchange product ID
   - Example: BTCUSD → Product ID 27

b) **Price Verification**
   - Gets current orderbook from Delta Exchange
   - Calculates mid-price: `(best_bid + best_ask) / 2`
   - Verifies signal price within 2% tolerance
   - If price mismatch > 2%, order rejected

c) **Order Placement**
   - Places limit order at verified price
   - Quantity: 1 (as specified)
   - Side: buy or sell
   - Returns order ID and status

### 4. Telegram Notification
Enhanced message includes:
```
📊 TradingView Signal

🟢 BUY 📈 OPENED
Trade opened: buy BTCUSD @ 108000.0

💹 Delta Exchange Order Placed
Order ID: 12345678
Status: open
Verified Price: 108313.50

Symbol: BTCUSD
Price: 108000.0
Size: 1
```

## Trading Flow

```
TradingView Signal
       ↓
Webhook Endpoint (/webhook)
       ↓
Enhanced Signal Handler
(check existing trades)
       ↓
[IGNORED] → No action
       ↓
[OPENED/SWITCHED] → Delta Exchange
       ↓
Price Verification
(get orderbook, verify within 2%)
       ↓
Place Limit Order
(size=1, limit_price)
       ↓
Telegram Notification
(order ID, status)
```

## Testing

### Test 1: Delta Exchange Trader
```bash
python tools\test_delta_integration.py
```

Output:
- Trading system status
- Product ID lookup (BTCUSD, ETHUSD)
- Price verification test
- Order placement (dry run if disabled)

### Test 2: Full Webhook Integration
```bash
python tools\test_delta_integration.py --full
```

This simulates TradingView signals and processes them through the entire flow.

### Test 3: Manual Signal
Send POST request to webhook:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "buy",
    "symbol": "BTCUSD",
    "price": 108000.0,
    "size": 1
  }'
```

## Safety Features

### 1. Dry Run Mode
When `DELTA_TRADING_ENABLED=false`:
- No orders placed on Delta Exchange
- All logic executed (price verification, etc.)
- Logs show "🔧 Trading Disabled"

### 2. Price Verification
Orders only placed if:
- Current market price retrieved successfully
- Signal price within 2% of market price
- Product exists on Delta Exchange

### 3. Error Handling
- Missing credentials → Client not initialized
- Invalid symbol → Order rejected
- Price mismatch → Order rejected with details
- API errors → Logged and reported to Telegram

## Symbol Mapping

Currently supported:
- `BTCUSD` → Product ID 27 (Bitcoin Perpetual)
- `ETHUSD` → Product ID 139 (Ethereum Perpetual)
- `BTCUSDT` → Maps to BTCUSD
- `ETHUSDT` → Maps to ETHUSD

To add more symbols:
1. Use `tools/test_products.py` to find product ID
2. Add mapping in `delta_exchange_service.py`, `get_product_id()` method

## Order Details

- **Order Type**: Limit Order
- **Quantity**: 1 (fixed)
- **Price**: Limit price at verified market price
- **Time in Force**: GTC (Good Till Cancel) - default
- **Product Type**: Perpetual futures

## Monitoring

### Logs
Check Flask logs for order status:
```
✅ Delta Exchange order placed: Order placed: buy 1 BTCUSD @ 108000.0
```

### Telegram
Real-time notifications include:
- Signal action (BUY/SELL)
- Enhanced status (OPENED/IGNORED/SWITCHED)
- Order ID and status
- Verified price

### Database
Orders tracked in `trades` table:
- Symbol, side, price, status
- Timestamps for open/close
- Position tracking

## Troubleshooting

### Order Not Placed
1. Check `DELTA_TRADING_ENABLED=true`
2. Verify API credentials in `.env`
3. Check IP whitelisting
4. Review logs for error messages

### Price Verification Failed
- Signal price differs > 2% from market
- Check TradingView signal price accuracy
- Adjust tolerance in `verify_price()` if needed

### Symbol Not Found
- Product may not exist on Delta Exchange
- Add symbol mapping in `get_product_id()`
- Use test_products.py to search

### Insufficient Balance
- Check wallet: `python tools/TradingClient.py`
- Current balance: $1.18 USD
- May need to deposit more funds

## Production Checklist

Before enabling live trading:

- [ ] API credentials configured
- [ ] IPs whitelisted on Delta Exchange
- [ ] Sufficient balance in wallet
- [ ] Test with dry run mode
- [ ] Verify signal handling logic
- [ ] Test price verification
- [ ] Confirm symbol mappings
- [ ] Enable Telegram notifications
- [ ] Set `DELTA_TRADING_ENABLED=true`
- [ ] Monitor first few signals closely

## Files Modified

- `src/services/delta_exchange_service.py` - New Delta Exchange trader
- `src/api/webhook.py` - Integrated order placement
- `tools/test_delta_integration.py` - Integration tests
- `docs/DELTA_EXCHANGE_INTEGRATION.md` - This file

## Next Steps

1. **Test in dry run mode** - Verify all logic works
2. **Enable with small quantity** - Already set to 1
3. **Monitor first signals** - Check Telegram notifications
4. **Add more symbols** - Expand symbol mapping
5. **Implement position sizing** - Calculate based on balance
6. **Add stop loss/take profit** - Future enhancement
