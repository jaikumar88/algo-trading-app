"""
Performance Analytics API Endpoints
Track performance, identify patterns, and get improvement suggestions
"""
import logging
from flask import Blueprint, jsonify, request

from src.services.performance_analytics_service import (
    get_performance_analytics
)


LOG = logging.getLogger(__name__)

performance_bp = Blueprint(
    'performance',
    __name__,
    url_prefix='/api/performance'
)


@performance_bp.route('/symbol/<symbol>', methods=['GET'])
def get_symbol_performance(symbol: str):
    """
    Get performance metrics for a specific symbol
    
    Query params:
        days: Number of days to analyze (default: 30)
    
    Example: GET /api/performance/symbol/BTCUSD?days=30
    
    Returns:
        {
            "symbol": "BTCUSD",
            "period_days": 30,
            "total_trades": 25,
            "win_rate": 65.5,
            "total_pnl": 1250.50,
            "risk_reward_ratio": 2.1,
            ...
        }
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        LOG.info(f"[API] Getting performance for {symbol} ({days} days)")
        
        analytics = get_performance_analytics()
        result = analytics.get_symbol_performance(symbol, days)
        
        return jsonify(result), 200
        
    except Exception as e:
        LOG.error(f"[API] Error getting symbol performance: {e}")
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/all', methods=['GET'])
def get_all_performance():
    """
    Get performance for all traded symbols
    
    Query params:
        days: Number of days to analyze (default: 30)
    
    Example: GET /api/performance/all?days=7
    
    Returns:
        [
            {"symbol": "BTCUSD", "win_rate": 70, "total_pnl": 500, ...},
            {"symbol": "ETHUSD", "win_rate": 45, "total_pnl": -150, ...}
        ]
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        LOG.info(f"[API] Getting performance for all symbols ({days} days)")
        
        analytics = get_performance_analytics()
        results = analytics.get_all_symbols_performance(days)
        
        return jsonify({
            'period_days': days,
            'total_symbols': len(results),
            'symbols': results
        }), 200
        
    except Exception as e:
        LOG.error(f"[API] Error getting all performance: {e}")
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/flows', methods=['GET'])
def get_trading_flows():
    """
    Get trading pattern analysis
    
    Query params:
        days: Number of days to analyze (default: 30)
    
    Example: GET /api/performance/flows?days=14
    
    Returns:
        {
            "period_days": 14,
            "total_trades_analyzed": 100,
            "by_hour": {
                "0": {"count": 5, "win_rate": 60, "total_pnl": 100},
                "1": {"count": 3, "win_rate": 33, "total_pnl": -50}
            },
            "by_day": {
                "Monday": {"count": 20, "win_rate": 55, "total_pnl": 200}
            },
            "by_action": {
                "long": {"count": 60, "win_rate": 65, "total_pnl": 800},
                "short": {"count": 40, "win_rate": 50, "total_pnl": 200}
            }
        }
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        LOG.info(f"[API] Getting trading flows ({days} days)")
        
        analytics = get_performance_analytics()
        flows = analytics.identify_trading_flows(days)
        
        return jsonify(flows), 200
        
    except Exception as e:
        LOG.error(f"[API] Error getting trading flows: {e}")
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/suggestions', methods=['GET'])
def get_improvement_suggestions():
    """
    Get improvement suggestions based on performance analysis
    
    Query params:
        days: Number of days to analyze (default: 30)
    
    Example: GET /api/performance/suggestions?days=30
    
    Returns:
        [
            {
                "priority": "high",
                "category": "Win Rate",
                "suggestion": "Consider avoiding symbols with low win rates",
                "details": "Symbols with <40% win rate: XYZ, ABC",
                "affected_symbols": ["XYZ", "ABC"],
                "metric": "win_rate"
            },
            ...
        ]
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        LOG.info(f"[API] Getting improvement suggestions ({days} days)")
        
        analytics = get_performance_analytics()
        suggestions = analytics.get_improvement_suggestions(days)
        
        return jsonify({
            'period_days': days,
            'total_suggestions': len(suggestions),
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        LOG.error(f"[API] Error getting suggestions: {e}")
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/dashboard', methods=['GET'])
def get_performance_dashboard():
    """
    Get comprehensive performance dashboard data
    
    Query params:
        days: Number of days to analyze (default: 30)
    
    Example: GET /api/performance/dashboard?days=7
    
    Returns:
        {
            "period_days": 7,
            "summary": {
                "total_symbols": 10,
                "total_trades": 50,
                "overall_pnl": 1500.50,
                "overall_win_rate": 62.5
            },
            "top_performers": [...],
            "worst_performers": [...],
            "flows": {...},
            "suggestions": [...]
        }
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        LOG.info(f"[API] Getting performance dashboard ({days} days)")
        
        analytics = get_performance_analytics()
        
        # Get all data
        all_perf = analytics.get_all_symbols_performance(days)
        flows = analytics.identify_trading_flows(days)
        suggestions = analytics.get_improvement_suggestions(days)
        
        # Calculate summary
        total_pnl = sum(p['total_pnl'] for p in all_perf) if all_perf else 0
        total_trades = sum(p['total_trades'] for p in all_perf) if all_perf else 0
        avg_win_rate = (
            sum(p['win_rate'] for p in all_perf) / len(all_perf)
            if all_perf else 0
        )
        
        # Get top and worst performers
        top_performers = all_perf[:5] if all_perf else []
        worst_performers = sorted(
            all_perf,
            key=lambda x: x['total_pnl']
        )[:5] if all_perf else []
        
        return jsonify({
            'period_days': days,
            'summary': {
                'total_symbols': len(all_perf),
                'total_trades': total_trades,
                'overall_pnl': round(total_pnl, 2),
                'overall_win_rate': round(avg_win_rate, 2)
            },
            'top_performers': top_performers,
            'worst_performers': worst_performers,
            'flows': flows,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        LOG.error(f"[API] Error getting dashboard: {e}")
        return jsonify({'error': str(e)}), 500
