"""
TradingView Webhook API Endpoint
Handles incoming TradingView alerts and processes trading signals
"""
from flask import Blueprint, jsonify, request
import os
import json
import hashlib
import re
import logging
from sqlalchemy.exc import IntegrityError
from src.database.session import SessionLocal
from src.models.base import Signal, IdempotencyKey

webhook_bp = Blueprint('webhook', __name__)
LOG = logging.getLogger(__name__)


@webhook_bp.route('/webhook', methods=['POST'])
def tradingview_webhook():
    """
    Endpoint for TradingView alerts.
    
    Accepts JSON with arbitrary fields or plain text in body. If the
    environment variable WEBHOOK_SECRET is set, incoming requests must
    include header X-WEBHOOK-SECRET with the same value for basic auth.
    """
    # Check webhook secret if configured
    secret_expected = os.getenv('WEBHOOK_SECRET')
    if secret_expected:
        # Accept the secret either via header or as a query parameter
        secret_header = request.headers.get('X-WEBHOOK-SECRET')
        secret_q = request.args.get('secret')
        if not (
            (secret_header and secret_header == secret_expected)
            or (secret_q and secret_q == secret_expected)
        ):
            LOG.warning('Webhook received with invalid or missing secret')
            return jsonify({'error': 'invalid or missing webhook secret'}), 403

    # Parse incoming data
    data = None
    text = None
    try:
        data = request.get_json(silent=True)
    except Exception:
        data = None

    if isinstance(data, dict):
        # Common TradingView templates may use 'message' or 'text'
        text = (
            data.get('message')
            or data.get('text')
            or json.dumps(data)
        )
    else:
        # Fallback: raw body
        text = request.get_data(as_text=True) or ''

    # Log incoming request for debugging
    try:
        hdrs = dict(request.headers)
        LOG.info('=' * 80)
        LOG.info('[INCOMING] WEBHOOK REQUEST')
        LOG.info('=' * 80)
        LOG.info('Headers: %s', hdrs)
        LOG.info('Body: %s', text)
        LOG.info('-' * 80)
        
        # Save raw body to file for inspection
        try:
            with open('data/last_webhook.txt', 'w', encoding='utf-8') as fh:
                fh.write(text or '')
            LOG.debug('Saved webhook body to data/last_webhook.txt')
        except Exception:
            LOG.debug('Failed to write last_webhook.txt', exc_info=True)
    except Exception:
        LOG.debug('Failed to log incoming webhook', exc_info=True)

    # Extract signal information
    LOG.info('Extracting signal data from webhook...')
    signal_data = extract_signal_data(data, text)
    LOG.info(f'Extracted signal: action={signal_data.get("action")}, symbol={signal_data.get("symbol")}, price={signal_data.get("price")}')
    
    # Idempotency check
    LOG.debug('Computing event key for idempotency check...')
    event_key = compute_event_key(request, text)
    if is_duplicate_event(event_key):
        LOG.warning(f'[WARN] Duplicate event detected: {event_key}')
        return jsonify({
            'status': 'success',
            'message': 'Duplicate event ignored',
            'duplicate': True,
            'signal': signal_data
        }), 200
    
    LOG.info('[OK] New event (not duplicate)')

    # Persist signal to database
    try:
        LOG.debug('Persisting signal to database...')
        persist_signal(signal_data, text)
        LOG.info('[OK] Signal persisted to database')
    except Exception as e:
        LOG.exception('[X] Failed to persist signal: %s', e)

    # Process trade signal first to get result
    trade_result = None
    try:
        LOG.info('[REFRESH] Processing trade signal...')
        trade_result = process_trade_signal(signal_data)
        signal_data['trade_result'] = trade_result  # Add result for Telegram
        LOG.info(f'[OK] Trade signal processed: action={trade_result.get("action")}')
    except Exception as e:
        LOG.exception('[X] Failed to process trade signal: %s', e)

    # Forward to Telegram with trade result
    try:
        LOG.debug('Forwarding to Telegram...')
        forward_to_telegram(text, signal_data)
        LOG.info('[OK] Forwarded to Telegram')
    except Exception as e:
        LOG.exception('[X] Failed to forward to Telegram: %s', e)

    return jsonify({
        'status': 'success',
        'message': 'Webhook received and processed',
        'signal': signal_data
    }), 200


def extract_signal_data(data, text):
    """Extract trading signal information from webhook data"""
    signal = {
        'action': None,
        'symbol': None,
        'price': None,
        'size': None,
        'stop_loss': None,
        'take_profit': None
    }
    
    # Try to extract from JSON data first
    if isinstance(data, dict):
        # Extract action
        for field in ['action', 'side', 'type', 'order_action', 'signal']:
            if field in data:
                val = str(data[field]).upper()
                if 'BUY' in val or 'LONG' in val:
                    signal['action'] = 'BUY'
                    break
                elif 'SELL' in val or 'SHORT' in val:
                    signal['action'] = 'SELL'
                    break
        
        # Extract price
        for field in ['price', 'close', 'entry_price', 'signal_price']:
            if field in data and data[field]:
                try:
                    signal['price'] = float(data[field])
                    break
                except (ValueError, TypeError):
                    pass
        
        # Extract symbol
        for field in ['symbol', 'ticker', 'pair', 'instrument']:
            if field in data and data[field]:
                signal['symbol'] = str(data[field]).upper()
                break
        
        # Extract additional fields
        if 'size' in data:
            try:
                signal['size'] = float(data['size'])
            except (ValueError, TypeError):
                pass
        
        if 'stop_loss' in data or 'sl' in data:
            try:
                signal['stop_loss'] = float(data.get('stop_loss') or data.get('sl'))
            except (ValueError, TypeError):
                pass
        
        if 'take_profit' in data or 'tp' in data:
            try:
                signal['take_profit'] = float(data.get('take_profit') or data.get('tp'))
            except (ValueError, TypeError):
                pass
    
    # Fallback to text parsing if not found in JSON
    if not signal['action']:
        low_text = (text or '').lower()
        if 'buy' in low_text or 'long' in low_text:
            signal['action'] = 'BUY'
        elif 'sell' in low_text or 'short' in low_text:
            signal['action'] = 'SELL'
    
    if not signal['price']:
        m = re.search(r"price[:=\s]*([0-9]+\.?[0-9]*)", text or '', re.IGNORECASE)
        if m:
            try:
                signal['price'] = float(m.group(1))
            except ValueError:
                pass
    
    if not signal['symbol']:
        # Try 'Symbol: BTCUSDT' pattern
        m_sym = re.search(r"[Ss]ymbol[:=\s]*([A-Za-z0-9\-/_.]+)", text or '', re.IGNORECASE)
        if m_sym:
            signal['symbol'] = m_sym.group(1).upper()
        else:
            # Try to find common trading pairs
            m2 = re.search(r"\b([A-Z]{2,6}(?:USD|USDT|BTC|ETH)?(?:/USDT|/USD)?)\b", text or '', re.IGNORECASE)
            if m2:
                signal['symbol'] = m2.group(1).upper()
    
    return signal


def compute_event_key(request, text):
    """Compute unique event key for idempotency"""
    event_key = request.headers.get('X-Event-ID')
    if not event_key:
        # Generate hash from text content
        event_key = hashlib.sha256((text or '').encode('utf-8')).hexdigest()
    return event_key


def is_duplicate_event(event_key):
    """Check if event was already processed (idempotency)"""
    try:
        session = SessionLocal()
        try:
            k = IdempotencyKey(key=event_key)
            session.add(k)
            session.commit()
            return False  # Successfully claimed, not a duplicate
        except IntegrityError:
            session.rollback()
            return True  # Already exists, is a duplicate
        finally:
            session.close()
    except Exception as e:
        LOG.exception('Idempotency check failed: %s', e)
        return False  # On error, allow processing


def persist_signal(signal_data, raw_text):
    """Persist signal to database"""
    session = SessionLocal()
    try:
        sig = Signal(
            source='webhook',
            symbol=signal_data.get('symbol'),
            action=signal_data.get('action'),
            price=signal_data.get('price'),
            raw=raw_text
        )
        session.add(sig)
        session.commit()
        LOG.info('Signal persisted: %s %s @ %s', 
                 signal_data.get('action'), 
                 signal_data.get('symbol'), 
                 signal_data.get('price'))
    finally:
        session.close()


def forward_to_telegram(text, signal_data):
    """Forward signal to Telegram if configured"""
    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
    tg_chat = os.getenv('TELEGRAM_CHAT_ID')
    
    if not (tg_token and tg_chat):
        return
    
    try:
        import requests
        
        # Get trade processing result if available
        trade_result = signal_data.get('trade_result')
        
        # Format message with enhanced status
        message_parts = ['[CHART] *TradingView Signal*\n']
        
        if signal_data.get('action'):
            action = signal_data['action'].upper()
            action_emoji = '[BUY]' if action == 'BUY' else '[SELL]'
            
            # Add status emoji based on trade result
            if trade_result:
                action_taken = trade_result.get('action', '')
                if action_taken == 'blocked':
                    status_emoji = '[BLOCKED]'
                    status_text = 'BLOCKED'
                elif action_taken == 'ignored':
                    status_emoji = '[WARN]'
                    status_text = 'IGNORED'
                elif action_taken == 'opened':
                    status_emoji = '[UP]'
                    status_text = 'OPENED'
                elif action_taken == 'closed_and_opened':
                    status_emoji = '[REFRESH]'
                    status_text = 'SWITCHED'
                else:
                    status_emoji = '[OK]'
                    status_text = 'PROCESSED'
                
                message_parts.append(f"{action_emoji} *{action}* {status_emoji} *{status_text}*")
                
                # Show price verification status
                if action_taken == 'blocked':
                    message_parts.append(f"\n[BLOCKED] *Price Verification Failed*")
                    message_parts.append(f"Signal Price: `${trade_result.get('signal_price')}`")
                    message_parts.append(f"Market Price: `${trade_result.get('market_price', 0):.2f}`")
                    message_parts.append(f"[X] Trade blocked for safety")
                
                if trade_result.get('message'):
                    message_parts.append(f"_{trade_result['message']}_")
                
                # Add Delta Exchange order status
                delta_order = trade_result.get('delta_order')
                if delta_order:
                    if delta_order.get('success'):
                        message_parts.append(f"\n[ORDER] *Delta Exchange Order Placed*")
                        message_parts.append(f"Order ID: `{delta_order.get('order_id')}`")
                        message_parts.append(f"Status: `{delta_order.get('status')}`")
                        if delta_order.get('verified_price'):
                            message_parts.append(f"Verified Price: `{delta_order.get('verified_price'):.2f}`")
                    elif delta_order.get('dry_run'):
                        message_parts.append(f"\n[CONFIG] *Trading Disabled*")
                        message_parts.append(f"_{delta_order.get('message')}_")
                    else:
                        message_parts.append(f"\n[X] *Order Failed*")
                        message_parts.append(f"_{delta_order.get('message')}_")
            else:
                message_parts.append(f"{action_emoji} *{action}*")
        
        if signal_data.get('symbol'):
            message_parts.append(f"Symbol: `{signal_data['symbol']}`")
        if signal_data.get('price'):
            message_parts.append(f"Price: `{signal_data['price']}`")
        if signal_data.get('size'):
            message_parts.append(f"Size: `{signal_data['size']}`")
        
        message_parts.append(f"\n_Raw:_ {text[:150]}...")  # Shorter raw text
        
        message = '\n'.join(message_parts)
        
        send_url = f'https://api.telegram.org/bot{tg_token}/sendMessage'
        payload = {
            'chat_id': tg_chat,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        r = requests.post(send_url, json=payload, timeout=5)
        LOG.info('Telegram forward status: %s', r.status_code)
        
    except Exception as e:
        LOG.exception('Failed to forward to Telegram: %s', e)


def process_trade_signal(signal_data):
    """Process the trade signal with enhanced same-direction handling and Delta Exchange integration"""
    LOG.info('=' * 80)
    LOG.info('[REFRESH] PROCESSING TRADE SIGNAL')
    LOG.info('=' * 80)
    
    action = signal_data.get('action')
    symbol = signal_data.get('symbol')
    price = signal_data.get('price')
    
    LOG.info(f'Signal details: action={action}, symbol={symbol}, price={price}')
    
    if not (action and symbol and price):
        LOG.warning('[WARN] Incomplete signal data, skipping trade processing')
        LOG.warning(f'Missing: action={bool(action)}, symbol={bool(symbol)}, price={bool(price)}')
        return {'action': 'skipped', 'message': 'Incomplete signal data'}
    
    try:
        # Import trading manager and Delta Exchange service
        LOG.debug('Importing trading services...')
        from src.services.trading_service import TradingManager
        from src.services.delta_exchange_service import get_delta_trader
        from decimal import Decimal
        
        LOG.info('Initializing trading manager...')
        trading_manager = TradingManager()
        
        LOG.info('Getting Delta Exchange trader...')
        delta_trader = get_delta_trader()
        
        # STEP 1: VERIFY REAL-TIME PRICE BEFORE PROCESSING SIGNAL
        print('\n' + '=' * 80)
        print('[STEP 1] VERIFYING REAL-TIME PRICE FROM DELTA EXCHANGE')
        print('=' * 80)
        LOG.info('=' * 80)
        LOG.info('[STEP 1] VERIFYING REAL-TIME PRICE FROM DELTA EXCHANGE')
        LOG.info('=' * 80)
        LOG.info(f'Signal Price: ${price}')
        LOG.info(f'Checking current market price for {symbol}...')
        print(f'Signal Price: ${price}')
        print(f'Checking current market price for {symbol}...')
        
        is_valid, current_price, msg = delta_trader.verify_price(symbol, float(price))
        
        if not is_valid:
            print('=' * 80)
            print('[X] PRICE VERIFICATION FAILED - TRADE BLOCKED')
            print('=' * 80)
            print(f'Symbol: {symbol}')
            print(f'Signal Price: ${price}')
            print(f'Current Market Price: ${current_price:.2f}')
            print(f'Reason: {msg}')
            print('[X] Trade will NOT be opened without price confirmation')
            print('=' * 80 + '\n')
            LOG.error('=' * 80)
            LOG.error('[X] PRICE VERIFICATION FAILED - TRADE BLOCKED')
            LOG.error('=' * 80)
            LOG.error(f'Symbol: {symbol}')
            LOG.error(f'Signal Price: ${price}')
            LOG.error(f'Current Market Price: ${current_price:.2f}')
            LOG.error(f'Reason: {msg}')
            LOG.error('[X] Trade will NOT be opened without price confirmation')
            LOG.error('=' * 80)
            return {
                'action': 'blocked',
                'message': f'Price verification failed: {msg}',
                'signal_price': price,
                'market_price': current_price,
                'error': 'Price mismatch - trade blocked for safety'
            }
        
        print('=' * 80)
        print('[OK] PRICE VERIFICATION PASSED')
        print('=' * 80)
        print(f'Symbol: {symbol}')
        print(f'Signal Price: ${price}')
        print(f'Current Market Price: ${current_price:.2f}')
        print(f'Price difference within acceptable tolerance')
        print('[OK] Proceeding with trade processing...')
        print('=' * 80 + '\n')
        LOG.info('=' * 80)
        LOG.info('[OK] PRICE VERIFICATION PASSED')
        LOG.info('=' * 80)
        LOG.info(f'Symbol: {symbol}')
        LOG.info(f'Signal Price: ${price}')
        LOG.info(f'Current Market Price: ${current_price:.2f}')
        LOG.info(f'Price difference within acceptable tolerance')
        LOG.info('[OK] Proceeding with trade processing...')
        LOG.info('=' * 80)
        
        # Handle signal using enhanced TradingManager
        side = action.upper()
        price_decimal = Decimal(str(price))
        
        LOG.info(f'Calling TradingManager.handle_signal: side={side}, symbol={symbol}, price={price_decimal}')
        result = trading_manager.handle_signal(
            user_id=None,
            symbol=symbol,
            side=side,
            price=price_decimal
        )
        
        LOG.info(f'TradingManager result: action={result.get("action")}, message={result.get("message")}')
        
        # Enhanced logging based on action taken
        action_taken = result.get('action', 'unknown')
        message = result.get('message', 'No message')
        
        LOG.info('-' * 80)
        LOG.info(f'Trade action determined: {action_taken}')
        
        # Place order on Delta Exchange if action is opened or closed_and_opened
        if action_taken in ['opened', 'closed_and_opened']:
            LOG.info('=' * 80)
            LOG.info('[ORDER] PLACING ORDER ON DELTA EXCHANGE')
            LOG.info('=' * 80)
            LOG.info(f'Order request: {side} {symbol} @ ${price}')
            
            # Place limit order with size=1
            order_result = delta_trader.place_order(
                symbol=symbol,
                side=side.lower(),
                price=float(price),
                size=1
            )
            
            # Add order result to the response
            result['delta_order'] = order_result
            
            if order_result.get('success'):
                LOG.info('=' * 80)
                LOG.info('[OK] DELTA EXCHANGE ORDER PLACED SUCCESSFULLY')
                LOG.info('=' * 80)
                LOG.info(f'Order ID: {order_result.get("order_id")}')
                LOG.info(f'Status: {order_result.get("status")}')
                LOG.info(f'Message: {order_result.get("message")}')
                LOG.info('=' * 80)
            elif order_result.get('dry_run'):
                LOG.info('=' * 80)
                LOG.info('[CONFIG] DELTA EXCHANGE TRADING DISABLED (DRY RUN)')
                LOG.info('=' * 80)
                LOG.info(f'Message: {order_result.get("message")}')
                LOG.info('=' * 80)
            else:
                LOG.error('=' * 80)
                LOG.error('[X] DELTA EXCHANGE ORDER FAILED')
                LOG.error('=' * 80)
                LOG.error(f'Message: {order_result.get("message")}')
                LOG.error(f'Error: {order_result.get("error")}')
                LOG.error('=' * 80)
        else:
            LOG.info(f'No Delta Exchange order needed (action: {action_taken})')
        
        if action_taken == 'ignored':
            LOG.info(
                '[WARN] Signal IGNORED: %s %s @ %s - %s',
                side, symbol, price, message
            )
        elif action_taken == 'opened':
            LOG.info(
                '[UP] Trade OPENED: %s %s @ %s - %s',
                side, symbol, price, message
            )
        elif action_taken == 'closed_and_opened':
            closed_count = len(result.get('closed', []))
            LOG.info(
                '[REFRESH] Trade SWITCHED: %s %s @ %s - Closed %d, Opened 1 - %s',
                side, symbol, price, closed_count, message
            )
        else:
            LOG.info(
                'Trade signal processed: %s %s @ %s - Action: %s, Message: %s',
                side, symbol, price, action_taken, message
            )
        
        return result
            
    except Exception as e:
        LOG.exception('Failed to process trade: %s', e)
        return {'action': 'error', 'message': f'Processing failed: {str(e)}'}
