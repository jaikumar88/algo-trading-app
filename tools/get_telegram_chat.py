#!/usr/bin/env python3
import os
import sys
import requests
import json

ENV_PATH = r"e:\workspace\python\rag-project\.env"


def read_token_from_env_file(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            if ln.upper().startswith("TELEGRAM_BOT_TOKEN="):
                _, val = ln.split("=", 1)
                return val.strip().strip('"').strip("'")
    return None


def env_has_chat_id(path):
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8") as fh:
        for ln in fh:
            if ln.strip().upper().startswith("TELEGRAM_CHAT_ID="):
                return True
    return False


def append_chat_id(path, chat_id):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(f"\nTELEGRAM_CHAT_ID={chat_id}\n")


if __name__ == '__main__':
    token = read_token_from_env_file(ENV_PATH) or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not found in .env or environment")
        sys.exit(2)
    print("Using token from .env or env (redacted):", token[:10] + "...")

    try:
        resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", params={"limit": 50}, timeout=10)
        resp.raise_for_status()
        j = resp.json()
    except Exception as e:
        print("ERROR calling getUpdates:", e)
        sys.exit(3)

    results = j.get("result") or []
    if not results:
        print("No updates returned. Have any users messaged the bot? Please send a message to the bot chat first.")
        sys.exit(4)

    # find the most recent chat id from the updates
    chat_id = None
    for upd in reversed(results):
        for key in ("message", "edited_message", "channel_post", "edited_channel_post"):
            if key in upd and upd[key] and "chat" in upd[key]:
                chat = upd[key]["chat"]
                chat_id = chat.get("id")
                break
        if chat_id:
            break

    if not chat_id:
        print("Could not detect a chat id in updates. Dumping latest update for inspection:")
        print(json.dumps(results[-1], indent=2))
        sys.exit(5)

    print("Detected chat_id:", chat_id)

    # append to .env if missing
    if not env_has_chat_id(ENV_PATH):
        try:
            append_chat_id(ENV_PATH, chat_id)
            print(f"Appended TELEGRAM_CHAT_ID={chat_id} to {ENV_PATH}")
        except Exception as e:
            print("Failed to append to .env:", e)
    else:
        print(".env already contains TELEGRAM_CHAT_ID; not modifying file.")

    # send a verification message
    try:
        send = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat_id, "text": "Test message from webhook forwarder: verification"}, timeout=10)
        print("sendMessage status:", send.status_code, send.text)
    except Exception as e:
        print("Failed to send verification message:", e)
        sys.exit(6)

    print("Done.")
