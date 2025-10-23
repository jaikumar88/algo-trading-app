import requests
import json

url = "http://127.0.0.1:5000/webhook"
payload = {"message": "TEST forward to tg (final verification)"}
try:
    r = requests.post(url, json=payload, timeout=10)
    print('status_code=', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print('response_text=', r.text)
except Exception as e:
    print('Request failed:', e)
