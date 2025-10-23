"""
Risk Management API Blueprint
Provides endpoints for configuring and monitoring risk management settings.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, func
from src.database.session import SessionLocal
from src.models.base import Trade, SystemSettings

risk_bp = Blueprint('risk', __name__, url_prefix='/api/risk')


@risk_bp.route('/settings', methods=['GET'])
def get_risk_settings():
    """Get current risk management settings."""
    session = SessionLocal()
    
    try:
        # Get settings from database
        settings_query = select(SystemSettings).where(
            SystemSettings.key.like('risk_%')
        )
        db_settings = session.execute(settings_query).scalars().all()
        
        # Default settings
        default_settings = {
            'stop_loss_percent': 1.0,
            'take_profit_percent': 2.0,
            'max_position_size': 100,
            'max_daily_loss': 1000,
            'max_daily_trades': 50,
            'trailing_stop_enabled': False,
            'trailing_stop_percent': 0.5,
            'max_open_positions': 10,
            'max_risk_per_trade': 100,
            'risk_reward_ratio': 2.0,
            'max_portfolio_risk_percent': 5.0,
            'max_correlation_exposure': 3,
            'daily_loss_limit_enabled': True,
            'auto_close_on_daily_limit': True,
            'trading_hours_enabled': False,
            'trading_start_hour': 9,
            'trading_end_hour': 17,
            'avoid_news_events': False,
            'panic_mode': False,
        }
        
        # Override with database values
        settings = default_settings.copy()
        for db_setting in db_settings:
            key = db_setting.key.replace('risk_', '')
            
            # Parse value based on type
            if db_setting.value_type == 'boolean':
                settings[key] = db_setting.value.lower() == 'true'
            elif db_setting.value_type == 'int':
                settings[key] = int(db_setting.value)
            elif db_setting.value_type == 'float':
                settings[key] = float(db_setting.value)
            else:
                settings[key] = db_setting.value
        
        return jsonify({
            'success': True,
            'settings': settings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


@risk_bp.route('/settings', methods=['POST'])
def save_risk_settings():
    """Save risk management settings."""
    session = SessionLocal()
    
    try:
        data = request.json
        
        # Save each setting to database
        for key, value in data.items():
            db_key = f'risk_{key}'
            
            # Determine value type
            if isinstance(value, bool):
                value_type = 'boolean'
                value_str = str(value)
            elif isinstance(value, (int, float)):
                value_type = 'float' if isinstance(value, float) else 'int'
                value_str = str(value)
            else:
                value_type = 'string'
                value_str = str(value)
            
            # Check if setting exists
            existing = session.execute(
                select(SystemSettings).where(SystemSettings.key == db_key)
            ).scalar_one_or_none()
            
            if existing:
                existing.value = value_str
                existing.value_type = value_type
                existing.updated_at = datetime.utcnow()
            else:
                new_setting = SystemSettings(
                    key=db_key,
                    value=value_str,
                    value_type=value_type,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(new_setting)
        
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Risk settings saved successfully'
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


@risk_bp.route('/stats', methods=['GET'])
def get_risk_stats():
    """Get current risk statistics."""
    session = SessionLocal()
    
    try:
        # Get today's date range
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get today's closed trades for P&L calculation
        closed_today = session.execute(
            select(Trade).where(
                Trade.status == 'CLOSED',
                Trade.close_time >= today_start
            )
        ).scalars().all()
        
        # Calculate daily loss
        current_daily_loss = sum(
            abs(float(t.profit_loss)) for t in closed_today 
            if t.profit_loss and float(t.profit_loss) < 0
        )
        
        # Get today's trade count
        current_daily_trades = len(closed_today)
        
        # Get open positions count
        current_open_positions = session.execute(
            select(func.count(Trade.id)).where(Trade.status == 'OPEN')
        ).scalar()
        
        # Get total exposure (sum of all open position costs)
        open_trades = session.execute(
            select(Trade).where(Trade.status == 'OPEN')
        ).scalars().all()
        
        total_exposure = sum(
            float(t.total_cost) if t.total_cost else 0
            for t in open_trades
        )
        
        # Get max daily loss setting
        max_daily_loss_setting = session.execute(
            select(SystemSettings).where(SystemSettings.key == 'risk_max_daily_loss')
        ).scalar_one_or_none()
        
        max_daily_loss = float(max_daily_loss_setting.value) if max_daily_loss_setting else 1000
        
        # Calculate available risk budget
        available_risk_budget = max(0, max_daily_loss - current_daily_loss)
        
        return jsonify({
            'current_daily_loss': current_daily_loss,
            'current_daily_trades': current_daily_trades,
            'current_open_positions': current_open_positions,
            'total_exposure': total_exposure,
            'available_risk_budget': available_risk_budget
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
    finally:
        session.close()


@risk_bp.route('/emergency-close', methods=['POST'])
def emergency_close_all():
    """Emergency close all open positions."""
    session = SessionLocal()
    
    try:
        # Get all open trades
        open_trades = session.execute(
            select(Trade).where(Trade.status == 'OPEN')
        ).scalars().all()
        
        if not open_trades:
            return jsonify({
                'success': True,
                'message': 'No open positions to close',
                'closed_count': 0
            })
        
        closed_count = 0
        
        # Close each trade at current price (would need live price in production)
        for trade in open_trades:
            # In production, fetch actual current price
            # For now, use a placeholder close price
            trade.close_price = trade.open_price  # Replace with actual price
            trade.close_time = datetime.utcnow()
            trade.status = 'CLOSED'
            trade.closed_by_user = True
            
            # Calculate P&L
            if trade.action == 'BUY':
                trade.profit_loss = (trade.close_price - trade.open_price) * trade.quantity
            else:
                trade.profit_loss = (trade.open_price - trade.close_price) * trade.quantity
            
            closed_count += 1
        
        session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Closed {closed_count} position(s)',
            'closed_count': closed_count
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


@risk_bp.route('/panic-mode', methods=['POST'])
def toggle_panic_mode():
    """Toggle panic mode on/off."""
    session = SessionLocal()
    
    try:
        data = request.json
        enabled = data.get('enabled', False)
        
        # Save panic mode setting
        existing = session.execute(
            select(SystemSettings).where(SystemSettings.key == 'risk_panic_mode')
        ).scalar_one_or_none()
        
        if existing:
            existing.value = enabled
            existing.updated_at = datetime.utcnow()
        else:
            new_setting = SystemSettings(
                key='risk_panic_mode',
                value=enabled,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_setting)
        
        session.commit()
        
        return jsonify({
            'success': True,
            'panic_mode': enabled,
            'message': f'Panic mode {"enabled" if enabled else "disabled"}'
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        session.close()


@risk_bp.route('/check', methods=['POST'])
def check_risk_limits():
    """Check if a proposed trade violates risk limits."""
    session = SessionLocal()
    
    try:
        data = request.json
        symbol = data.get('symbol')
        size = float(data.get('size', 0))
        
        # Get risk settings
        settings_query = select(SystemSettings).where(
            SystemSettings.key.like('risk_%')
        )
        db_settings = session.execute(settings_query).scalars().all()
        settings = {s.key.replace('risk_', ''): s.value for s in db_settings}
        
        violations = []
        
        # Check max position size
        max_size = float(settings.get('max_position_size', 100))
        if size > max_size:
            violations.append(f'Position size ({size}) exceeds maximum ({max_size})')
        
        # Check max open positions
        open_count = session.execute(
            select(func.count(Trade.id)).where(Trade.status == 'OPEN')
        ).scalar()
        
        max_open = int(settings.get('max_open_positions', 10))
        if open_count >= max_open:
            violations.append(f'Maximum open positions ({max_open}) reached')
        
        # Check daily trade limit
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        daily_trades = session.execute(
            select(func.count(Trade.id)).where(
                Trade.open_time >= today_start
            )
        ).scalar()
        
        max_daily = int(settings.get('max_daily_trades', 50))
        if daily_trades >= max_daily:
            violations.append(f'Daily trade limit ({max_daily}) reached')
        
        # Check panic mode
        if settings.get('panic_mode', False):
            violations.append('Panic mode is active - all trading suspended')
        
        allowed = len(violations) == 0
        
        return jsonify({
            'allowed': allowed,
            'violations': violations
        })
        
    except Exception as e:
        return jsonify({
            'allowed': False,
            'error': str(e)
        }), 500
    finally:
        session.close()
