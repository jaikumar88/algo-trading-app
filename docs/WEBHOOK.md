# Webhook for TradingView (project: rag-project)

This document explains how to configure TradingView (or any external service) to POST alerts to your local Flask `/webhook` endpoint and how to test it locally.

## Local webhook URL(s)

- Default Flask webhook (when you run the app locally):
  - http://127.0.0.1:5000/webhook

- Lightweight forward webhook (if you started it via `telegram_bot.start_forward_webhook()`):
  - http://127.0.0.1:8765/forward

## Secret verification

If you set `WEBHOOK_SECRET` in your `.env` or environment, the webhook endpoint requires the secret. Two ways to provide it:

1) Header: set header `X-WEBHOOK-SECRET: <your-secret>`
2) Query param (useful when the sender cannot add headers): append `?secret=<your-secret>` to the URL

TradingView alerts can be configured to use the query param approach by including the secret in the webhook URL.

## Example TradingView alert body

Use one of these templates as the alert message. Your Flask endpoint accepts JSON or plain text.

Simple JSON payload:

{
  "message": "BUY BTC at 30000 size 0.5 LIMIT SL 29500 TP 31000"
}

Plain text body:

BUY BTC at 30000 size 0.5 LIMIT SL 29500 TP 31000

## Example TradingView webhook URL

If you run Flask locally and use ngrok to expose it, the URL will look like:

https://<ngrok-id>.ngrok.io/webhook

If you set `WEBHOOK_SECRET=sekret123`, you can configure TradingView with either:

- Header approach (in TradingView's webhook settings, add a custom header if available):
  - Header: `X-WEBHOOK-SECRET: sekret123`
- Query param approach (paste the full url in TradingView):
  - `https://<ngrok-id>.ngrok.io/webhook?secret=sekret123`

## Expose local server with ngrok

1) Start your Flask app locally (project root):

```powershell
# activate venv (optional)
. .venv\Scripts\Activate.ps1
# start flask app
python -u app.py
```

2) Start ngrok forwarding port 5000:

```powershell
ngrok http 5000
```

3) Copy the generated `https://...` URL from ngrok and add `/webhook` at the end (and `?secret=` if using query secret).

### Quick helper (Windows PowerShell)

There's a helper script `start_ngrok.ps1` in the project root that will attempt to start ngrok and print the public URL for the tunnel (it looks for tunnels on the ngrok local API at http://127.0.0.1:4040). Usage:

```powershell
# from project root
.\start_ngrok.ps1 -Port 5000
```

The script will print the public URL, e.g. `https://abcd1234.ngrok.io/webhook` which you can paste into TradingView. If `start_ngrok.ps1` fails to detect ngrok, run `ngrok http 5000` manually.

## Quick local test (PowerShell)

Simple JSON POST to local webhook:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/webhook' -Method Post -ContentType 'application/json' -Body (@{message='BUY BTC at 30000 size 0.5 LIMIT SL 29500 TP 31000'} | ConvertTo-Json)
```

If `WEBHOOK_SECRET` is set to `sekret123`:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/webhook?secret=sekret123' -Method Post -ContentType 'application/json' -Body (@{message='BUY BTC at 30000 size 0.5 LIMIT SL 29500 TP 31000'} | ConvertTo-Json)
```

Or set header explicitly:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/webhook' -Method Post -ContentType 'application/json' -Headers @{ 'X-WEBHOOK-SECRET' = 'sekret123' } -Body (@{message='BUY BTC at 30000 size 0.5 LIMIT SL 29500 TP 31000'} | ConvertTo-Json)
```

## Notes

- The webhook endpoint will attempt to parse the message using the project's `analyze_trade_text` heuristic. If `GOOGLE_API_KEY` is configured and the `gemini_client` is available, it will attempt to parse with Vision+Gemini and validate the response before forwarding.
- If `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set, the webhook will also forward the parsed summary to your Telegram chat as a convenience.

If you'd like, I can add a sample TradingView alert JSON (with placeholders) you can paste into TradingView's alert dialog, or add HMAC verification for stronger security.

## Ready-to-copy TradingView alert templates

Paste one of these into TradingView's alert `Message` box.

1) Simple JSON payload (recommended if TradingView supports Content-Type: application/json):

```json
{
  "message": "BUY BTC at 30000 size 0.5 LIMIT SL 29500 TP 31000",
  "symbol": "BTCUSDT",
  "source": "TradingView"
}
```

2) Plain text payload (if you prefer):

```
BUY BTC at 30000 size 0.5 LIMIT SL 29500 TP 31000
```

3) Pine script example (in TradingView Pine) to include dynamic fields. Put this `alert()` call in your strategy or study:

```pinescript
// Example: send a formatted alert when condition triggers
//@version=5
indicator("Example Alert", overlay=true)
cond = ta.crossover(ta.sma(close, 9), ta.sma(close, 21))
if cond
    message = '{"message":"BUY ' + syminfo.ticker + ' at ' + str.tostring(close) + ' size 0.1 LIMIT","symbol":"' + syminfo.ticker + '","source":"TradingView"}'
    alert(message, alert.freq_once_per_bar_close)
```

Notes:
- If TradingView doesn't support setting custom headers for the webhook, use the `?secret=` query parameter on the webhook URL (see above) to provide `WEBHOOK_SECRET`.
- TradingView's alert dialog `Webhook URL` field expects a single URL; paste the ngrok URL + `/webhook` (and `?secret=` if needed).
