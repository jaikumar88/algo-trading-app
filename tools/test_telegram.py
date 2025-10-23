import os
from dotenv import load_dotenv
import requests

load_dotenv()
TG_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TG_CHAT = os.getenv('TELEGRAM_CHAT_ID')

print('Token present:', bool(TG_TOKEN))
print('Chat ID present:', bool(TG_CHAT))

if not TG_TOKEN:
    print('No TELEGRAM_BOT_TOKEN found in environment.')
    raise SystemExit(1)

getme_url = f'https://api.telegram.org/bot{TG_TOKEN}/getMe'
resp = requests.get(getme_url, timeout=10)
print('getMe status:', resp.status_code)
print(resp.json())

# Try sendMessage
send_url = f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage'
payload = {
    'chat_id': TG_CHAT,
    'text': 'Test message from RAG Trading System (local test).',
}
resp2 = requests.post(send_url, json=payload, timeout=10)
print('sendMessage status:', resp2.status_code)
print(resp2.json())
