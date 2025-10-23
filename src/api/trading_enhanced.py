"""
Enhanced Trading API with Chart Integration
Provides order placement, position management, one-click close,
and reverse functionality
"""
from flask import Blueprint, jsonify, request
from decimal import Decimal
from datetime import datetime
import logging
from sqlalchemy import desc, and_
from src.database.session import SessionLocal
from src.models.base import Trade, AllowedInstrument, PriceHistory

trading_enhanced_bp = Blueprint('trading_enhanced', __name__)
LOG = logging.getLogger(__name__)


def get_latest_price(session, symbol: str) -> Decimal:
    """Get the latest price for a symbol from price history."""
    latest = session.query(PriceHistory).filter(
        and_(
            PriceHistory.symbol == symbol.upper(),
            PriceHistory.timeframe == '1m'
        )
    ).order_by(desc(PriceHistory.timestamp)).first()
    
    if not latest:
        raise ValueError(f'No price data found for {symbol}')
    
    return latest.close_price


@trading_enhanced_bp.route('/api/trading/orders', methods=['POST'])
def place_order():
    """
    Place a new trading order (Market or Limit).
    
    Request body:
        {
            "symbol": "BTCUSDT",
            "side": "BUY",  // BUY or SELL
            "type": "MARKET",  // MARKET or LIMIT
            "quantity": 0.1,
            "price": 43250.50,  // Required for LIMIT orders
            "stop_loss": 42000.00,  // Optional
            "take_profit": 45000.00  // Optional
        }
    
    Returns:
        {
            "success": true,
            "trade_id": 123,
            "order": {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quantity": 0.1,
                "price": 43250.50,
                "stop_loss": 42000.00,
                "take_profit": 45000.00,
                "status": "OPEN",
                "timestamp": "2025-10-16T10:00:00Z"
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        symbol = data.get('symbol', '').upper()
        side = data.get('side', '').upper()
        order_type = data.get('type', 'MARKET').upper()
        quantity = data.get('quantity')
        
        if not symbol:
            return jsonify({'error': 'symbol is required'}), 400
        if side not in ['BUY', 'SELL']:
            return jsonify({'error': 'side must be BUY or SELL'}), 400
        if order_type not in ['MARKET', 'LIMIT']:
            return jsonify({'error': 'type must be MARKET or LIMIT'}), 400
        if not quantity:
            return jsonify({'error': 'quantity is required'}), 400
        
        quantity = Decimal(str(quantity))
        
        session = SessionLocal()
        
        # Check if instrument is allowed
        instrument = session.query(AllowedInstrument).filter(
            AllowedInstrument.symbol == symbol
        ).first()
        
        if not instrument:
            return jsonify({
                'error': f'Instrument {symbol} is not available'
            }), 400
        
        if not instrument.enabled:
            return jsonify({
                'error': f'Trading is disabled for {symbol}'
            }), 400
        
        # Validate quantity
        if quantity < instrument.min_quantity:
            return jsonify({
                'error': (
                    f'Quantity must be at least '
                    f'{instrument.min_quantity}'
                )
            }), 400
        
        if instrument.max_quantity and quantity > instrument.max_quantity:
            return jsonify({
                'error': (
                    f'Quantity must not exceed '
                    f'{instrument.max_quantity}'
                )
            }), 400
        
        # Get execution price
        if order_type == 'MARKET':
            # Use latest market price
            price = get_latest_price(session, symbol)
        else:
            # LIMIT order - use specified price
            limit_price = data.get('price')
            if not limit_price:
                return jsonify({
                    'error': 'price is required for LIMIT orders'
                }), 400
            price = Decimal(str(limit_price))
        
        # Optional SL/TP
        stop_loss = data.get('stop_loss')
        take_profit = data.get('take_profit')
        
        if stop_loss:
            stop_loss = Decimal(str(stop_loss))
        if take_profit:
            take_profit = Decimal(str(take_profit))
        
        # Create trade record
        trade = Trade(
            user_id=None,
            action=side,
            symbol=symbol,
            quantity=quantity,
            open_price=price,
            status='OPEN',
            order_type=order_type,
            limit_price=price if order_type == 'LIMIT' else None,
            stop_loss=stop_loss,
            take_profit=take_profit,
            total_cost=price * quantity,
            open_time=datetime.utcnow()
        )
        
        session.add(trade)
        session.commit()
        session.refresh(trade)
        
        LOG.info(
            'Order placed: %s %s %s @ %s (ID: %s)',
            side, quantity, symbol, price, trade.id
        )
        
        return jsonify({
            'success': True,
            'trade_id': trade.id,
            'order': {
                'id': trade.id,
                'symbol': trade.symbol,
                'side': trade.action,
                'type': trade.order_type,
                'quantity': float(trade.quantity),
                'price': float(trade.open_price),
                'stop_loss': float(trade.stop_loss) if trade.stop_loss else None,
                'take_profit': (
                    float(trade.take_profit) if trade.take_profit else None
                ),
                'status': trade.status,
                'timestamp': trade.open_time.isoformat()
            }
        }), 201
        
    except Exception as e:
        LOG.exception('Error placing order: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_enhanced_bp.route(
    '/api/trading/trades/<int:trade_id>/close',
    methods=['POST']
)
def close_trade(trade_id):
    """
    One-click close for a specific trade.
    
    Path params:
        - trade_id: ID of the trade to close
    
    Returns:
        {
            "success": true,
            "trade_id": 123,
            "close_price": 43500.75,
            "profit_loss": 250.25,
            "profit_loss_pct": 0.58,
            "timestamp": "2025-10-16T10:00:00Z"
        }
    """
    try:
        session = SessionLocal()
        
        # Get the trade
        trade = session.query(Trade).filter(
            Trade.id == trade_id
        ).first()
        
        if not trade:
            return jsonify({'error': f'Trade {trade_id} not found'}), 404
        
        if trade.status != 'OPEN':
            return jsonify({
                'error': f'Trade {trade_id} is already closed'
            }), 400
        
        # Get current market price
        close_price = get_latest_price(session, trade.symbol)
        
        # Calculate P&L
        if trade.action == 'BUY':
            # Profit = (Close Price - Open Price) * Quantity
            pnl = (close_price - trade.open_price) * trade.quantity
        else:  # SELL
            # Profit = (Open Price - Close Price) * Quantity
            pnl = (trade.open_price - close_price) * trade.quantity
        
        # Calculate P&L percentage
        pnl_pct = (pnl / trade.total_cost) * 100 if trade.total_cost else 0
        
        # Update trade
        trade.close_price = close_price
        trade.close_time = datetime.utcnow()
        trade.status = 'CLOSED'
        trade.profit_loss = pnl
        trade.closed_by_user = True
        
        session.commit()
        
        LOG.info(
            'Trade closed: ID %s, Symbol %s, P&L: %s (%.2f%%)',
            trade_id, trade.symbol, pnl, pnl_pct
        )
        
        return jsonify({
            'success': True,
            'trade_id': trade.id,
            'symbol': trade.symbol,
            'close_price': float(close_price),
            'profit_loss': float(pnl),
            'profit_loss_pct': round(float(pnl_pct), 2),
            'timestamp': trade.close_time.isoformat()
        }), 200
        
    except Exception as e:
        LOG.exception('Error closing trade: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_enhanced_bp.route(
    '/api/trading/trades/<int:trade_id>/reverse',
    methods=['POST']
)
def reverse_trade(trade_id):
    """
    Reverse a trade: Close current position and open opposite position.
    
    Path params:
        - trade_id: ID of the trade to reverse
    
    Request body (optional):
        {
            "quantity": 0.15,  // Optional: new position size
            "stop_loss": 42000.00,  // Optional: SL for new position
            "take_profit": 45000.00  // Optional: TP for new position
        }
    
    Returns:
        {
            "success": true,
            "closed_trade": {
                "id": 123,
                "symbol": "BTCUSDT",
                "side": "BUY",
                "close_price": 43500.75,
                "profit_loss": 250.25
            },
            "new_trade": {
                "id": 124,
                "symbol": "BTCUSDT",
                "side": "SELL",
                "price": 43500.75,
                "quantity": 0.1
            }
        }
    """
    try:
        data = request.get_json() or {}
        session = SessionLocal()
        
        # Get the trade
        trade = session.query(Trade).filter(
            Trade.id == trade_id
        ).first()
        
        if not trade:
            return jsonify({'error': f'Trade {trade_id} not found'}), 404
        
        if trade.status != 'OPEN':
            return jsonify({
                'error': f'Trade {trade_id} is already closed'
            }), 400
        
        # Get current market price
        current_price = get_latest_price(session, trade.symbol)
        
        # Calculate P&L for closing trade
        if trade.action == 'BUY':
            pnl = (current_price - trade.open_price) * trade.quantity
        else:
            pnl = (trade.open_price - current_price) * trade.quantity
        
        # Close the current trade
        trade.close_price = current_price
        trade.close_time = datetime.utcnow()
        trade.status = 'CLOSED'
        trade.profit_loss = pnl
        trade.closed_by_user = True
        
        # Determine opposite side
        new_side = 'SELL' if trade.action == 'BUY' else 'BUY'
        
        # Use provided quantity or same as closed trade
        new_quantity = data.get('quantity')
        if new_quantity:
            new_quantity = Decimal(str(new_quantity))
        else:
            new_quantity = trade.quantity
        
        # Optional SL/TP for new position
        stop_loss = data.get('stop_loss')
        take_profit = data.get('take_profit')
        
        if stop_loss:
            stop_loss = Decimal(str(stop_loss))
        if take_profit:
            take_profit = Decimal(str(take_profit))
        
        # Create new opposite trade
        new_trade = Trade(
            user_id=trade.user_id,
            action=new_side,
            symbol=trade.symbol,
            quantity=new_quantity,
            open_price=current_price,
            status='OPEN',
            order_type='MARKET',
            stop_loss=stop_loss,
            take_profit=take_profit,
            total_cost=current_price * new_quantity,
            open_time=datetime.utcnow()
        )
        
        session.add(new_trade)
        session.commit()
        session.refresh(new_trade)
        
        LOG.info(
            'Trade reversed: Closed %s %s (P&L: %s), '
            'Opened %s %s @ %s (ID: %s)',
            trade.action, trade.symbol, pnl,
            new_side, trade.symbol, current_price, new_trade.id
        )
        
        return jsonify({
            'success': True,
            'closed_trade': {
                'id': trade.id,
                'symbol': trade.symbol,
                'side': trade.action,
                'close_price': float(current_price),
                'profit_loss': float(pnl),
                'timestamp': trade.close_time.isoformat()
            },
            'new_trade': {
                'id': new_trade.id,
                'symbol': new_trade.symbol,
                'side': new_trade.action,
                'price': float(current_price),
                'quantity': float(new_quantity),
                'stop_loss': float(stop_loss) if stop_loss else None,
                'take_profit': float(take_profit) if take_profit else None,
                'timestamp': new_trade.open_time.isoformat()
            }
        }), 200
        
    except Exception as e:
        LOG.exception('Error reversing trade: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_enhanced_bp.route('/api/trading/positions', methods=['GET'])
def get_open_positions():
    """
    Get all open positions with current P&L.
    
    Query params:
        - symbol: Filter by symbol (optional)
    
    Returns:
        {
            "positions": [
                {
                    "id": 123,
                    "symbol": "BTCUSDT",
                    "side": "BUY",
                    "quantity": 0.1,
                    "open_price": 43250.50,
                    "current_price": 43500.75,
                    "profit_loss": 25.025,
                    "profit_loss_pct": 0.58,
                    "stop_loss": 42000.00,
                    "take_profit": 45000.00,
                    "open_time": "2025-10-16T10:00:00Z"
                }
            ],
            "total_pnl": 25.025
        }
    """
    try:
        symbol_filter = request.args.get('symbol')
        
        session = SessionLocal()
        
        # Get open trades
        query = session.query(Trade).filter(Trade.status == 'OPEN')
        
        if symbol_filter:
            query = query.filter(Trade.symbol == symbol_filter.upper())
        
        trades = query.order_by(desc(Trade.open_time)).all()
        
        positions = []
        total_pnl = Decimal('0')
        
        for trade in trades:
            try:
                # Get current price
                current_price = get_latest_price(session, trade.symbol)
                
                # Calculate current P&L
                if trade.action == 'BUY':
                    pnl = (current_price - trade.open_price) * trade.quantity
                else:
                    pnl = (trade.open_price - current_price) * trade.quantity
                
                pnl_pct = (
                    (pnl / trade.total_cost) * 100
                    if trade.total_cost else 0
                )
                
                total_pnl += pnl
                
                positions.append({
                    'id': trade.id,
                    'symbol': trade.symbol,
                    'side': trade.action,
                    'quantity': float(trade.quantity),
                    'open_price': float(trade.open_price),
                    'current_price': float(current_price),
                    'profit_loss': float(pnl),
                    'profit_loss_pct': round(float(pnl_pct), 2),
                    'stop_loss': (
                        float(trade.stop_loss) if trade.stop_loss else None
                    ),
                    'take_profit': (
                        float(trade.take_profit) if trade.take_profit else None
                    ),
                    'open_time': trade.open_time.isoformat()
                })
            except Exception as e:
                LOG.warning(
                    'Error calculating P&L for trade %s: %s',
                    trade.id, e
                )
        
        return jsonify({
            'positions': positions,
            'total_pnl': float(total_pnl),
            'count': len(positions)
        }), 200
        
    except Exception as e:
        LOG.exception('Error fetching positions: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_enhanced_bp.route(
    '/api/trading/trades/<int:trade_id>/modify',
    methods=['PATCH']
)
def modify_trade(trade_id):
    """
    Modify stop loss and/or take profit for an open trade.
    
    Path params:
        - trade_id: ID of the trade to modify
    
    Request body:
        {
            "stop_loss": 42000.00,  // Optional
            "take_profit": 45000.00  // Optional
        }
    
    Returns:
        {
            "success": true,
            "trade_id": 123,
            "stop_loss": 42000.00,
            "take_profit": 45000.00
        }
    """
    try:
        data = request.get_json() or {}
        session = SessionLocal()
        
        # Get the trade
        trade = session.query(Trade).filter(
            Trade.id == trade_id
        ).first()
        
        if not trade:
            return jsonify({'error': f'Trade {trade_id} not found'}), 404
        
        if trade.status != 'OPEN':
            return jsonify({
                'error': f'Trade {trade_id} is closed, cannot modify'
            }), 400
        
        # Update SL/TP if provided
        if 'stop_loss' in data:
            if data['stop_loss'] is None:
                trade.stop_loss = None
            else:
                trade.stop_loss = Decimal(str(data['stop_loss']))
        
        if 'take_profit' in data:
            if data['take_profit'] is None:
                trade.take_profit = None
            else:
                trade.take_profit = Decimal(str(data['take_profit']))
        
        session.commit()
        
        LOG.info(
            'Trade modified: ID %s, SL: %s, TP: %s',
            trade_id, trade.stop_loss, trade.take_profit
        )
        
        return jsonify({
            'success': True,
            'trade_id': trade.id,
            'stop_loss': float(trade.stop_loss) if trade.stop_loss else None,
            'take_profit': (
                float(trade.take_profit) if trade.take_profit else None
            )
        }), 200
        
    except Exception as e:
        LOG.exception('Error modifying trade: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@trading_enhanced_bp.route('/api/trading/history', methods=['GET'])
def get_trade_history():
    """
    Get trade history with filters.
    
    Query params:
        - symbol: Filter by symbol (optional)
        - from: Start date ISO format (optional)
        - to: End date ISO format (optional)
        - limit: Max results (default 50, max 500)
        - offset: Pagination offset (default 0)
    
    Returns:
        {
            "trades": [...],
            "count": 50,
            "total_profit_loss": 1250.50
        }
    """
    try:
        session = SessionLocal()
        
        # Parse filters
        symbol = request.args.get('symbol')
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = session.query(Trade).filter(Trade.status == 'CLOSED')
        
        if symbol:
            query = query.filter(Trade.symbol == symbol.upper())
        
        if from_date:
            from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            query = query.filter(Trade.close_time >= from_dt)
        
        if to_date:
            to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            query = query.filter(Trade.close_time <= to_dt)
        
        # Order and paginate
        query = query.order_by(desc(Trade.close_time)).limit(limit).offset(
            offset
        )
        
        trades = query.all()
        
        # Format response
        history = []
        total_pnl = Decimal('0')
        
        for trade in trades:
            if trade.profit_loss:
                total_pnl += trade.profit_loss
            
            history.append({
                'id': trade.id,
                'symbol': trade.symbol,
                'side': trade.action,
                'quantity': float(trade.quantity),
                'open_price': float(trade.open_price),
                'close_price': (
                    float(trade.close_price) if trade.close_price else None
                ),
                'profit_loss': (
                    float(trade.profit_loss) if trade.profit_loss else 0
                ),
                'open_time': trade.open_time.isoformat(),
                'close_time': (
                    trade.close_time.isoformat() if trade.close_time else None
                )
            })
        
        return jsonify({
            'trades': history,
            'count': len(history),
            'total_profit_loss': float(total_pnl)
        }), 200
        
    except Exception as e:
        LOG.exception('Error fetching trade history: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
