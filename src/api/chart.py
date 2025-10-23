"""
Chart and Market Data API
Provides OHLCV data, instrument info, and real-time price feeds
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from sqlalchemy import desc, and_
from src.database.session import SessionLocal
from src.models.base import PriceHistory, AllowedInstrument

chart_bp = Blueprint('chart', __name__)
LOG = logging.getLogger(__name__)

# Supported timeframes
VALID_TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']


@chart_bp.route('/api/chart/instruments', methods=['GET'])
def get_instruments():
    """
    Get list of all available trading instruments.
    
    Query params:
        - enabled: Filter by enabled status (true/false)
    
    Returns:
        {
            "instruments": [
                {
                    "symbol": "BTCUSDT",
                    "name": "Bitcoin",
                    "enabled": true,
                    "type": "crypto"
                }
            ]
        }
    """
    try:
        session = SessionLocal()
        query = session.query(AllowedInstrument)
        
        # Filter by enabled status
        enabled_filter = request.args.get('enabled')
        if enabled_filter is not None:
            enabled = enabled_filter.lower() == 'true'
            query = query.filter(AllowedInstrument.enabled == enabled)
        
        instruments = query.order_by(AllowedInstrument.symbol).all()
        
        result = []
        for inst in instruments:
            result.append({
                'symbol': inst.symbol,
                'name': inst.name or inst.symbol,
                'enabled': inst.enabled,
                'created_at': (
                    inst.created_at.isoformat()
                    if inst.created_at else None
                )
            })
        
        return jsonify({'instruments': result}), 200
        
    except Exception as e:
        LOG.exception('Error fetching instruments: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@chart_bp.route('/api/chart/ohlcv', methods=['GET'])
def get_ohlcv_data():
    """
    Get OHLCV (candlestick) data for charting.
    
    Query params:
        - symbol: Trading symbol (required) e.g., BTCUSDT
        - timeframe: Candle timeframe (required) e.g., 1m, 5m, 15m, 1h, 4h, 1d
        - from: Start timestamp (optional) ISO format or Unix timestamp
        - to: End timestamp (optional) ISO format or Unix timestamp
        - limit: Max number of candles (optional, default 500, max 1000)
    
    Returns:
        {
            "symbol": "BTCUSDT",
            "timeframe": "1h",
            "data": [
                {
                    "timestamp": "2025-10-16T10:00:00Z",
                    "open": 43250.50,
                    "high": 43580.25,
                    "low": 43100.00,
                    "close": 43450.75,
                    "volume": 125.45
                }
            ]
        }
    """
    try:
        # Validate required params
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe')
        
        if not symbol:
            return jsonify({'error': 'symbol parameter is required'}), 400
        if not timeframe:
            return jsonify({'error': 'timeframe parameter is required'}), 400
        if timeframe not in VALID_TIMEFRAMES:
            return jsonify({
                'error': f'Invalid timeframe. Must be one of: '
                         f'{", ".join(VALID_TIMEFRAMES)}'
            }), 400
        
        # Parse optional date range
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        limit = request.args.get('limit', 500, type=int)
        
        # Limit validation
        if limit > 1000:
            limit = 1000
        
        session = SessionLocal()
        
        # Build query
        query = session.query(PriceHistory).filter(
            and_(
                PriceHistory.symbol == symbol.upper(),
                PriceHistory.timeframe == timeframe
            )
        )
        
        # Apply date filters
        if from_date:
            try:
                # Try parsing as ISO format first
                if 'T' in from_date or ' ' in from_date:
                    from_dt = datetime.fromisoformat(
                        from_date.replace('Z', '+00:00')
                    )
                else:
                    # Unix timestamp
                    from_dt = datetime.fromtimestamp(float(from_date))
                query = query.filter(PriceHistory.timestamp >= from_dt)
            except (ValueError, TypeError) as e:
                return jsonify({
                    'error': f'Invalid from date format: {e}'
                }), 400
        
        if to_date:
            try:
                if 'T' in to_date or ' ' in to_date:
                    to_dt = datetime.fromisoformat(
                        to_date.replace('Z', '+00:00')
                    )
                else:
                    to_dt = datetime.fromtimestamp(float(to_date))
                query = query.filter(PriceHistory.timestamp <= to_dt)
            except (ValueError, TypeError) as e:
                return jsonify({'error': f'Invalid to date format: {e}'}), 400
        
        # Order by timestamp descending and apply limit
        query = query.order_by(desc(PriceHistory.timestamp)).limit(limit)
        
        candles = query.all()
        
        # Reverse to get chronological order (oldest first)
        candles = list(reversed(candles))
        
        # Format response
        data = []
        for candle in candles:
            data.append({
                'timestamp': candle.timestamp.isoformat(),
                'open': float(candle.open_price),
                'high': float(candle.high_price),
                'low': float(candle.low_price),
                'close': float(candle.close_price),
                'volume': float(candle.volume)
            })
        
        return jsonify({
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'count': len(data),
            'data': data
        }), 200
        
    except Exception as e:
        LOG.exception('Error fetching OHLCV data: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@chart_bp.route('/api/chart/latest-price', methods=['GET'])
def get_latest_price():
    """
    Get the latest price for a symbol.
    
    Query params:
        - symbol: Trading symbol (required) e.g., BTCUSDT
        - timeframe: Timeframe to use (optional, default 1m)
    
    Returns:
        {
            "symbol": "BTCUSDT",
            "price": 43450.75,
            "timestamp": "2025-10-16T10:00:00Z",
            "change_24h": 2.5,
            "volume_24h": 25000.50
        }
    """
    try:
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe', '1m')
        
        if not symbol:
            return jsonify({'error': 'symbol parameter is required'}), 400
        
        session = SessionLocal()
        
        # Get latest candle
        latest = session.query(PriceHistory).filter(
            and_(
                PriceHistory.symbol == symbol.upper(),
                PriceHistory.timeframe == timeframe
            )
        ).order_by(desc(PriceHistory.timestamp)).first()
        
        if not latest:
            return jsonify({
                'error': f'No price data found for {symbol}'
            }), 404
        
        # Get 24h ago price for change calculation
        time_24h_ago = latest.timestamp - timedelta(hours=24)
        price_24h_ago = session.query(PriceHistory).filter(
            and_(
                PriceHistory.symbol == symbol.upper(),
                PriceHistory.timeframe == timeframe,
                PriceHistory.timestamp >= time_24h_ago
            )
        ).order_by(PriceHistory.timestamp).first()
        
        # Calculate 24h change percentage
        change_24h = 0
        if price_24h_ago:
            old_price = float(price_24h_ago.close_price)
            new_price = float(latest.close_price)
            if old_price > 0:
                change_24h = ((new_price - old_price) / old_price) * 100
        
        # Calculate 24h volume (sum of all candles in last 24h)
        volume_24h_data = session.query(PriceHistory).filter(
            and_(
                PriceHistory.symbol == symbol.upper(),
                PriceHistory.timeframe == timeframe,
                PriceHistory.timestamp >= time_24h_ago
            )
        ).all()
        
        volume_24h = sum(float(c.volume) for c in volume_24h_data)
        
        return jsonify({
            'symbol': symbol.upper(),
            'price': float(latest.close_price),
            'timestamp': latest.timestamp.isoformat(),
            'change_24h': round(change_24h, 2),
            'volume_24h': round(volume_24h, 2),
            'high_24h': float(max(c.high_price for c in volume_24h_data))
            if volume_24h_data else float(latest.high_price),
            'low_24h': float(min(c.low_price for c in volume_24h_data))
            if volume_24h_data else float(latest.low_price)
        }), 200
        
    except Exception as e:
        LOG.exception('Error fetching latest price: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@chart_bp.route('/api/chart/multi-symbol-prices', methods=['POST'])
def get_multi_symbol_prices():
    """
    Get latest prices for multiple symbols in one request.
    
    Request body:
        {
            "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
            "timeframe": "1m"
        }
    
    Returns:
        {
            "prices": {
                "BTCUSDT": {
                    "price": 43450.75,
                    "change_24h": 2.5,
                    "timestamp": "2025-10-16T10:00:00Z"
                },
                ...
            }
        }
    """
    try:
        data = request.get_json() or {}
        symbols = data.get('symbols', [])
        timeframe = data.get('timeframe', '1m')
        
        if not symbols:
            return jsonify({'error': 'symbols array is required'}), 400
        
        session = SessionLocal()
        prices = {}
        
        for symbol in symbols:
            try:
                # Get latest candle
                latest = session.query(PriceHistory).filter(
                    and_(
                        PriceHistory.symbol == symbol.upper(),
                        PriceHistory.timeframe == timeframe
                    )
                ).order_by(desc(PriceHistory.timestamp)).first()
                
                if latest:
                    # Get 24h ago price
                    time_24h_ago = latest.timestamp - timedelta(hours=24)
                    price_24h_ago = session.query(PriceHistory).filter(
                        and_(
                            PriceHistory.symbol == symbol.upper(),
                            PriceHistory.timeframe == timeframe,
                            PriceHistory.timestamp >= time_24h_ago
                        )
                    ).order_by(PriceHistory.timestamp).first()
                    
                    change_24h = 0
                    if price_24h_ago:
                        old_price = float(price_24h_ago.close_price)
                        new_price = float(latest.close_price)
                        if old_price > 0:
                            change_24h = (
                                (new_price - old_price) / old_price
                            ) * 100
                    
                    prices[symbol.upper()] = {
                        'price': float(latest.close_price),
                        'change_24h': round(change_24h, 2),
                        'timestamp': latest.timestamp.isoformat()
                    }
            except Exception as e:
                LOG.warning(
                    'Error fetching price for %s: %s',
                    symbol, e
                )
                prices[symbol.upper()] = {
                    'error': str(e)
                }
        
        return jsonify({'prices': prices}), 200
        
    except Exception as e:
        LOG.exception('Error fetching multi-symbol prices: %s', e)
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
