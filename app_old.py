from dotenv import load_dotenv
import os
import logging

# Load env first so dependent modules can read MOCK_OPENAI at import time
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MOCK_OPENAI = os.getenv("MOCK_OPENAI", "false").lower() in (
    "1",
    "true",
    "yes",
)

if not OPENAI_API_KEY and not MOCK_OPENAI:
    # If no API key provided, default to mock mode for local dev
    print(
        "WARNING: OPENAI_API_KEY not set. Defaulting to "
        "MOCK_OPENAI=true for local testing."
    )
    os.environ["MOCK_OPENAI"] = "true"
    MOCK_OPENAI = True

# Now import modules that may depend on MOCK_OPENAI
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import json
from openai_client import chat_completion

# configure basic file logging for the Flask app so external helpers can tail it
LOG = logging.getLogger("rag_project")
LOG.setLevel(logging.INFO)
if not LOG.handlers:
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        fh = logging.FileHandler("flask.log", encoding="utf-8")
        fh.setFormatter(fmt)
        LOG.addHandler(fh)
    except Exception:
        # if file handler can't be created, continue with no file logging
        LOG.debug("Could not create flask.log file handler")

 
# Lazy import/store creation to avoid heavy deps at module import time
_store = None


def get_vector_store():
    global _store
    if _store is None:
        # import here to avoid sklearn import during lightweight runs/tests
        from vector_store import InMemoryVectorStore

        DOCS_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")
        _store = InMemoryVectorStore()
        _store.add_documents_from_dir(DOCS_DIR)
    return _store
from telegram_bot import analyze_trade_text, forward_to_telegram
from trading import TradingManager
from db import SessionLocal
from models import Trade, Signal
import requests


app = Flask(__name__)
# Enable CORS for all routes - simple and effective for development
CORS(app, resources={r"/*": {"origins": "*"}})

# Register trading management blueprint
try:
    from trading_api import trading_bp
    app.register_blueprint(trading_bp)
    LOG.info("Registered trading management API blueprint")
except Exception as e:
    LOG.error(f"Failed to register trading_api blueprint: {e}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/query", methods=["POST"])
def query():
    data = request.get_json() or {}
    user_query = data.get("query")
    if not user_query:
        return jsonify({"error": "`query` field is required"}), 400

    # retrieve top-k relevant docs
    top_k = int(data.get("top_k", 3))
    results = get_vector_store().query(user_query, top_k=top_k)

    # Build retrieval context
    context_texts = []
    for i, (doc, score) in enumerate(results):
        context_texts.append(f"[DOC {i+1} | score={score:.4f}]\n{doc.strip()}")
    context = "\n\n---\n\n".join(context_texts)

    # Compose prompt for the LLM
    system_prompt = (
        "You are an assistant that answers user questions using the provided "
        "context. If the answer is not contained in the context, say you "
        "don't know and avoid hallucination. Cite the relevant document "
        "fragments when possible."
    )

    user_prompt = (
        "Context:\n"
        f"{context}\n\n"
        f"User question: {user_query}\n\n"
        "Answer concisely and cite the document numbers if used."
    )

    # Call OpenAI ChatCompletion
    try:
        resp = chat_completion(
            model=data.get("model", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=512,
            temperature=float(data.get("temperature", 0.0)),
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    answer = resp["choices"][0]["message"]["content"].strip()

    return jsonify({"answer": answer, "retrieved": [
        {"text": doc, "score": float(score)} for doc, score in results
    ]})


@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    """Endpoint for TradingView alerts.

    Accepts JSON with arbitrary fields or plain text in body. If the
    environment variable WEBHOOK_SECRET is set, incoming requests must
    include header X-WEBHOOK-SECRET with the same value for basic auth.

    The endpoint runs `analyze_trade_text` on the provided message and
    returns a JSON response with the parsed summary. If TELEGRAM_BOT_TOKEN
    and TELEGRAM_CHAT_ID are set in the environment, the parsed summary
    will also be POSTed to the Telegram sendMessage API as a convenience.
    """
    secret_expected = os.getenv('WEBHOOK_SECRET')
    if secret_expected:
        # Accept the secret either via header or as a query parameter to
        # support services (or setups) that cannot set custom headers.
        secret_header = request.headers.get('X-WEBHOOK-SECRET')
        secret_q = request.args.get('secret')
        if not (
            (secret_header and secret_header == secret_expected)
            or (secret_q and secret_q == secret_expected)
        ):
            return jsonify({'error': 'invalid or missing webhook secret'}), 403

    data = None
    text = None
    try:
        # Try JSON first
        data = request.get_json(silent=True)
    except Exception:
        data = None

    if isinstance(data, dict):
        # Common TradingView templates may use 'message' or 'text';
        # otherwise fall back to the full JSON payload.
        text = (
            data.get('message')
            or data.get('text')
            or json.dumps(data)
        )
    else:
        # fallback: raw body
        text = request.get_data(as_text=True) or ''

    # Log raw incoming request for debugging (headers + body)
    try:
        hdrs = dict(request.headers)
        LOG.info('Incoming webhook headers: %s', hdrs)
        LOG.info('Incoming webhook body: %s', text)
        # also save the raw body to a file for quick inspection
        try:
            with open('last_webhook.txt', 'w', encoding='utf-8') as fh:
                fh.write(text or '')
        except Exception:
            LOG.debug('Failed to write last_webhook.txt', exc_info=True)
    except Exception:
        LOG.debug('Failed to log incoming webhook', exc_info=True)

    summary = analyze_trade_text(text)

    # Quick heuristic extraction for signals (used to persist Signal record)
    # Priority: 1) data dict fields, 2) parsed text, 3) summary analysis
    pre_action = None
    pre_price = None
    pre_symbol = None
    
    # Try to extract from JSON data first
    if isinstance(data, dict):
        # Check common field names for action
        for field in ['action', 'side', 'type', 'order_action', 'signal']:
            if field in data:
                val = str(data[field]).upper()
                if 'BUY' in val or 'LONG' in val:
                    pre_action = 'BUY'
                    break
                elif 'SELL' in val or 'SHORT' in val:
                    pre_action = 'SELL'
                    break
        
        # Check common field names for price
        for field in ['price', 'close', 'entry_price', 'signal_price']:
            if field in data and data[field]:
                try:
                    pre_price = float(data[field])
                    break
                except (ValueError, TypeError):
                    pass
        
        # Check common field names for symbol
        for field in ['symbol', 'ticker', 'pair', 'instrument']:
            if field in data and data[field]:
                pre_symbol = str(data[field]).upper()
                break
    
    # Fallback to text parsing if not found in JSON
    try:
        if not pre_action:
            # Check in summary
            low_summary = (summary or '').lower()
            low_text = (text or '').lower()
            
            # Check both summary and raw text
            combined = low_summary + ' ' + low_text
            if 'buy' in combined or 'long' in combined:
                pre_action = 'BUY'
            elif 'sell' in combined or 'short' in combined:
                pre_action = 'SELL'
        
        if not pre_price:
            import re
            m = re.search(r"price[:=\s]*([0-9]+\.?[0-9]*)", text, re.IGNORECASE)
            if m:
                pre_price = float(m.group(1))

        if not pre_symbol:
            m_sym = re.search(r"[Ss]ymbol[:=\s]*([A-Za-z0-9\-/_.]+)", text, re.IGNORECASE)
            if m_sym:
                pre_symbol = m_sym.group(1).upper()
            else:
                # Try to find common trading pairs
                m2 = re.search(r"\b([A-Za-z]{2,6}(?:USD|USDT|BTC|ETH)?(?:/USDT|/USD)?)\b", text, re.IGNORECASE)
                if m2:
                    pre_symbol = m2.group(1).upper()
    except Exception as e:
        LOG.exception('Error during signal extraction: %s', e)
        pass

    # Idempotency: compute the event key and TRY to insert it immediately.
    # This claims ownership of the event; if insertion fails with
    # IntegrityError it means another process already claimed it and we
    # should return duplicate early. This avoids the classic check-then-act
    # race.
    event_key = None
    try:
        event_key = request.headers.get('X-Event-ID')
        if not event_key:
            import hashlib

            event_key = hashlib.sha256((text or '').encode('utf-8')).hexdigest()

        from sqlalchemy.exc import IntegrityError
        s = SessionLocal()
        try:
            from models import IdempotencyKey

            k = IdempotencyKey(key=event_key)
            s.add(k)
            try:
                s.commit()
            except IntegrityError:
                s.rollback()
                LOG.info('Duplicate event detected at claim: %s', event_key)
                return jsonify({'summary': summary, 'raw': text, 'duplicate': True}), 200
        finally:
            s.close()
    except Exception:
        LOG.exception('Idempotency check/claim failed')

    # If Gemini is available, prefer its structured parse and validate it to
    # avoid false alerts. This is best-effort and only used when the
    # gemini_client module and GOOGLE_API_KEY are available.
    # ensure parsed exists to avoid UnboundLocalError in older runtimes
    parsed = None
    try:
        from gemini_client import (
            parse_trade_with_gemini,
            GOOGLE_API_KEY as _GEM_KEY,
        )
    except Exception:
        parse_trade_with_gemini = None
        _GEM_KEY = None

    if parse_trade_with_gemini and _GEM_KEY:
        try:
            parsed = parse_trade_with_gemini(text)
            # If parsed is dict and includes validation info, use it
            if isinstance(parsed, dict):
                if parsed.get('valid') is False:
                    # Don't forward invalid parsed trades. Return validation
                    # details to caller for auditing.
                    return (
                        jsonify(
                            {
                                'summary': None,
                                'raw': text,
                                'parsed': parsed,
                            }
                        ),
                        200,
                    )
                # Build a short summary from Gemini's parse for forwarding
                summary_parts = []
                if parsed.get('action'):
                    summary_parts.append(
                        f"{parsed.get('action')} {parsed.get('symbol', '')}"
                    )
                if parsed.get('size'):
                    summary_parts.append(f"size={parsed.get('size')}")
                if parsed.get('price'):
                    summary_parts.append(f"price={parsed.get('price')}")
                summary = " | ".join(summary_parts) or summary
        except Exception:
            # If Gemini call fails, fall back to the simpler analyzer summary
            pass

    # Optionally forward to Telegram if configured (use helper from telegram_bot)
    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
    tg_chat = os.getenv('TELEGRAM_CHAT_ID')
    if tg_token and tg_chat:
        try:
            send_text = 'Incoming webhook:\n' + (text or '') + '\n\n' + summary
            try:
                ok = forward_to_telegram(send_text, chat_id=tg_chat)
                LOG.info('forward_to_telegram returned: %s', bool(ok))
            except Exception:
                LOG.exception('forward_to_telegram raised an exception')
                ok = False

            # Fallback: if helper failed, try direct requests call so we at least
            # attempt delivery. All forwarding is best-effort and must not
            # affect webhook response.
            if not ok:
                try:
                    send_url = (
                        f'https://api.telegram.org/bot{tg_token}/sendMessage'
                    )
                    payload = {
                        'chat_id': tg_chat,
                        'text': send_text,
                    }
                    r = requests.post(send_url, json=payload, timeout=5)
                    LOG.info(
                        'Direct Telegram send status: %s',
                        getattr(r, 'status_code', None),
                    )
                except Exception:
                    LOG.exception('Direct Telegram send also failed')
        except Exception:
            LOG.exception('Unexpected error while attempting Telegram forward')

    # Persist raw signal for reporting (best-effort). Use the preliminary
    # extracted metadata so we don't depend on variables set later.
    try:
        s_session = SessionLocal()
        try:
            sig = Signal(
                source='webhook',
                symbol=pre_symbol or None,
                action=pre_action or None,
                price=pre_price,
                raw=text,
            )
            s_session.add(sig)
            s_session.commit()
        finally:
            s_session.close()
    except Exception:
        LOG.exception('Failed to persist Signal')

    # Persist trade signals using the TradingManager if possible. This is
    # best-effort and shouldn't prevent webhook response on failure.
    try:
        # naive parse: look for keywords BUY/SELL in summary or parsed dict
        tm = TradingManager()
        # prefer the structured parse from gemini if available earlier
        action = None
        price = None
        symbol = None
        # If gemini returned a dict, prefer its structured fields.
        if parsed and isinstance(parsed, dict):
            action = parsed.get('action')
            price = parsed.get('price')
            symbol = parsed.get('symbol')
        # If parsed didn't provide fields, fall back to the quick heuristics
        # fallback to quick heuristic from summary text
        if not action:
            summary_lower = summary.lower()
            if 'buy' in summary_lower or 'long' in summary_lower:
                action = 'BUY'
            elif 'sell' in summary_lower or 'short' in summary_lower:
                action = 'SELL'
        # attempt to extract a numeric price from the text if needed
        if price is None:
            import re

            m = re.search(r"price[:= ]*([0-9]+\.?[0-9]*)", text, re.IGNORECASE)
            if m:
                price = float(m.group(1))

        # fallback: try to extract symbol from common patterns in the text
        if not symbol:
            import re

            # Try a 'Symbol' label first (e.g. 'Symbol: ETHUSD')
            m_sym = re.search(r"Symbol[:= ]*([A-Za-z0-9\-/_.]+)", text, re.IGNORECASE)
            if m_sym:
                symbol = m_sym.group(1).upper()
            else:
                # General heuristic: uppercase ticker-like tokens (ETHUSD, BTCUSDT, ETH/USDT)
                m2 = re.search(r"\b([A-Za-z]{2,6}(?:USD|USDT|BTC|ETH)?(?:/USDT|/USD)?)\b", text, re.IGNORECASE)
                if m2:
                    symbol = m2.group(1).upper()

        # Use preliminary pre-extracted metadata as a final fallback so we
        # don't crash if the more-accurate parse didn't return values.
        action = action or pre_action
        price = price or pre_price
        symbol = symbol or pre_symbol

        if action and symbol and price:
            # Dispatch trade handling to background worker if Redis is
            # configured; otherwise run inline.
            try:
                REDIS_URL = os.getenv('REDIS_URL')
                if REDIS_URL:
                    try:
                        from redis import Redis
                        from rq import Queue

                        rconn = Redis.from_url(REDIS_URL)
                        q = Queue(connection=rconn)
                        q.enqueue('tasks.process_signal_task', event_key, text, action, symbol, price, summary)
                        LOG.info('Enqueued trade task to Redis')
                    except Exception:
                        LOG.exception('Failed to enqueue trade task; running inline')
                        from decimal import Decimal

                        trade_res = tm.handle_signal(None, symbol, action, Decimal(str(price)))
                        LOG.info('Persisted trading action inline: %s', trade_res)
                else:
                    from decimal import Decimal

                    trade_res = tm.handle_signal(None, symbol, action, Decimal(str(price)))
                    LOG.info('Persisted trading action inline: %s', trade_res)
            except Exception:
                LOG.exception('Failed to persist trade signal')
        # store idempotency key on successful flow. Use transactional
        # insert and handle IntegrityError to be race-safe.
        try:
            from sqlalchemy.exc import IntegrityError
            sk = SessionLocal()
            try:
                from models import IdempotencyKey

                k = IdempotencyKey(key=event_key)
                sk.add(k)
                try:
                    sk.commit()
                except IntegrityError:
                    sk.rollback()
                    LOG.info('Idempotency key already exists (race): %s', event_key)
            finally:
                sk.close()
        except Exception:
            LOG.exception('Failed to persist idempotency key')
    except Exception:
        LOG.exception('Unexpected error while handling persistence')

    return jsonify({'summary': summary, 'raw': text})


@app.route('/dashboard')
def dashboard():
    # simple dashboard that lists recent trades
    session = SessionLocal()
    try:
        trades = (
            session.query(Trade)
            .order_by(Trade.open_time.desc())
            .limit(200)
            .all()
        )
    finally:
        session.close()
    return render_template('dashboard.html', trades=trades)


@app.route('/api/metrics')
def api_metrics():
    """Return simple metrics: today's count/pnl by hour, weekly and monthly pnl series."""
    from datetime import datetime, timedelta
    session = SessionLocal()
    try:
        now = datetime.utcnow()
        start = datetime(now.year, now.month, now.day)
        # today's trades
        q = session.query(Trade).filter(Trade.open_time >= start)
        trades_today = q.all()
        count = len(trades_today)
        total_pnl = sum([float(t.profit_loss or 0) for t in trades_today])
        # hourly distribution
        hours = []
        counts = []
        for h in range(0,24):
            hstart = start + timedelta(hours=h)
            hend = hstart + timedelta(hours=1)
            c = session.query(Trade).filter(Trade.open_time >= hstart, Trade.open_time < hend).count()
            hours.append(f"{h}:00")
            counts.append(c)

        # weekly (last 7 days) pnl
        week_labels = []
        week_values = []
        for d in range(6,-1,-1):
            day = now.date() - timedelta(days=d)
            dstart = datetime(day.year, day.month, day.day)
            dend = dstart + timedelta(days=1)
            vals = session.query(Trade).filter(Trade.open_time >= dstart, Trade.open_time < dend).all()
            week_labels.append(day.strftime('%Y-%m-%d'))
            week_values.append(sum([float(t.profit_loss or 0) for t in vals]))

        # monthly (last 30 days) simple PnL
        month_values = []
        month_labels = []
        for d in range(29,-1,-1):
            day = now.date() - timedelta(days=d)
            dstart = datetime(day.year, day.month, day.day)
            dend = dstart + timedelta(days=1)
            vals = session.query(Trade).filter(Trade.open_time >= dstart, Trade.open_time < dend).all()
            month_labels.append(day.strftime('%m-%d'))
            month_values.append(sum([float(t.profit_loss or 0) for t in vals]))

        return jsonify({
            'today': {'count': count, 'pnl': total_pnl, 'hours': hours, 'hour_counts': counts},
            'week': {'labels': week_labels, 'values': week_values},
            'month': {'labels': month_labels, 'values': month_values},
        })
    finally:
        session.close()


@app.route('/api/signals')
def api_signals():
    session = SessionLocal()
    try:
        q = session.query(Signal)
        date = request.args.get('date')
        symbol = request.args.get('symbol')
        if date:
            from datetime import datetime, timedelta
            d = datetime.strptime(date, '%Y-%m-%d')
            q = q.filter(Signal.created_at >= d, Signal.created_at < d + timedelta(days=1))
        if symbol:
            q = q.filter(Signal.symbol == symbol.upper())
        signals = q.order_by(Signal.created_at.desc()).limit(500).all()
        return jsonify({'count': len(signals), 'signals': [
            {'id': s.id, 'symbol': s.symbol, 'action': s.action, 'price': float(s.price) if s.price else None, 'created_at': s.created_at.isoformat(), 'raw': s.raw}
            for s in signals
        ]})
    finally:
        session.close()


@app.route('/api/historical-prices/<symbol>', methods=['GET'])
def get_historical_prices(symbol):
    """
    Get historical OHLCV data for a symbol.
    Query params:
    - timeframe: 1m, 5m, 15m, 1h, 4h, 1d (default: 1h)
    - limit: number of candles (default: 500)
    - use_mock: true/false (default: true for development)
    """
    from price_history_service import PriceHistoryService
    
    session = SessionLocal()
    try:
        service = PriceHistoryService(session)
        
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 500))
        use_mock = request.args.get('use_mock', 'true').lower() == 'true'
        
        # Get data from database
        data = service.get_historical_data(symbol.upper(), timeframe, limit)
        
        # If no data exists, generate/fetch it
        if not data:
            LOG.info(f"No historical data found for {symbol}, collecting data (mock={use_mock})...")
            result = service.collect_data_for_instrument(symbol.upper(), timeframe, use_mock)
            if result['status'] == 'success':
                data = service.get_historical_data(symbol.upper(), timeframe, limit)
            else:
                return jsonify({'error': result['message']}), 500
        
        return jsonify({
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'count': len(data),
            'data': data
        })
        
    except Exception as e:
        LOG.error(f"Error fetching historical prices: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/collect-price-data', methods=['POST'])
def collect_price_data():
    """
    Manually trigger price data collection for instruments.
    POST body: {
        "symbol": "BTCUSDT" (optional, if not provided collects for all enabled),
        "timeframe": "1h" (optional, default: 1h),
        "use_mock": true (optional, default: true)
    }
    """
    from price_history_service import PriceHistoryService
    
    session = SessionLocal()
    try:
        service = PriceHistoryService(session)
        data = request.get_json() or {}
        
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', '1h')
        use_mock = data.get('use_mock', True)
        
        if symbol:
            # Collect for single instrument
            result = service.collect_data_for_instrument(symbol.upper(), timeframe, use_mock)
            return jsonify(result)
        else:
            # Collect for all enabled instruments
            results = service.collect_all_instruments(timeframe, use_mock)
            return jsonify({
                'status': 'completed',
                'results': results,
                'total_instruments': len(results),
                'successful': sum(1 for r in results if r['status'] == 'success')
            })
    
    except Exception as e:
        LOG.error(f"Error collecting price data: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/latest-price/<symbol>', methods=['GET'])
def get_latest_price(symbol):
    """Get the most recent price data for a symbol."""
    from price_history_service import PriceHistoryService
    
    session = SessionLocal()
    try:
        service = PriceHistoryService(session)
        timeframe = request.args.get('timeframe', '1h')
        
        latest = service.get_latest_price(symbol.upper(), timeframe)
        
        if latest:
            return jsonify(latest)
        else:
            return jsonify({'error': 'No data found'}), 404
    
    except Exception as e:
        LOG.error(f"Error fetching latest price: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/client')
@app.route('/client/')
@app.route('/client/<path:path>')
def serve_client(path='index.html'):
    """
    Serve the built React client from static/client.
    Run build_client.ps1 to build and copy the client files.
    """
    from flask import send_from_directory
    import os
    client_dir = os.path.join(app.static_folder or 'static', 'client')
    if not os.path.exists(client_dir):
        return f"Client not built yet. Run: cd client && npm run build && copy dist to static/client", 404
    # Handle SPA routing - serve index.html for all non-file paths
    if path and '.' not in path.split('/')[-1]:
        path = 'index.html'
    return send_from_directory(client_dir, path)


if __name__ == "__main__":
    # Initialize database and create tables if they don't exist
    print("\n" + "=" * 60)
    print("🚀 Starting RAG Trading Assistant")
    print("=" * 60)
    
    from db import init_db
    init_db()
    
    print("\n🌐 Starting Flask server on http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    
    app.run(host="127.0.0.1", port=5000, debug=True)
