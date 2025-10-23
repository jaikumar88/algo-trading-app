"""
Historical Price Data API
Endpoints for managing price data collection and viewing historical prices
"""
from flask import Blueprint, jsonify, request
import logging
from datetime import datetime, timedelta
from sqlalchemy import desc, and_
from src.database.session import SessionLocal
from src.models.base import HistoricalPrice, AllowedInstrument

historical_bp = Blueprint('historical', __name__, url_prefix='/api/historical')
LOG = logging.getLogger(__name__)


@historical_bp.route('/symbols', methods=['GET'])
def get_symbols():
    """Get all instruments with their enabled status"""
    session = SessionLocal()
    try:
        instruments = session.query(AllowedInstrument).all()
        
        result = []
        for inst in instruments:
            result.append({
                'id': inst.id,
                'symbol': inst.symbol,
                'name': inst.name,
                'enabled': inst.enabled,
                'instrument_type': inst.instrument_type,
                'base_currency': inst.base_currency,
                'quote_currency': inst.quote_currency
            })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'symbols': result
        }), 200
        
    except Exception as e:
        LOG.exception(f"Error getting symbols: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@historical_bp.route('/symbols/<symbol>/enable', methods=['POST'])
def enable_symbol(symbol):
    """Enable price collection for a symbol"""
    session = SessionLocal()
    try:
        inst = session.query(AllowedInstrument).filter(
            AllowedInstrument.symbol == symbol
        ).first()
        
        if not inst:
            return jsonify({'error': f'Symbol {symbol} not found'}), 404
        
        inst.enabled = True
        session.commit()
        
        LOG.info(f"[OK] Enabled price collection for {symbol}")
        
        return jsonify({
            'success': True,
            'message': f'Price collection enabled for {symbol}',
            'symbol': symbol,
            'enabled': True
        }), 200
        
    except Exception as e:
        session.rollback()
        LOG.exception(f"Error enabling symbol: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@historical_bp.route('/symbols/<symbol>/disable', methods=['POST'])
def disable_symbol(symbol):
    """Disable price collection for a symbol"""
    session = SessionLocal()
    try:
        inst = session.query(AllowedInstrument).filter(
            AllowedInstrument.symbol == symbol
        ).first()
        
        if not inst:
            return jsonify({'error': f'Symbol {symbol} not found'}), 404
        
        inst.enabled = False
        session.commit()
        
        LOG.info(f"[OK] Disabled price collection for {symbol}")
        
        return jsonify({
            'success': True,
            'message': f'Price collection disabled for {symbol}',
            'symbol': symbol,
            'enabled': False
        }), 200
        
    except Exception as e:
        session.rollback()
        LOG.exception(f"Error disabling symbol: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@historical_bp.route('/prices/<symbol>', methods=['GET'])
def get_historical_prices(symbol):
    """
    Get historical price data for a symbol
    
    Query params:
        - limit: Number of records to return (default: 100, max: 10000)
        - hours: Only get data from last N hours
        - from_time: Start timestamp (ISO format)
        - to_time: End timestamp (ISO format)
    """
    session = SessionLocal()
    try:
        # Parse query parameters
        limit = int(request.args.get('limit', 100))
        limit = min(limit, 10000)  # Max 10000 records
        
        hours = request.args.get('hours')
        from_time = request.args.get('from_time')
        to_time = request.args.get('to_time')
        
        # Build query
        query = session.query(HistoricalPrice).filter(
            HistoricalPrice.symbol == symbol
        )
        
        # Apply time filters
        if hours:
            cutoff = datetime.utcnow() - timedelta(hours=int(hours))
            query = query.filter(HistoricalPrice.timestamp >= cutoff)
        
        if from_time:
            from_dt = datetime.fromisoformat(from_time.replace('Z', '+00:00'))
            query = query.filter(HistoricalPrice.timestamp >= from_dt)
        
        if to_time:
            to_dt = datetime.fromisoformat(to_time.replace('Z', '+00:00'))
            query = query.filter(HistoricalPrice.timestamp <= to_dt)
        
        # Order by timestamp descending and limit
        query = query.order_by(desc(HistoricalPrice.timestamp)).limit(limit)
        
        prices = query.all()
        
        # Format results
        result = []
        for price in prices:
            result.append({
                'timestamp': price.timestamp.isoformat(),
                'bid': float(price.bid_price),
                'ask': float(price.ask_price),
                'mid': float(price.mid_price),
                'spread': float(price.spread),
                'spread_pct': float(price.spread_pct),
                'volume_bid': float(price.volume_bid) if price.volume_bid else None,
                'volume_ask': float(price.volume_ask) if price.volume_ask else None
            })
        
        # Reverse to get chronological order
        result.reverse()
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'count': len(result),
            'prices': result
        }), 200
        
    except Exception as e:
        LOG.exception(f"Error getting historical prices: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@historical_bp.route('/latest', methods=['GET'])
def get_latest_prices():
    """Get latest price for all enabled symbols"""
    session = SessionLocal()
    try:
        # Get enabled symbols
        enabled_symbols = session.query(AllowedInstrument).filter(
            AllowedInstrument.enabled.is_(True)
        ).all()
        
        result = []
        for inst in enabled_symbols:
            # Get latest price
            latest = session.query(HistoricalPrice).filter(
                HistoricalPrice.symbol == inst.symbol
            ).order_by(desc(HistoricalPrice.timestamp)).first()
            
            if latest:
                result.append({
                    'symbol': inst.symbol,
                    'name': inst.name,
                    'timestamp': latest.timestamp.isoformat(),
                    'bid': float(latest.bid_price),
                    'ask': float(latest.ask_price),
                    'mid': float(latest.mid_price),
                    'spread': float(latest.spread),
                    'spread_pct': float(latest.spread_pct)
                })
        
        return jsonify({
            'success': True,
            'count': len(result),
            'prices': result
        }), 200
        
    except Exception as e:
        LOG.exception(f"Error getting latest prices: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@historical_bp.route('/stats/<symbol>', methods=['GET'])
def get_price_stats(symbol):
    """
    Get price statistics for a symbol
    
    Query params:
        - hours: Calculate stats for last N hours (default: 24)
    """
    session = SessionLocal()
    try:
        hours = int(request.args.get('hours', 24))
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        prices = session.query(HistoricalPrice).filter(
            and_(
                HistoricalPrice.symbol == symbol,
                HistoricalPrice.timestamp >= cutoff
            )
        ).all()
        
        if not prices:
            return jsonify({
                'error': f'No data found for {symbol} in last {hours} hours'
            }), 404
        
        # Calculate stats
        mid_prices = [float(p.mid_price) for p in prices]
        spreads = [float(p.spread_pct) for p in prices]
        
        stats = {
            'symbol': symbol,
            'period_hours': hours,
            'data_points': len(prices),
            'first_timestamp': prices[0].timestamp.isoformat(),
            'last_timestamp': prices[-1].timestamp.isoformat(),
            'price': {
                'current': mid_prices[-1],
                'high': max(mid_prices),
                'low': min(mid_prices),
                'avg': sum(mid_prices) / len(mid_prices),
                'change': mid_prices[-1] - mid_prices[0],
                'change_pct': ((mid_prices[-1] - mid_prices[0]) / mid_prices[0] * 100)
                              if mid_prices[0] > 0 else 0
            },
            'spread': {
                'current': spreads[-1],
                'avg': sum(spreads) / len(spreads),
                'min': min(spreads),
                'max': max(spreads)
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        LOG.exception(f"Error getting price stats: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
