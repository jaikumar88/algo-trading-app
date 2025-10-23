"""
Metrics API - Dashboard data endpoints
Provides aggregated data for the trading dashboard
"""
from flask import Blueprint, jsonify
from src.database.session import SessionLocal
from src.models.base import Trade, Signal
from sqlalchemy import func, and_
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Create metrics blueprint
metrics_bp = Blueprint('metrics', __name__, url_prefix='/api/metrics')

@metrics_bp.route('/')
def get_dashboard_metrics():
    """Get dashboard metrics for charts and summaries"""
    session = SessionLocal()
    
    try:
        # Current date calculations
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        # Today's metrics
        today_trades = session.query(Trade).filter(
            Trade.open_time >= today_start
        ).all()
        
        today_count = len(today_trades)
        today_pnl = sum((t.close_price or t.open_price) - t.open_price 
                       for t in today_trades if t.open_price)
        
        # Hourly distribution for today
        hour_counts = [0] * 24
        for trade in today_trades:
            if trade.open_time:
                hour = trade.open_time.hour
                hour_counts[hour] += 1
                
        hours = [f"{i:02d}:00" for i in range(24)]
        
        # Weekly data
        weekly_trades = session.query(Trade).filter(
            Trade.open_time >= week_start
        ).all()
        
        # Group by day for weekly chart
        week_labels = []
        week_values = []
        for i in range(7):
            day_start = today_start - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_trades = [t for t in weekly_trades 
                         if t.open_time and day_start <= t.open_time < day_end]
            day_pnl = sum((t.close_price or t.open_price) - t.open_price 
                         for t in day_trades if t.open_price)
            
            week_labels.insert(0, day_start.strftime('%m/%d'))
            week_values.insert(0, day_pnl)
        
        # Monthly data (weekly aggregation)
        month_labels = []
        month_values = []
        for i in range(4):
            week_start_date = today_start - timedelta(days=i*7)
            week_end_date = week_start_date + timedelta(days=7)
            
            week_trades = session.query(Trade).filter(
                and_(Trade.open_time >= week_start_date - timedelta(days=30),
                     Trade.open_time < week_end_date - timedelta(days=30))
            ).all()
            
            week_pnl = sum((t.close_price or t.open_price) - t.open_price 
                          for t in week_trades if t.open_price)
            
            month_labels.insert(0, f"W{4-i}")
            month_values.insert(0, week_pnl)
        
        # Signal metrics
        total_signals = session.query(Signal).count()
        pending_signals = session.query(Signal).filter(
            Signal.status == 'PENDING'
        ).count() if hasattr(Signal, 'status') else 0
        
        return jsonify({
            'today': {
                'count': today_count,
                'pnl': today_pnl,
                'hours': hours,
                'hour_counts': hour_counts
            },
            'week': {
                'labels': week_labels,
                'values': week_values
            },
            'month': {
                'labels': month_labels,
                'values': month_values
            },
            'signals': {
                'total': total_signals,
                'pending': pending_signals
            },
            'summary': {
                'total_trades': session.query(Trade).count(),
                'open_trades': session.query(Trade).filter(
                    Trade.status == 'OPEN'
                ).count(),
                'total_pnl': sum((t.close_price or t.open_price) - t.open_price 
                               for t in session.query(Trade).all() if t.open_price)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        session.close()

@metrics_bp.route('/trades/recent')
def get_recent_trades():
    """Get recent trades for dashboard table"""
    session = SessionLocal()
    
    try:
        # Get last 10 trades
        recent_trades = session.query(Trade).order_by(
            Trade.open_time.desc()
        ).limit(10).all()
        
        trades_data = []
        for trade in recent_trades:
            trades_data.append({
                'id': trade.id,
                'symbol': trade.symbol,
                'action': trade.action,
                'quantity': float(trade.quantity) if trade.quantity else 0,
                'open_price': float(trade.open_price) if trade.open_price else 0,
                'close_price': float(trade.close_price) if trade.close_price else None,
                'status': trade.status,
                'open_time': trade.open_time.isoformat() if trade.open_time else None,
                'close_time': trade.close_time.isoformat() if trade.close_time else None
            })
        
        return jsonify({
            'trades': trades_data,
            'total': len(trades_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting recent trades: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        session.close()