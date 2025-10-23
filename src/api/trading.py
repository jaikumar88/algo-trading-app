"""
Trading Management API Endpoints
Handles trade history, positions, instrument management, risk control
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from src.database.session import SessionLocal
from src.models.base import (
    Trade, AllowedInstrument, SystemSettings, FundAllocation, Signal
)

trading_bp = Blueprint('trading', __name__, url_prefix='/api/trading')


# =============================================================================
# TRADE HISTORY & POSITIONS
# =============================================================================

@trading_bp.route('/trades', methods=['GET'])
def get_trades():
    """Get all trades with optional filters."""
    session = SessionLocal()
    try:
        # Get query parameters
        status = request.args.get('status')  # OPEN, CLOSED, or None for all
        symbol = request.args.get('symbol')
        limit = int(request.args.get('limit', 100))
        
        # Support both 'page' and 'offset' parameters
        page = request.args.get('page')
        if page:
            # Convert page number to offset (page 1 = offset 0)
            offset = (int(page) - 1) * limit
        else:
            offset = int(request.args.get('offset', 0))
        
        # Build query
        query = select(Trade)
        
        if status:
            query = query.where(Trade.status == status.upper())
        if symbol:
            query = query.where(Trade.symbol == symbol)
        
        # Order by most recent first
        query = query.order_by(Trade.open_time.desc())
        query = query.limit(limit).offset(offset)
        
        trades = session.execute(query).scalars().all()
        
        # Calculate current P&L for open trades (would need live price)
        trade_list = []
        for t in trades:
            trade_dict = {
                'id': t.id,
                'symbol': t.symbol,
                'action': t.action,
                'quantity': float(t.quantity),
                'open_price': float(t.open_price),
                'open_time': t.open_time.isoformat() if t.open_time else None,
                'close_price': float(t.close_price) if t.close_price else None,
                'close_time': t.close_time.isoformat() if t.close_time else None,
                'status': t.status,
                'profit_loss': float(t.profit_loss) if t.profit_loss else None,
                'total_cost': float(t.total_cost) if t.total_cost else None,
                'allocated_fund': float(t.allocated_fund) if t.allocated_fund else None,
                'risk_amount': float(t.risk_amount) if t.risk_amount else None,
                'stop_loss': float(t.stop_loss) if t.stop_loss else None,
                'take_profit': float(t.take_profit) if t.take_profit else None,
                'stop_loss_triggered': t.stop_loss_triggered,
                'closed_by_user': t.closed_by_user,
            }
            trade_list.append(trade_dict)
        
        # Get summary statistics
        total_count = session.execute(
            select(func.count(Trade.id))
        ).scalar()
        
        open_count = session.execute(
            select(func.count(Trade.id)).where(Trade.status == 'OPEN')
        ).scalar()
        
        closed_count = session.execute(
            select(func.count(Trade.id)).where(Trade.status == 'CLOSED')
        ).scalar()
        
        total_pnl = session.execute(
            select(func.sum(Trade.profit_loss)).where(Trade.status == 'CLOSED')
        ).scalar() or 0
        
        # Calculate pagination info
        current_page = (offset // limit) + 1 if limit > 0 else 1
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
        
        return jsonify({
            'trades': trade_list,
            'summary': {
                'total': total_count,
                'open': open_count,
                'closed': closed_count,
                'total_pnl': float(total_pnl),
            },
            'pagination': {
                'page': current_page,
                'limit': limit,
                'offset': offset,
                'total': total_count,
                'total_pages': total_pages,
                'has_next': offset + limit < total_count,
                'has_prev': offset > 0,
            }
        })
    finally:
        session.close()


@trading_bp.route('/positions', methods=['GET'])
def get_open_positions():
    """Get all currently open positions."""
    session = SessionLocal()
    try:
        query = select(Trade).where(Trade.status == 'OPEN').order_by(Trade.open_time.desc())
        trades = session.execute(query).scalars().all()
        
        positions = []
        total_exposure = Decimal('0')
        
        for t in trades:
            position = {
                'id': t.id,
                'symbol': t.symbol,
                'action': t.action,
                'quantity': float(t.quantity),
                'open_price': float(t.open_price),
                'open_time': t.open_time.isoformat() if t.open_time else None,
                'allocated_fund': float(t.allocated_fund) if t.allocated_fund else None,
                'risk_amount': float(t.risk_amount) if t.risk_amount else None,
                # Would need live price to calculate current P&L
                'current_pnl': None,  # TODO: integrate with price feed
            }
            positions.append(position)
            
            if t.total_cost:
                total_exposure += t.total_cost
        
        return jsonify({
            'positions': positions,
            'total_exposure': float(total_exposure),
            'count': len(positions),
        })
    finally:
        session.close()


@trading_bp.route('/trades/<int:trade_id>/close', methods=['POST'])
def close_trade(trade_id):
    """Manually close an open trade."""
    session = SessionLocal()
    try:
        data = request.json or {}
        close_price = data.get('close_price')
        
        if not close_price:
            return jsonify({'error': 'close_price is required'}), 400
        
        close_price = Decimal(str(close_price))
        
        # Get the trade
        trade = session.execute(
            select(Trade).where(Trade.id == trade_id, Trade.status == 'OPEN')
        ).scalar_one_or_none()
        
        if not trade:
            return jsonify({'error': 'Trade not found or already closed'}), 404
        
        # Close the trade
        trade.close_price = close_price
        trade.close_time = datetime.utcnow()
        trade.status = 'CLOSED'
        trade.closed_by_user = True
        
        # Calculate P&L
        close_amount = close_price * trade.quantity
        open_amount = trade.total_cost or (trade.open_price * trade.quantity)
        
        if trade.action == "BUY":
            trade.profit_loss = close_amount - open_amount
        else:  # SELL
            trade.profit_loss = open_amount - close_amount
        
        session.commit()
        session.refresh(trade)
        
        return jsonify({
            'success': True,
            'trade': {
                'id': trade.id,
                'symbol': trade.symbol,
                'action': trade.action,
                'close_price': float(trade.close_price),
                'profit_loss': float(trade.profit_loss),
                'status': trade.status,
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/trades/<int:trade_id>', methods=['DELETE'])
def delete_trade(trade_id):
    """Delete a trade record from history."""
    session = SessionLocal()
    try:
        # Get the trade
        trade = session.execute(
            select(Trade).where(Trade.id == trade_id)
        ).scalar_one_or_none()
        
        if not trade:
            return jsonify({'error': 'Trade not found'}), 404
        
        # Delete the trade
        session.delete(trade)
        session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Trade #{trade_id} deleted successfully'
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# =============================================================================
# INSTRUMENT MANAGEMENT
# =============================================================================

@trading_bp.route('/instruments', methods=['GET'])
def get_instruments():
    """Get all allowed instruments."""
    session = SessionLocal()
    try:
        query = select(AllowedInstrument).order_by(AllowedInstrument.symbol)
        instruments = session.execute(query).scalars().all()
        
        result = []
        for inst in instruments:
            result.append({
                'id': inst.id,
                'symbol': inst.symbol,
                'name': inst.name,
                'enabled': inst.enabled,
                'created_at': inst.created_at.isoformat() if inst.created_at else None,
            })
        
        return jsonify({'instruments': result})
    finally:
        session.close()


@trading_bp.route('/instruments', methods=['POST'])
def add_instrument():
    """Add a new allowed instrument."""
    session = SessionLocal()
    try:
        data = request.json or {}
        symbol = data.get('symbol', '').upper().strip()
        name = data.get('name', '').strip()
        enabled = data.get('enabled', True)
        
        if not symbol:
            return jsonify({'error': 'symbol is required'}), 400
        
        # Check if already exists
        existing = session.execute(
            select(AllowedInstrument).where(AllowedInstrument.symbol == symbol)
        ).scalar_one_or_none()
        
        if existing:
            return jsonify({'error': f'Instrument {symbol} already exists'}), 409
        
        instrument = AllowedInstrument(
            symbol=symbol,
            name=name or symbol,
            enabled=enabled,
        )
        
        session.add(instrument)
        session.commit()
        session.refresh(instrument)
        
        return jsonify({
            'success': True,
            'instrument': {
                'id': instrument.id,
                'symbol': instrument.symbol,
                'name': instrument.name,
                'enabled': instrument.enabled,
            }
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/instruments/<int:instrument_id>', methods=['PUT'])
def update_instrument(instrument_id):
    """Update an instrument (enable/disable or change name)."""
    session = SessionLocal()
    try:
        data = request.json or {}
        
        instrument = session.execute(
            select(AllowedInstrument).where(AllowedInstrument.id == instrument_id)
        ).scalar_one_or_none()
        
        if not instrument:
            return jsonify({'error': 'Instrument not found'}), 404
        
        if 'name' in data:
            instrument.name = data['name']
        if 'enabled' in data:
            instrument.enabled = bool(data['enabled'])
        
        session.commit()
        session.refresh(instrument)
        
        return jsonify({
            'success': True,
            'instrument': {
                'id': instrument.id,
                'symbol': instrument.symbol,
                'name': instrument.name,
                'enabled': instrument.enabled,
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/instruments/<int:instrument_id>', methods=['DELETE'])
def delete_instrument(instrument_id):
    """Delete an instrument."""
    session = SessionLocal()
    try:
        instrument = session.execute(
            select(AllowedInstrument).where(AllowedInstrument.id == instrument_id)
        ).scalar_one_or_none()
        
        if not instrument:
            return jsonify({'error': 'Instrument not found'}), 404
        
        session.delete(instrument)
        session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# =============================================================================
# SYSTEM SETTINGS & CONTROL
# =============================================================================

@trading_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get all system settings."""
    session = SessionLocal()
    try:
        query = select(SystemSettings)
        settings = session.execute(query).scalars().all()
        
        result = {}
        for setting in settings:
            # Convert value based on type
            if setting.value_type == 'boolean':
                value = setting.value.lower() == 'true' if setting.value else False
            elif setting.value_type == 'float':
                value = float(setting.value) if setting.value else 0.0
            elif setting.value_type == 'int':
                value = int(setting.value) if setting.value else 0
            else:
                value = setting.value
            
            result[setting.key] = {
                'value': value,
                'type': setting.value_type,
                'description': setting.description,
            }
        
        return jsonify({'settings': result})
    finally:
        session.close()


@trading_bp.route('/settings/<key>', methods=['PUT'])
def update_setting(key):
    """Update a system setting."""
    session = SessionLocal()
    try:
        data = request.json or {}
        new_value = data.get('value')
        
        if new_value is None:
            return jsonify({'error': 'value is required'}), 400
        
        setting = session.execute(
            select(SystemSettings).where(SystemSettings.key == key)
        ).scalar_one_or_none()
        
        if not setting:
            return jsonify({'error': f'Setting {key} not found'}), 404
        
        # Convert value to string for storage
        setting.value = str(new_value)
        setting.updated_at = datetime.utcnow()
        
        session.commit()
        session.refresh(setting)
        
        return jsonify({
            'success': True,
            'setting': {
                'key': setting.key,
                'value': new_value,
                'type': setting.value_type,
            }
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/fund-allocations', methods=['GET'])
def get_fund_allocations():
    """Get fund allocations for all instruments."""
    session = SessionLocal()
    try:
        query = select(FundAllocation).order_by(FundAllocation.symbol)
        allocations = session.execute(query).scalars().all()
        
        result = []
        for alloc in allocations:
            result.append({
                'id': alloc.id,
                'symbol': alloc.symbol,
                'allocated_amount': float(alloc.allocated_amount),
                'used_amount': float(alloc.used_amount),
                'total_loss': float(alloc.total_loss),
                'risk_limit': float(alloc.risk_limit),
                'trading_enabled': alloc.trading_enabled,
                'available': float(alloc.allocated_amount - alloc.used_amount),
                'loss_percentage': float((alloc.total_loss / alloc.allocated_amount) * 100) if alloc.allocated_amount > 0 else 0,
            })
        
        return jsonify({'allocations': result})
    finally:
        session.close()


# =============================================================================
# CHART DATA
# =============================================================================

@trading_bp.route('/chart/<symbol>', methods=['GET'])
def get_chart_data(symbol):
    """Get historical price data for charting.
    
    Query params:
    - timeframe: 1m, 5m, 15m, 1h, 4h, 1d (default: 1h)
    - limit: number of candles to return (default: 200)
    """
    try:
        timeframe = request.args.get('timeframe', '1h')
        limit = int(request.args.get('limit', 200))
        
        # TODO: Integrate with real price feed API (Binance, Coinbase, etc.)
        # For now, returning sample data structure
        
        import time
        from decimal import Decimal
        
        candles = []
        volumes = []
        base_price = Decimal('50000')
        current_time = int(time.time())
        
        # Determine time interval in seconds
        interval_map = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400
        }
        interval = interval_map.get(timeframe, 3600)
        
        # Generate sample data
        for i in range(limit):
            timestamp = current_time - ((limit - i) * interval)
            open_price = float(base_price)
            close_price = open_price + (float(base_price) * 0.002 * (2 * (i % 2) - 1))
            high_price = max(open_price, close_price) * 1.001
            low_price = min(open_price, close_price) * 0.999
            volume = 500 + (i % 100) * 5
            
            candles.append({
                'time': timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price
            })
            
            volumes.append({
                'time': timestamp,
                'value': volume,
                'color': '#26a69a80' if close_price >= open_price else '#ef535080'
            })
            
            base_price = Decimal(str(close_price))
        
        return jsonify({
            'symbol': symbol,
            'timeframe': timeframe,
            'candles': candles,
            'volumes': volumes,
            'count': len(candles)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@trading_bp.route('/chart/<symbol>/live', methods=['GET'])
def get_live_price(symbol):
    """Get current live price for a symbol.
    
    TODO: Integrate with real-time WebSocket feed
    """
    try:
        # TODO: Get real live price from exchange API
        # For now, returning sample data
        
        import random
        import time
        base_price = 50000
        current_price = base_price + (random.random() - 0.5) * base_price * 0.01
        
        return jsonify({
            'symbol': symbol,
            'price': current_price,
            'timestamp': int(time.time()),
            'volume_24h': random.randint(10000, 50000)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# SIGNALS
# =============================================================================

@trading_bp.route('/signals', methods=['GET'])
def get_signals():
    """Get trading signals with optional filters."""
    session = SessionLocal()
    try:
        # Get query parameters
        symbol = request.args.get('symbol')
        action = request.args.get('action')  # BUY or SELL
        source = request.args.get('source')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = select(Signal)
        
        if symbol:
            query = query.where(Signal.symbol == symbol.upper())
        if action:
            query = query.where(Signal.action == action.upper())
        if source:
            query = query.where(Signal.source == source)
        
        # Order by most recent first
        query = query.order_by(Signal.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        signals = session.execute(query).scalars().all()
        
        # Convert to list of dicts
        signal_list = []
        for s in signals:
            signal_dict = {
                'id': s.id,
                'source': s.source,
                'symbol': s.symbol,
                'action': s.action,
                'price': float(s.price) if s.price else None,
                'raw': s.raw,
                'created_at': s.created_at.isoformat() if s.created_at else None,
            }
            signal_list.append(signal_dict)
        
        # Get total count
        total_count = session.execute(
            select(func.count(Signal.id))
        ).scalar()
        
        return jsonify({
            'signals': signal_list,
            'count': len(signal_list),
            'total': total_count,
            'pagination': {
                'limit': limit,
                'offset': offset,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/signals/<int:signal_id>', methods=['GET'])
def get_signal(signal_id):
    """Get a specific signal by ID."""
    session = SessionLocal()
    try:
        signal = session.execute(
            select(Signal).where(Signal.id == signal_id)
        ).scalar_one_or_none()
        
        if not signal:
            return jsonify({'error': 'Signal not found'}), 404
        
        return jsonify({
            'id': signal.id,
            'source': signal.source,
            'symbol': signal.symbol,
            'action': signal.action,
            'price': float(signal.price) if signal.price else None,
            'raw': signal.raw,
            'status': getattr(signal, 'status', 'PENDING'),
            'confidence_score': getattr(signal, 'confidence_score', None),
            'validation_notes': getattr(signal, 'validation_notes', None),
            'validated_by': getattr(signal, 'validated_by', None),
            'trade_id': getattr(signal, 'trade_id', None),
            'created_at': signal.created_at.isoformat() if signal.created_at else None,
            'updated_at': getattr(signal, 'updated_at', None).isoformat() if getattr(signal, 'updated_at', None) else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# =============================================================================
# SIGNAL MANAGEMENT & VALIDATION
# =============================================================================

@trading_bp.route('/signals/<int:signal_id>/validate', methods=['POST'])
def validate_signal(signal_id):
    """
    Validate or reject a signal.
    Used to mark signals as false positives or confirm valid signals.
    """
    session = SessionLocal()
    try:
        data = request.get_json()
        
        # Get the signal
        signal = session.execute(
            select(Signal).where(Signal.id == signal_id)
        ).scalar_one_or_none()
        
        if not signal:
            return jsonify({'error': 'Signal not found'}), 404
        
        # Check if already processed
        if hasattr(signal, 'status') and signal.status in ['EXECUTED', 'REJECTED']:
            return jsonify({
                'error': f'Signal already {signal.status.lower()}',
                'signal_id': signal_id,
                'status': signal.status
            }), 400
        
        # Update signal status
        is_valid = data.get('is_valid', True)
        validation_notes = data.get('notes', '')
        validated_by = data.get('validated_by', 'system')
        confidence_score = data.get('confidence_score')
        
        if hasattr(signal, 'status'):
            signal.status = 'VALIDATED' if is_valid else 'FALSE'
            signal.validated_by = validated_by
            signal.validation_notes = validation_notes
            
            if confidence_score is not None:
                signal.confidence_score = float(confidence_score)
        
        session.commit()
        
        return jsonify({
            'signal_id': signal_id,
            'status': 'VALIDATED' if is_valid else 'FALSE',
            'message': 'Signal validated successfully' if is_valid else 'Signal marked as false',
            'validation_notes': validation_notes,
            'validated_by': validated_by
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/signals/<int:signal_id>/reject', methods=['POST'])
def reject_signal(signal_id):
    """
    Mark a signal as false/rejected.
    Quick endpoint to reject false signals.
    """
    session = SessionLocal()
    try:
        data = request.get_json() or {}
        
        signal = session.execute(
            select(Signal).where(Signal.id == signal_id)
        ).scalar_one_or_none()
        
        if not signal:
            return jsonify({'error': 'Signal not found'}), 404
        
        reason = data.get('reason', 'False signal')
        rejected_by = data.get('rejected_by', 'user')
        
        if hasattr(signal, 'status'):
            signal.status = 'REJECTED'
            signal.validated_by = rejected_by
            signal.validation_notes = reason
        
        session.commit()
        
        return jsonify({
            'signal_id': signal_id,
            'status': 'REJECTED',
            'message': 'Signal rejected successfully',
            'reason': reason,
            'rejected_by': rejected_by
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/signals/<int:signal_id>/execute', methods=['POST'])
def execute_signal(signal_id):
    """
    Execute a signal - place trade based on signal.
    Links the signal to a trade and marks it as executed.
    """
    session = SessionLocal()
    try:
        data = request.get_json() or {}
        
        signal = session.execute(
            select(Signal).where(Signal.id == signal_id)
        ).scalar_one_or_none()
        
        if not signal:
            return jsonify({'error': 'Signal not found'}), 404
        
        if hasattr(signal, 'status') and signal.status == 'EXECUTED':
            return jsonify({
                'error': 'Signal already executed',
                'trade_id': signal.trade_id
            }), 400
        
        if hasattr(signal, 'status') and signal.status in ['REJECTED', 'FALSE']:
            return jsonify({
                'error': f'Cannot execute {signal.status.lower()} signal'
            }), 400
        
        # Get quantity from request or use default
        quantity = data.get('quantity', 100.0)
        
        # Create trade from signal
        new_trade = Trade(
            symbol=signal.symbol,
            action=signal.action,
            quantity=quantity,
            open_price=signal.price,
            status='OPEN'
        )
        
        session.add(new_trade)
        session.flush()  # Get the trade ID
        
        # Link signal to trade
        if hasattr(signal, 'status'):
            signal.status = 'EXECUTED'
            signal.trade_id = new_trade.id
            signal.executed_at = func.now()
        
        session.commit()
        
        return jsonify({
            'signal_id': signal_id,
            'trade_id': new_trade.id,
            'status': 'EXECUTED',
            'message': 'Signal executed successfully',
            'trade': {
                'id': new_trade.id,
                'symbol': new_trade.symbol,
                'action': new_trade.action,
                'quantity': float(new_trade.quantity),
                'open_price': float(new_trade.open_price),
                'status': new_trade.status
            }
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/signals/stats', methods=['GET'])
def get_signal_stats():
    """
    Get statistics about signals including validation accuracy.
    Helps track false signal rate.
    """
    session = SessionLocal()
    try:
        # Total signals
        total = session.execute(select(func.count(Signal.id))).scalar()
        
        # Count by status (if status column exists)
        stats = {
            'total': total,
            'pending': 0,
            'validated': 0,
            'executed': 0,
            'rejected': 0,
            'false': 0
        }
        
        # Try to get status counts
        try:
            status_counts = session.execute(
                select(Signal.status, func.count(Signal.id))
                .group_by(Signal.status)
            ).all()
            
            for status, count in status_counts:
                if status:
                    stats[status.lower()] = count
        except:
            pass  # Status column might not exist yet
        
        # Calculate accuracy
        total_validated = stats['validated'] + stats['rejected'] + stats['false']
        accuracy = 0
        if total_validated > 0:
            accuracy = round((stats['validated'] / total_validated) * 100, 2)
        
        false_signal_rate = 0
        if total_validated > 0:
            false_signal_rate = round(((stats['rejected'] + stats['false']) / total_validated) * 100, 2)
        
        return jsonify({
            'stats': stats,
            'accuracy': {
                'validation_accuracy': f'{accuracy}%',
                'false_signal_rate': f'{false_signal_rate}%',
                'total_validated': total_validated
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/signals/bulk-validate', methods=['POST'])
def bulk_validate_signals():
    """
    Bulk validate or reject multiple signals at once.
    Useful for batch processing false signals.
    """
    session = SessionLocal()
    try:
        data = request.get_json()
        signal_ids = data.get('signal_ids', [])
        is_valid = data.get('is_valid', True)
        notes = data.get('notes', '')
        validated_by = data.get('validated_by', 'system')
        
        if not signal_ids:
            return jsonify({'error': 'No signal IDs provided'}), 400
        
        updated_count = 0
        errors = []
        
        for signal_id in signal_ids:
            try:
                signal = session.execute(
                    select(Signal).where(Signal.id == signal_id)
                ).scalar_one_or_none()
                
                if signal and hasattr(signal, 'status'):
                    if signal.status not in ['EXECUTED', 'REJECTED']:
                        signal.status = 'VALIDATED' if is_valid else 'FALSE'
                        signal.validated_by = validated_by
                        signal.validation_notes = notes
                        updated_count += 1
            except Exception as e:
                errors.append(f'Signal {signal_id}: {str(e)}')
        
        session.commit()
        
        return jsonify({
            'updated_count': updated_count,
            'total_requested': len(signal_ids),
            'status': 'VALIDATED' if is_valid else 'FALSE',
            'errors': errors if errors else None
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_bp.route('/prices', methods=['GET'])
def get_current_prices():
    """
    Get current market prices for all enabled symbols.
    
    Returns:
        {
            "prices": {
                "BTCUSD": 43250.50,
                "ETHUSD": 2280.75,
                ...
            }
        }
    """
    try:
        from src.services.delta_exchange_service import (
            get_delta_exchange_trader
        )
        
        trader = get_delta_exchange_trader()
        prices = {}
        
        # Get all enabled symbols
        session = SessionLocal()
        enabled_symbols = session.execute(
            select(AllowedInstrument).where(
                AllowedInstrument.enabled == True
            )
        ).scalars().all()
        
        # Fetch current prices from Delta Exchange
        for symbol_obj in enabled_symbols:
            try:
                orderbook = trader.get_orderbook(symbol_obj.symbol)
                if orderbook and 'mid' in orderbook:
                    prices[symbol_obj.symbol] = float(orderbook['mid'])
            except Exception:
                # Skip symbols that fail
                pass
        
        session.close()
        
        return jsonify({'prices': prices})
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'prices': {}
        }), 500
