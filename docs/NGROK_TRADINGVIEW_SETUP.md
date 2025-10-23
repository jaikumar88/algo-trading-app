# TradingView Webhook Setup with ngrok

## 🚀 Your Webhook is Now Live!

**Public Webhook URL**: `https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook`

## TradingView Alert Setup

### 1. Create Alert in TradingView
1. Open TradingView and go to your chart
2. Click the "Alert" button (bell icon)
3. Set your alert conditions (price, indicators, etc.)
4. In the "Notifications" tab, check "Webhook URL"

### 2. Configure Webhook Settings
```
Webhook URL: https://uncurdling-joane-pantomimical.ngrok-free.dev/webhook
```

### 3. Alert Message Format
Use this JSON format in the "Message" field:

#### Basic Format:
```json
{
  "action": "{{strategy.order.action}}",
  "symbol": "{{ticker}}",
  "price": "{{close}}",
  "volume": "1.0",
  "timestamp": "{{time}}"
}
```

#### Advanced Format with Stop Loss/Take Profit:
```json
{
  "action": "{{strategy.order.action}}",
  "symbol": "{{ticker}}",
  "price": "{{close}}",
  "volume": "1.0",
  "stop_loss": "{{close * 0.98}}",
  "take_profit": "{{close * 1.02}}",
  "timestamp": "{{time}}",
  "timeframe": "{{interval}}",
  "exchange": "{{exchange}}"
}
```

#### Text Format (Alternative):
```
{{strategy.order.action}} {{ticker}} at {{close}}
```

## Testing Your Setup

### 1. Monitor ngrok Traffic
- Visit: http://127.0.0.1:4040
- This shows all incoming requests to your webhook

### 2. Check Your Logs
- Flask logs: `flask_stderr.log` and `flask_stdout.log`
- Last webhook data: `data/last_webhook.txt`

### 3. Test Telegram Integration
Your webhook automatically forwards signals to Telegram if configured with:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Current Status

✅ Flask server running on port 5000  
✅ ngrok tunnel active  
✅ Webhook endpoint accessible  
✅ Telegram integration configured  

## Important Notes

1. **Keep ngrok running**: The tunnel only works while ngrok is active
2. **Free ngrok limitations**: 
   - URL changes when restarted
   - Rate limits apply
   - Update TradingView webhook URL if ngrok restarts

3. **Security**: 
   - Set `WEBHOOK_SECRET` in your `.env` for additional security
   - Use the secret in TradingView webhook URL: `?secret=your_secret`

## Troubleshooting

### If alerts aren't received:
1. Check ngrok web interface for incoming requests
2. Verify TradingView webhook URL is correct
3. Check Flask server logs for errors
4. Ensure alert conditions are triggered

### If Telegram messages aren't sent:
1. Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`
2. Test with: `python tools/test_telegram.py`
3. Check bot permissions and chat access

## Next Steps

1. Create your first TradingView alert with the webhook URL
2. Monitor the ngrok interface for incoming requests
3. Check Telegram for forwarded messages
4. Verify signal data in your database via `/api/trading/signals`

Happy Trading! 🎯