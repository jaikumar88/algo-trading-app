#!/usr/bin/env python3
import os
import sys
import json
import requests

ENV_PATH = r"e:\workspace\python\rag-project\.env"


def read_env(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, 'r', encoding='utf-8') as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            if '=' in ln:
                k, v = ln.split('=', 1)
                out[k.strip()] = v.strip().strip("'\" ")
    return out


def main():
    env = read_env(ENV_PATH)
    token = env.get('TELEGRAM_BOT_TOKEN') or os.environ.get('TELEGRAM_BOT_TOKEN')
    chat = env.get('TELEGRAM_CHAT_ID') or os.environ.get('TELEGRAM_CHAT_ID')
    if not token:
        print('ERROR: TELEGRAM_BOT_TOKEN not found in .env or environment')
        sys.exit(2)
    if not chat:
        print('ERROR: TELEGRAM_CHAT_ID not found in .env or environment')
        sys.exit(3)
    # If chat looks like a username and doesn't start with @, add @
    if not chat.startswith('@') and not chat.lstrip('-').isdigit():
        chat = '@' + chat
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat, 'text': 'Verification message: test from send_tg_test.py'}
    try:
        r = requests.post(url, json=payload, timeout=10)
        print('status_code=', r.status_code)
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print('response_text=', r.text)
    except Exception as e:
        print('Request failed:', e)
        sys.exit(4)


if __name__ == '__main__':
    main()
