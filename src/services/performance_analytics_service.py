"""
Trading Performance Analytics Service
Analyzes trading performance, identifies patterns, and suggests improvements
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from decimal import Decimal

from src.database.session import SessionLocal
from src.models.base import Trade, Signal, HistoricalPrice


LOG = logging.getLogger(__name__)


class PerformanceAnalytics:
    """Analyze trading performance and provide insights"""
    
    def __init__(self):
        """Initialize performance analytics"""
        self.session = SessionLocal()
        LOG.info("[ANALYTICS] Performance Analytics initialized")
    
    def get_symbol_performance(
        self,
        symbol: str,
        days: int = 30
    ) -> Dict:
        """
        Get performance metrics for a specific symbol
        
        Args:
            symbol: Trading symbol
            days: Number of days to analyze
            
        Returns:
            Performance metrics dictionary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            # Get all trades for symbol
            trades = self.session.query(Trade).filter(
                and_(
                    Trade.symbol == symbol,
                    Trade.entry_time >= cutoff_date
                )
            ).all()
            
            if not trades:
                return {
                    'symbol': symbol,
                    'period_days': days,
                    'total_trades': 0,
                    'message': 'No trades found for this symbol'
                }
            
            # Calculate metrics
            total_trades = len(trades)
            closed_trades = [t for t in trades if t.status == 'closed']
            open_trades = [t for t in trades if t.status == 'open']
            
            winning_trades = [
                t for t in closed_trades
                if t.profit_loss and t.profit_loss > 0
            ]
            losing_trades = [
                t for t in closed_trades
                if t.profit_loss and t.profit_loss < 0
            ]
            
            total_pnl = sum(
                t.profit_loss for t in closed_trades
                if t.profit_loss
            ) or Decimal('0')
            
            avg_win = (
                sum(t.profit_loss for t in winning_trades) / len(winning_trades)
                if winning_trades else Decimal('0')
            )
            
            avg_loss = (
                sum(t.profit_loss for t in losing_trades) / len(losing_trades)
                if losing_trades else Decimal('0')
            )
            
            win_rate = (
                len(winning_trades) / len(closed_trades) * 100
                if closed_trades else 0
            )
            
            # Calculate average hold time
            hold_times = []
            for trade in closed_trades:
                if trade.exit_time and trade.entry_time:
                    hold_time = (trade.exit_time - trade.entry_time).total_seconds()
                    hold_times.append(hold_time)
            
            avg_hold_time = (
                sum(hold_times) / len(hold_times)
                if hold_times else 0
            )
            
            # Risk/Reward ratio
            risk_reward_ratio = (
                abs(float(avg_win) / float(avg_loss))
                if avg_loss != 0 else 0
            )
            
            return {
                'symbol': symbol,
                'period_days': days,
                'total_trades': total_trades,
                'open_trades': len(open_trades),
                'closed_trades': len(closed_trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': round(win_rate, 2),
                'total_pnl': float(total_pnl),
                'average_win': float(avg_win),
                'average_loss': float(avg_loss),
                'risk_reward_ratio': round(risk_reward_ratio, 2),
                'avg_hold_time_seconds': round(avg_hold_time, 2),
                'avg_hold_time_hours': round(avg_hold_time / 3600, 2)
            }
            
        except Exception as e:
            LOG.error(f"[ERROR] Failed to get performance for {symbol}: {e}")
            return {'error': str(e)}
        finally:
            self.session.close()
    
    def get_all_symbols_performance(self, days: int = 30) -> List[Dict]:
        """Get performance for all traded symbols"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all symbols that have trades
            symbols = self.session.query(Trade.symbol).filter(
                Trade.entry_time >= cutoff_date
            ).distinct().all()
            
            symbols = [s[0] for s in symbols]
            
            LOG.info(f"[ANALYTICS] Analyzing {len(symbols)} symbols")
            
            results = []
            for symbol in symbols:
                perf = self.get_symbol_performance(symbol, days)
                if 'error' not in perf:
                    results.append(perf)
            
            # Sort by total PnL
            results.sort(key=lambda x: x.get('total_pnl', 0), reverse=True)
            
            return results
            
        except Exception as e:
            LOG.error(f"[ERROR] Failed to get all symbols performance: {e}")
            return []
    
    def identify_trading_flows(self, days: int = 30) -> Dict:
        """
        Identify trading patterns and flows
        
        Returns:
            Dictionary with pattern analysis
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        try:
            trades = self.session.query(Trade).filter(
                Trade.entry_time >= cutoff_date
            ).all()
            
            if not trades:
                return {'message': 'No trades found'}
            
            # Analyze by time of day
            hour_performance = {}
            for trade in trades:
                if trade.entry_time:
                    hour = trade.entry_time.hour
                    if hour not in hour_performance:
                        hour_performance[hour] = {
                            'count': 0,
                            'wins': 0,
                            'total_pnl': 0
                        }
                    
                    hour_performance[hour]['count'] += 1
                    if trade.profit_loss:
                        hour_performance[hour]['total_pnl'] += float(trade.profit_loss)
                        if trade.profit_loss > 0:
                            hour_performance[hour]['wins'] += 1
            
            # Analyze by day of week
            day_performance = {}
            for trade in trades:
                if trade.entry_time:
                    day = trade.entry_time.strftime('%A')
                    if day not in day_performance:
                        day_performance[day] = {
                            'count': 0,
                            'wins': 0,
                            'total_pnl': 0
                        }
                    
                    day_performance[day]['count'] += 1
                    if trade.profit_loss:
                        day_performance[day]['total_pnl'] += float(trade.profit_loss)
                        if trade.profit_loss > 0:
                            day_performance[day]['wins'] += 1
            
            # Analyze by action (long/short)
            action_performance = {}
            for trade in trades:
                action = trade.action
                if action not in action_performance:
                    action_performance[action] = {
                        'count': 0,
                        'wins': 0,
                        'total_pnl': 0
                    }
                
                action_performance[action]['count'] += 1
                if trade.profit_loss:
                    action_performance[action]['total_pnl'] += float(trade.profit_loss)
                    if trade.profit_loss > 0:
                        action_performance[action]['wins'] += 1
            
            # Calculate win rates
            for hour_data in hour_performance.values():
                hour_data['win_rate'] = (
                    hour_data['wins'] / hour_data['count'] * 100
                    if hour_data['count'] > 0 else 0
                )
            
            for day_data in day_performance.values():
                day_data['win_rate'] = (
                    day_data['wins'] / day_data['count'] * 100
                    if day_data['count'] > 0 else 0
                )
            
            for action_data in action_performance.values():
                action_data['win_rate'] = (
                    action_data['wins'] / action_data['count'] * 100
                    if action_data['count'] > 0 else 0
                )
            
            return {
                'period_days': days,
                'total_trades_analyzed': len(trades),
                'by_hour': hour_performance,
                'by_day': day_performance,
                'by_action': action_performance
            }
            
        except Exception as e:
            LOG.error(f"[ERROR] Failed to identify trading flows: {e}")
            return {'error': str(e)}
        finally:
            self.session.close()
    
    def get_improvement_suggestions(self, days: int = 30) -> List[Dict]:
        """
        Generate improvement suggestions based on performance data
        
        Returns:
            List of suggestions with priority and details
        """
        suggestions = []
        
        try:
            # Get overall performance
            all_perf = self.get_all_symbols_performance(days)
            flows = self.identify_trading_flows(days)
            
            if not all_perf:
                return [{
                    'priority': 'info',
                    'category': 'No Data',
                    'suggestion': 'No trading data available for analysis',
                    'details': f'No trades found in the last {days} days'
                }]
            
            # Calculate overall metrics
            total_pnl = sum(p['total_pnl'] for p in all_perf)
            avg_win_rate = sum(p['win_rate'] for p in all_perf) / len(all_perf)
            
            # Suggestion 1: Low win rate symbols
            low_win_rate_symbols = [
                p for p in all_perf
                if p['win_rate'] < 40 and p['closed_trades'] >= 5
            ]
            
            if low_win_rate_symbols:
                symbols_list = ', '.join(s['symbol'] for s in low_win_rate_symbols[:5])
                suggestions.append({
                    'priority': 'high',
                    'category': 'Win Rate',
                    'suggestion': f'Consider avoiding or adjusting strategy for symbols with low win rates',
                    'details': f'Symbols with <40% win rate: {symbols_list}',
                    'affected_symbols': [s['symbol'] for s in low_win_rate_symbols],
                    'metric': 'win_rate'
                })
            
            # Suggestion 2: Negative PnL symbols
            negative_pnl_symbols = [
                p for p in all_perf
                if p['total_pnl'] < 0
            ]
            
            if negative_pnl_symbols:
                symbols_list = ', '.join(s['symbol'] for s in negative_pnl_symbols[:5])
                total_loss = sum(s['total_pnl'] for s in negative_pnl_symbols)
                suggestions.append({
                    'priority': 'high',
                    'category': 'Profitability',
                    'suggestion': 'Disable or review strategy for consistently losing symbols',
                    'details': f'Symbols with negative PnL: {symbols_list}. Total loss: ${total_loss:.2f}',
                    'affected_symbols': [s['symbol'] for s in negative_pnl_symbols],
                    'metric': 'total_pnl'
                })
            
            # Suggestion 3: Poor risk/reward ratios
            poor_rr_symbols = [
                p for p in all_perf
                if p.get('risk_reward_ratio', 0) < 1.5 and p['closed_trades'] >= 5
            ]
            
            if poor_rr_symbols:
                symbols_list = ', '.join(s['symbol'] for s in poor_rr_symbols[:5])
                suggestions.append({
                    'priority': 'medium',
                    'category': 'Risk/Reward',
                    'suggestion': 'Improve take-profit levels for better risk/reward ratio',
                    'details': f'Symbols with R:R < 1.5: {symbols_list}. Target R:R >= 2.0',
                    'affected_symbols': [s['symbol'] for s in poor_rr_symbols],
                    'metric': 'risk_reward_ratio'
                })
            
            # Suggestion 4: Best performing symbols
            best_performers = [
                p for p in all_perf
                if p['total_pnl'] > 0 and p['win_rate'] > 60
            ][:5]
            
            if best_performers:
                symbols_list = ', '.join(s['symbol'] for s in best_performers)
                suggestions.append({
                    'priority': 'low',
                    'category': 'Opportunity',
                    'suggestion': 'Consider increasing position size for best performers',
                    'details': f'Top performers: {symbols_list}',
                    'affected_symbols': [s['symbol'] for s in best_performers],
                    'metric': 'combined'
                })
            
            # Suggestion 5: Time-based patterns
            if 'by_hour' in flows:
                worst_hours = sorted(
                    flows['by_hour'].items(),
                    key=lambda x: x[1]['total_pnl']
                )[:3]
                
                if worst_hours and worst_hours[0][1]['total_pnl'] < 0:
                    hours_list = ', '.join(f"{h}:00" for h, _ in worst_hours)
                    suggestions.append({
                        'priority': 'medium',
                        'category': 'Timing',
                        'suggestion': 'Avoid trading during unprofitable hours',
                        'details': f'Worst performing hours: {hours_list}',
                        'metric': 'timing'
                    })
            
            # Suggestion 6: Long vs Short bias
            if 'by_action' in flows:
                action_perf = flows['by_action']
                if 'long' in action_perf and 'short' in action_perf:
                    long_pnl = action_perf['long']['total_pnl']
                    short_pnl = action_perf['short']['total_pnl']
                    
                    if abs(long_pnl - short_pnl) > 100:  # Significant difference
                        better_side = 'long' if long_pnl > short_pnl else 'short'
                        worse_side = 'short' if long_pnl > short_pnl else 'long'
                        suggestions.append({
                            'priority': 'medium',
                            'category': 'Direction Bias',
                            'suggestion': f'Consider focusing more on {better_side} trades',
                            'details': f'{better_side.title()} PnL: ${max(long_pnl, short_pnl):.2f}, {worse_side.title()} PnL: ${min(long_pnl, short_pnl):.2f}',
                            'metric': 'direction'
                        })
            
            # Suggestion 7: Overall performance
            if avg_win_rate < 50:
                suggestions.append({
                    'priority': 'high',
                    'category': 'Strategy',
                    'suggestion': 'Overall win rate is below 50% - review entry criteria',
                    'details': f'Current win rate: {avg_win_rate:.2f}%. Target: >= 55%',
                    'metric': 'overall_win_rate'
                })
            
            return suggestions
            
        except Exception as e:
            LOG.error(f"[ERROR] Failed to generate suggestions: {e}")
            return [{
                'priority': 'error',
                'category': 'Error',
                'suggestion': 'Failed to analyze data',
                'details': str(e)
            }]


# Singleton instance
_performance_analytics = None


def get_performance_analytics() -> PerformanceAnalytics:
    """Get singleton instance of PerformanceAnalytics"""
    global _performance_analytics
    if _performance_analytics is None:
        _performance_analytics = PerformanceAnalytics()
    return _performance_analytics
