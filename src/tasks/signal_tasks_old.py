"""Background processing tasks for signals.

This module exposes a single function `process_signal_task` which can be
enqueued via RQ or called synchronously from `app.py` when Redis is not
configured.
"""
from decimal import Decimal
import logging

from db import SessionLocal
from trading import TradingManager
from models import Signal, IdempotencyKey

LOG = logging.getLogger("rag_project.tasks")


def process_signal_task(event_key: str, text: str, pre_action, pre_symbol, pre_price, summary):
    """Process a raw signal: persist Signal, handle trades, persist
    idempotency key.

    This is safe to run in a worker process or synchronously.
    """
    session = SessionLocal()
    try:
        # Persist Signal (best-effort)
        try:
            sig = Signal(
                source="webhook",
                symbol=pre_symbol or None,
                action=pre_action or None,
                price=pre_price,
                raw=text,
            )
            session.add(sig)
            session.commit()
        except Exception:
            session.rollback()
            LOG.exception("Failed to persist Signal in task")

        # Use pre-extracted metadata to decide whether to execute a trade
        action = pre_action
        price = pre_price
        symbol = pre_symbol

        if action and symbol and price:
            try:
                # Quick check: warn if there's already an open trade for this symbol
                from models import Trade
                from sqlalchemy import select
                
                existing_open = session.execute(
                    select(Trade).where(
                        Trade.symbol == symbol,
                        Trade.status == "OPEN"
                    )
                ).scalars().first()
                
                if existing_open:
                    LOG.warning(
                        f"⚠️ Signal received for {symbol} ({action}) but there's already an OPEN {existing_open.action} trade. "
                        f"Will close existing and open new trade."
                    )
                
                tm = TradingManager(session=session)
                res = tm.handle_signal(None, symbol, action, Decimal(str(price)))
                LOG.info("Task persisted trading action: %s", res)
                
                # Log the result for monitoring
                if res.get('closed'):
                    LOG.info(f"✅ Closed {len(res['closed'])} existing trade(s) for {symbol}")
                LOG.info(f"✅ Opened new {action} trade for {symbol} at {price}")
                
            except Exception:
                session.rollback()
                LOG.exception("Failed to persist trade in task")

        # Persist idempotency key (transactional - if duplicate insertion
        # occurs treat as already processed)
        try:
            k = IdempotencyKey(key=event_key)
            session.add(k)
            try:
                session.commit()
            except Exception:
                session.rollback()
                LOG.info("Idempotency key already present: %s", event_key)
        except Exception:
            LOG.exception("Failed to persist idempotency key in task")
    finally:
        try:
            session.close()
        except Exception:
            pass


def collect_price_data_task(use_mock=True, timeframe='1h'):
    """
    Background task to collect historical price data for all enabled instruments.
    
    Args:
        use_mock: If True, generate mock data; otherwise fetch from Binance
        timeframe: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
    
    This task should be scheduled to run periodically (e.g., every hour for 1h timeframe)
    to keep historical data up-to-date.
    """
    from price_history_service import PriceHistoryService
    
    session = SessionLocal()
    try:
        service = PriceHistoryService(session)
        results = service.collect_all_instruments(timeframe=timeframe, use_mock=use_mock)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        total_saved = sum(r.get('saved_count', 0) for r in results)
        
        LOG.info(
            f"Price data collection completed: {success_count}/{len(results)} instruments, "
            f"{total_saved} new candles saved (timeframe={timeframe}, mock={use_mock})"
        )
        
        return {
            'status': 'completed',
            'timeframe': timeframe,
            'total_instruments': len(results),
            'successful': success_count,
            'total_candles_saved': total_saved,
            'results': results
        }
        
    except Exception as e:
        LOG.exception(f"Error in collect_price_data_task: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        try:
            session.close()
        except Exception:
            pass

