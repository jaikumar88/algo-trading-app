import os
import logging
from dotenv import load_dotenv
import sys
import json
from telegram.ext import CommandHandler
from gemini_client import GOOGLE_API_KEY

try:
    from telegram import Update
    from telegram.ext import (
        ApplicationBuilder,
        ContextTypes,
        MessageHandler,
        filters,
    )
    _TELEGRAM_AVAILABLE = True
except Exception:
    # Allow importing this module without having python-telegram-bot installed.
    Update = None  # type: ignore
    ApplicationBuilder = None  # type: ignore
    ContextTypes = None  # type: ignore
    MessageHandler = None  # type: ignore
    filters = None  # type: ignore
    _TELEGRAM_AVAILABLE = False

load_dotenv()

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
# If no handlers are configured (e.g., when module imported), add a
# stream handler and a rotating file handler so messages are visible
# both in-terminal and in a log file for background runs.
if not LOG.handlers:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    LOG.addHandler(sh)
    try:
        fh = logging.FileHandler("telegram_bot.log", encoding="utf-8")
        fh.setFormatter(fmt)
        LOG.addHandler(fh)
    except Exception:
        # If file handler can't be created (permissions etc.), continue
        LOG.debug("Could not create file handler for telegram_bot.log")


def analyze_trade_text(text: str) -> str:
    """Robust analyzer that extracts structured trade fields from text.

    Returns a short, human-friendly summary string. The returned string is
    either a concise detected-trade summary or a short excerpt if nothing is
    found.
    """
    import re

    s = (text or "").upper()
    # normalize common OCR errors: replace weird quotes, multiple spaces
    s = re.sub(r"[\u2018\u2019\u201c\u201d]", "'", s)
    s = re.sub(r"[^A-Z0-9\./:\s@,\-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    # intent
    intent = None
    if re.search(r"\bBUY\b", s):
        intent = "BUY"
    elif re.search(r"\bSELL\b", s):
        intent = "SELL"

    # symbol: prefer a whitelist of common symbols to avoid OCR/noise
    sym = None
    # common crypto symbols (uppercase) - small whitelist to reduce false positives
    KNOWN_SYMBOLS = {
        'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'LTC', 'LINK', 'MATIC',
        'AVAX', 'DOGE', 'ATOM', 'FTM', 'TRX', 'EOS', 'ALGO', 'UNI', 'AAVE'
    }
    # Try to find explicit forms like BTC/USDT or BTCUSDT first
    sym_m = re.search(r"\b([A-Z]{3,6}(?:/[A-Z]{3,6})?)\b", s)
    if sym_m:
        candidate = sym_m.group(1)
        # normalize combined forms
        cand_base = candidate.split('/')[0]
        if cand_base in KNOWN_SYMBOLS:
            sym = candidate
    if not sym:
        # try combined like BTCUSDT or standalone token; prefer known symbols
        for token in re.findall(r"\b[A-Z]{3,7}\b", s):
            # skip obvious keywords
            if token in ('BUY', 'SELL', 'ORDER', 'PRICE', 'SIZE', 'SL', 'TP', 'LIMIT', 'MARKET'):
                continue
            # token like BTCUSDT -> check base
            if token.endswith('USDT') and token[:-4] in KNOWN_SYMBOLS:
                sym = token[:-4] + '/USDT'
                break
            if token in KNOWN_SYMBOLS:
                sym = token + '/USDT'
                break
    # If still not found, keep older heuristic as a last resort (but avoid single-word BUY/SELL)
    if not sym:
        sym2 = re.search(r"\b([A-Z]{3,6}(?:/[A-Z]{3,6})?)\b", s)
        if sym2:
            cand = sym2.group(1)
            if cand not in ('BUY', 'SELL'):
                sym = cand
        else:
            sym3 = re.search(r"\b([A-Z]{6,7})\b", s)
            if sym3:
                sym = sym3.group(1)
    if sym:
        sym = sym.replace(" ", "")
        if "/" not in sym:
            # if single symbol, default to /USDT
            if len(sym) <= 4:
                sym = sym + "/USDT"
            else:
                # split into base/quote if possible (heuristic)
                if sym.endswith("USDT"):
                    sym = sym[:-4] + "/USDT"

    # price detection
    price = None
    for pat in (r"@\s*([0-9,]+(?:\.[0-9]+)?)", r"PRICE[:\s]*([0-9,]+(?:\.[0-9]+)?)", r"AT\s*([0-9,]+(?:\.[0-9]+)?)"):
        m = re.search(pat, s)
        if m:
            price = m.group(1).replace(",", "")
            break

    # size detection
    size = None
    m = re.search(r"SIZE[:\s]*([0-9,]+(?:\.[0-9]+)?)", s)
    if not m:
        m = re.search(r"\b([0-9]+(?:\.[0-9]+)?)\s*(LOT|LOTS|UNITS|CONTRACTS)?\b", s)
    if m:
        size = m.group(1).replace(",", "")

    # order type
    order_type = None
    if "MARKET" in s:
        order_type = "MARKET"
    elif "LIMIT" in s:
        order_type = "LIMIT"

    # SL / TP
    sl = None
    tp = None
    m = re.search(r"\bSL[:\s]*([0-9,]+(?:\.[0-9]+)?)\b", s) or re.search(r"STOP\s*LOSS[:\s]*([0-9,]+(?:\.[0-9]+)?)", s)
    if m:
        sl = m.group(1).replace(",", "")
    m = re.search(r"\bTP[:\s]*([0-9,]+(?:\.[0-9]+)?)\b", s) or re.search(r"TAKE\s*PROFIT[:\s]*([0-9,]+(?:\.[0-9]+)?)", s)
    if m:
        tp = m.group(1).replace(",", "")

    # leverage
    leverage = None
    m = re.search(r"(\d+(?:\.\d+)?)\s*x\b", s)
    if m:
        leverage = m.group(1)
    else:
        m = re.search(r"LEVERAGE[:\s]*(\d+(?:\.\d+)?)", s)
        if m:
            leverage = m.group(1)

    # build summary
    parts = []
    if intent:
        parts.append(f"Intent: {intent}")
    if sym:
        parts.append(f"Symbol: {sym}")
    if size:
        parts.append(f"Size: {size}")
    if price:
        parts.append(f"Price: {price}")
    if order_type:
        parts.append(f"Type: {order_type}")
    if sl:
        parts.append(f"SL: {sl}")
    if tp:
        parts.append(f"TP: {tp}")
    if leverage:
        parts.append(f"Leverage: {leverage}")

    if parts:
        return "Detected trade — " + "; ".join(parts)

    snippet = (text or "").strip().replace("\n", " ")
    return f"Extracted text (no clear trade intent): {snippet[:400]}"


def _find_tesseract_cmd() -> str | None:
    """Try to locate a tesseract executable on PATH or common Windows
    install locations.
    """
    import shutil
    # check PATH
    path = shutil.which("tesseract")
    if path:
        return path
    # common Windows path
    possible = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for p in possible:
        if os.path.exists(p):
            return p
    return None


def _tesseract_available() -> bool:
    """Return True if a tesseract binary can be found on PATH
    or common locations.
    """
    try:
        return _find_tesseract_cmd() is not None
    except Exception:
        return False


async def handle_message(update, context):
    text = update.message.text or ""
    user = update.effective_user.username or update.effective_user.id
    # Print incoming text message to stdout / log
    if text:
        LOG.info("Telegram message from %s: %s", user, text)
        print(f"Telegram message from {user}: {text}")
        # Simple acknowledgement reply
        await update.message.reply_text(f"Got your message: {text}")
        return

    # Handle photos (Telegram sends a list of PhotoSize objects)
    # and image documents
    photo_list = getattr(update.message, "photo", None)
    document = getattr(update.message, "document", None)
    if photo_list:
        # pick the largest available photo
        photo = photo_list[-1]
        file_id = getattr(photo, "file_id", None)
        width = getattr(photo, "width", None)
        height = getattr(photo, "height", None)
        caption = getattr(update.message, "caption", "") or ""
        LOG.info(
            "Received photo from %s: file_id=%s size=%sx%s caption=%s",
            user,
            file_id,
            width,
            height,
            caption,
        )
        print(
            (
                "Telegram photo from {user}: file_id={file_id} "
                "size={width}x{height} caption={caption}"
            ).format(
                user=user,
                file_id=file_id,
                width=width,
                height=height,
                caption=caption,
            )
        )
        # Try to fetch file info (may include a file_path)
        try:
            if context and getattr(context, "bot", None):
                f = await context.bot.get_file(file_id)
                file_path = getattr(f, "file_path", None)
                LOG.info("Telegram photo file_path=%s", file_path)
                print(f"photo file_path={file_path}")
                # download the file to received_images
                try:
                    os.makedirs("received_images", exist_ok=True)
                    local_name = os.path.join(
                        "received_images", f"photo_{file_id}.jpg"
                    )
                    await f.download_to_drive(local_name)
                    LOG.info("Saved photo to %s", local_name)
                    # OCR: ensure tesseract binary is available first
                    if not _tesseract_available():
                        # Try an in-Python OCR fallback when tesseract is missing
                        LOG.info('Tesseract not found; trying EasyOCR for %s', local_name)
                        try:
                            import easyocr

                            # easyocr may download or initialize models on first run
                            # and can be slow. Use CPU by default (gpu=False).
                            reader = easyocr.Reader(['en'], gpu=False)
                            results = reader.readtext(local_name, detail=0)
                            ocr_text = "\n".join(results)
                            txt_path = local_name + ".txt"
                            with open(txt_path, "w", encoding="utf-8") as tf:
                                tf.write(ocr_text)
                            LOG.info('EasyOCR extracted %d chars', len(ocr_text))
                            analysis = analyze_trade_text(ocr_text)
                            await update.message.reply_text(analysis)
                        except ModuleNotFoundError:
                            LOG.warning('EasyOCR not installed; instructing user')
                            await update.message.reply_text(
                                'I saved your image, but OCR is not available.\n'
                                'Install EasyOCR in the project venv:\n'
                                '  ' + sys.executable + ' -m pip install easyocr\n'
                                'Note: EasyOCR may pull PyTorch and is large.\n'
                                'Or install Tesseract system-wide.'
                            )
                        except Exception:
                            LOG.exception('EasyOCR failed for %s', local_name)
                            await update.message.reply_text(
                                'Received image and saved it, but OCR failed on the server.'
                            )
                    else:
                        # try OCR
                        try:
                            from PIL import Image
                            import pytesseract

                            img = Image.open(local_name)
                            text = pytesseract.image_to_string(img)
                            txt_path = local_name + ".txt"
                            with open(txt_path, "w", encoding="utf-8") as tf:
                                tf.write(text)
                            LOG.info("OCR extracted %d chars", len(text))
                            print(f"OCR text saved to {txt_path}")
                            # Analyze trading text and reply
                            analysis = analyze_trade_text(text)
                            await update.message.reply_text(analysis)
                        except Exception:
                            LOG.debug("OCR not available or failed", exc_info=True)
                except Exception:
                    LOG.exception("Failed to download photo")
        except Exception:
            LOG.debug("Could not fetch file info for photo", exc_info=True)
        return
        return

    if document and getattr(document, "mime_type", "").startswith("image"):
        file_id = getattr(document, "file_id", None)
        fname = getattr(document, "file_name", None)
        caption = getattr(update.message, "caption", "") or ""
        LOG.info(
            "Received image document from %s: file_id=%s name=%s caption=%s",
            user,
            file_id,
            fname,
            caption,
        )
        print(
            (
                "Telegram image document from {user}: file_id={file_id} "
                "name={fname} caption={caption}"
            ).format(user=user, file_id=file_id, fname=fname, caption=caption)
        )
        try:
            if context and getattr(context, "bot", None):
                f = await context.bot.get_file(file_id)
                file_path = getattr(f, "file_path", None)
                LOG.info("Telegram document file_path=%s", file_path)
                print(f"document file_path={file_path}")
                # download
                try:
                    os.makedirs("received_images", exist_ok=True)
                    local_name = os.path.join(
                        "received_images", f"doc_{file_id}_{fname}"
                    )
                    await f.download_to_drive(local_name)
                    LOG.info("Saved document to %s", local_name)
                    # try OCR if image
                    try:
                        from PIL import Image
                        import pytesseract

                        img = Image.open(local_name)
                        text = pytesseract.image_to_string(img)
                        txt_path = local_name + ".txt"
                        with open(txt_path, "w", encoding="utf-8") as tf:
                            tf.write(text)
                        LOG.info("OCR extracted %d chars", len(text))
                        print(f"OCR text saved to {txt_path}")
                        analysis = analyze_trade_text(text)
                        await update.message.reply_text(analysis)
                    except Exception:
                        LOG.debug("OCR not available or failed", exc_info=True)
                except Exception:
                    LOG.exception("Failed to download document")
        except Exception:
            LOG.debug("Could not fetch file info for document", exc_info=True)
        return
        return


def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    # If token not in environment, attempt to read common config files.
    if not token:
        # helper: try parse simple KEY=VALUE lines
        def _try_read_key_from_file(path, key):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    for ln in fh:
                        ln = ln.strip()
                        if not ln or ln.startswith("#"):
                            continue
                        if "=" in ln:
                            k, v = ln.split("=", 1)
                            if k.strip() == key:
                                return v.strip().strip("'\" ")
            except Exception:
                return None
            return None

        here = os.path.dirname(__file__)
        # check .env first, then .env.example
        for fname in (".env", ".env.example"):
            p = os.path.join(here, fname)
            if os.path.exists(p):
                token = _try_read_key_from_file(p, "TELEGRAM_BOT_TOKEN")
                if token:
                    LOG.info("Loaded TELEGRAM_BOT_TOKEN from %s", p)
                    break
        # fallback: config.json with {"TELEGRAM_BOT_TOKEN": "..."}
        if not token:
            try:
                import json

                p = os.path.join(here, "config.json")
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as fh:
                        cfg = json.load(fh)
                        token = cfg.get("TELEGRAM_BOT_TOKEN")
                        if token:
                            LOG.info("Loaded TELEGRAM_BOT_TOKEN from %s", p)
            except Exception:
                token = token

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set in environment")

    if not _TELEGRAM_AVAILABLE:
        # Friendly guidance for common pitfall: running system Python instead
        # of the project's virtualenv. Include exact commands to run.
        venv_python = os.path.join(
            os.path.dirname(__file__),
            ".venv",
            "Scripts",
            "python.exe",
        )
        raw = r'''
python-telegram-bot is not installed in this Python interpreter.
Common cause: you're running the system Python instead of the project's venv.

If you have the project venv, run:
  {venv_python} telegram_bot.py

Or activate the venv in PowerShell:
  . .venv\Scripts\Activate.ps1
then run: python telegram_bot.py

If you don't have dependencies installed, install them once into the venv:
  .venv\Scripts\python.exe -m pip install -r requirements.txt
'''
        msg = raw.format(venv_python=venv_python)
        raise RuntimeError(msg)
    app = ApplicationBuilder().token(token).build()
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    # Also handle photos and image documents
    app.add_handler(MessageHandler(filters.PHOTO, handle_message))
    # Prefer document image filters if available in this version
    doc_filter = None
    if hasattr(filters, "Document"):
        # try IMAGE then ALL
        doc_filter = getattr(filters.Document, "IMAGE", None) or getattr(
            filters.Document, "ALL", None
        )
    if doc_filter is not None:
        app.add_handler(MessageHandler(doc_filter, handle_message))
    else:
        # Fallback: handle any non-text, non-command messages (broad but safe)
        app.add_handler(
            MessageHandler(
                ~(filters.TEXT | filters.COMMAND),
                handle_message,
            )
        )
    # Register /parse_gemini command to let users forward/reply images for
    # structured parsing via Google Vision + Gemini (falls back to EasyOCR).
    app.add_handler(CommandHandler("parse_gemini", parse_gemini_command))
    # Start the bot's polling loop so it stays running. Log lifecycle events.
    LOG.info("Starting Telegram bot...")
    try:
        # This blocks and runs the bot until interrupted.
        app.run_polling()
    except (KeyboardInterrupt, SystemExit):
        LOG.info("Telegram bot stopped by user or system signal")
    except Exception:
        LOG.exception("Telegram bot crashed")


async def parse_gemini_command(update, context):
    # Accept either the image in the message or an image the message replies to
    target = update.message
    if update.message.reply_to_message:
        target = update.message.reply_to_message

    photo_list = getattr(target, "photo", None)
    document = getattr(target, "document", None)
    if not photo_list and not document:
        await update.message.reply_text("Please send or reply to an image to parse.")
        return

    file_id = None
    if photo_list:
        file_id = photo_list[-1].file_id
    elif document:
        file_id = document.file_id

    if not file_id:
        await update.message.reply_text("Couldn't find an image file to download.")
        return

    try:
        f = await context.bot.get_file(file_id)
        os.makedirs("received_images", exist_ok=True)
        local_name = os.path.join("received_images", f"parse_{file_id}.jpg")
        await f.download_to_drive(local_name)
    except Exception:
        LOG.exception("Failed to download image for /parse_gemini")
        await update.message.reply_text("Failed to download the image.")
        return

    if GOOGLE_API_KEY:
        try:
            await update.message.reply_text("Sending image to Vision + Gemini...")
            from gemini_client import ocr_with_vision_api, parse_trade_with_gemini

            txt = ocr_with_vision_api(local_name)
            parsed = parse_trade_with_gemini(txt)
            # If model returned validation info, respect it and show warnings
            if isinstance(parsed, dict) and parsed.get("valid") is False:
                reasons = parsed.get("validation") or []
                await update.message.reply_text(
                    "Gemini parsed a trade but validation failed: "
                    + ", ".join(str(r) for r in reasons)
                )
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                await update.message.reply_text(pretty)
                return
            # create a short human summary for valid parse
            summary_parts = []
            if isinstance(parsed, dict):
                if parsed.get("action"):
                    summary_parts.append(f"{parsed.get('action')} {parsed.get('symbol', '')}")
                if parsed.get("size"):
                    summary_parts.append(f"size={parsed.get('size')}")
                if parsed.get("price"):
                    summary_parts.append(f"price={parsed.get('price')}")
            summary = " | ".join(summary_parts) or "Parsed trade details"
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            await update.message.reply_text(f"{summary}\n\n{pretty}")
            return
        except Exception:
            LOG.exception("Gemini parsing failed")
            await update.message.reply_text(
                "Vision or Gemini API call failed; falling back to EasyOCR."
            )

    # fallback to EasyOCR
    try:
        import easyocr

        reader = easyocr.Reader(["en"], gpu=False)
        lines = reader.readtext(local_name, detail=0)
        text = "\n".join(lines)
        parsed = analyze_trade_text(text)
        await update.message.reply_text("Fallback EasyOCR parsed:\n" + parsed)
    except Exception:
        LOG.exception("EasyOCR fallback failed for /parse_gemini")
        await update.message.reply_text(
            "Both cloud OCR and local OCR failed. Install Tesseract or EasyOCR."
        )
    # Done handling /parse_gemini; return to main loop.


def simulate_message(text: str, user: str | int = "simulated_user"):
    """Simulate receiving a Telegram message without the dependency.

    This creates a minimal-like object expected by handle_message and
    runs the handler in an asyncio loop.
    """
    import asyncio

    class _Msg:
        def __init__(self, text):
            self.text = text

        async def reply_text(self, txt):
            print("[reply]", txt)

    class _Update:
        def __init__(self, text, user):
            self.message = _Msg(text)
            
            class _User:
                def __init__(self, u):
                    self.username = u if isinstance(u, str) else None
                    self.id = u
            self.effective_user = _User(user)

    asyncio.run(handle_message(_Update(text, user), None))


def forward_to_telegram(text: str, chat_id: str | None = None) -> bool:
    """Best-effort send a text message to Telegram using TELEGRAM_BOT_TOKEN.

    Returns True on HTTP 200 from Telegram, False otherwise. This helper is
    intentionally lightweight to avoid requiring the full telegram library
    at runtime; it uses the REST API directly.
    """
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        LOG.debug('TELEGRAM_BOT_TOKEN not set; skipping forward_to_telegram')
        return False
    chat = chat_id or os.getenv('TELEGRAM_CHAT_ID')
    if not chat:
        LOG.debug('TELEGRAM_CHAT_ID not set; skipping forward_to_telegram')
        return False
    try:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {'chat_id': chat, 'text': text}
        import requests

        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception:
        LOG.exception('forward_to_telegram failed')
        return False


def start_forward_webhook(host: str = '127.0.0.1', port: int = 8765, secret: str | None = None):
    """Start a tiny Flask webhook in the current process to forward incoming
    POSTs into Telegram (calls `forward_to_telegram`).

    This is a convenience for running a small webhook from the same host
    without changing the main Flask app. It's intended for local/dev use.
    """
    try:
        from flask import Flask, request, jsonify
    except Exception:
        raise RuntimeError('Flask is required to run the forward webhook')

    tiny = Flask('telegram_forward')

    @tiny.route('/forward', methods=['POST'])
    def _forward():
        if secret:
            hdr = request.headers.get('X-FORWARD-SECRET')
            if hdr != secret:
                return jsonify({'error': 'invalid secret'}), 403
        data = request.get_json(silent=True)
        if isinstance(data, dict):
            txt = data.get('message') or data.get('text') or json.dumps(data)
        else:
            txt = request.get_data(as_text=True) or ''
        ok = forward_to_telegram(txt)
        return jsonify({'forwarded': bool(ok)})

    LOG.info('Starting lightweight forward webhook on %s:%s', host, port)
    tiny.run(host=host, port=port)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--simulate",
        "-s",
        help="Simulate an incoming message",
    )
    args = parser.parse_args()
    if args.simulate:
        simulate_message(args.simulate)
    else:
        run_bot()
