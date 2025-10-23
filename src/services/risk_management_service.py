"""
Risk Management Service
Handles stop loss, take profit, trailing stops, and emergency exits

IMPORTANT: This service handles automatic SL/TP execution based on price movements.
However, when OPPOSITE SIGNALS are received through the trading service, trades are 
IMMEDIATELY closed at current market price, bypassing SL/TP levels entirely.

Risk Management Priority:
1. IMMEDIATE CLOSE on opposite signals (highest priority)
2. Stop Loss/Take Profit monitoring (this service)
3. Trailing stops and emergency exits
"""
import logging
from decimal import Decimal
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import select
from src.database.session import SessionLocal
from src.models.base import Trade, SystemSettings

LOG = logging.getLogger(__name__)


class RiskManager:
    """Manages risk for open trades with SL, TP and trailing stops"""
    
    def __init__(self):
        # Default values (overridden by database settings)
        self.stop_loss_pct = Decimal('0.01')  # 1% stop loss
        self.take_profit_pct = Decimal('0.02')  # 2% take profit
        self.trailing_stop_enabled = False
        self.trailing_stop_type = 'percent'  # 'percent' or 'amount'
        self.trailing_stop_percent = Decimal('0.005')  # 0.5%
        self.trailing_stop_amount = Decimal('50')  # $50
        self.emergency_spike_pct = Decimal('0.10')  # 10% spike emergency exit
        
        # Load settings from database
        self._load_settings()
        
        LOG.info("=" * 80)
        LOG.info("Risk Manager Initialized")
        LOG.info(f"Stop Loss: {self.stop_loss_pct * 100}%")
        LOG.info(f"Take Profit: {self.take_profit_pct * 100}%")
        LOG.info(f"Trailing Stop Enabled: {self.trailing_stop_enabled}")
        if self.trailing_stop_enabled:
            if self.trailing_stop_type == 'percent':
                LOG.info(f"Trailing Stop: {self.trailing_stop_percent * 100}%")
            else:
                LOG.info(f"Trailing Stop: ${self.trailing_stop_amount}")
        LOG.info(f"Emergency Spike: {self.emergency_spike_pct * 100}%")
        LOG.info("=" * 80)
    
    def _load_settings(self):
        """Load risk settings from database"""
        try:
            with SessionLocal() as db:
                settings = db.execute(
                    select(SystemSettings).where(
                        SystemSettings.key.like('risk_%')
                    )
                ).scalars().all()
                
                for setting in settings:
                    key = setting.key.replace('risk_', '')
                    value = setting.value
                    
                    if key == 'stop_loss_percent':
                        self.stop_loss_pct = Decimal(value) / 100
                    elif key == 'take_profit_percent':
                        self.take_profit_pct = Decimal(value) / 100
                    elif key == 'trailing_stop_enabled':
                        self.trailing_stop_enabled = value.lower() == 'true'
                    elif key == 'trailing_stop_type':
                        self.trailing_stop_type = value
                    elif key == 'trailing_stop_percent':
                        self.trailing_stop_percent = Decimal(value) / 100
                    elif key == 'trailing_stop_amount':
                        self.trailing_stop_amount = Decimal(value)
                        
        except Exception as e:
            LOG.warning(f"Could not load settings from database: {e}")
            LOG.warning("Using default risk settings")
    
    def should_close_trade(self, trade: Trade, current_price: Decimal) -> tuple[bool, str, str]:
        """Check if trade should be closed based on risk rules
        
        Returns:
            (should_close, reason, exit_type)
            exit_type: 'stop_loss', 'take_profit', 'trailing_stop', 'emergency_spike'
        """
        entry_price = trade.open_price
        side = trade.action
        
        # Calculate current P&L
        if side.upper() == 'BUY':
            pnl_value = current_price - entry_price
            pnl_pct = (current_price - entry_price) / entry_price
        else:  # SELL
            pnl_value = entry_price - current_price
            pnl_pct = (entry_price - current_price) / entry_price
        
        LOG.debug(f"Checking trade {trade.id}: {side} {trade.symbol} @ ${entry_price}, current=${current_price}, P&L={pnl_pct*100:.2f}%")
        
        # 1. Check Stop Loss (from trade record or default)
        if trade.stop_loss:
            sl_price = trade.stop_loss
            if side.upper() == 'BUY':
                # BUY: SL below entry
                if current_price <= sl_price:
                    reason = f"Stop loss hit: ${current_price:,.2f} <= ${sl_price:,.2f} (loss: {pnl_pct*100:.2f}%)"
                    LOG.warning(f"[STOP LOSS] {trade.symbol} {side} - ${current_price:,.2f} <= ${sl_price:,.2f}")
                    return True, reason, 'stop_loss'
            else:  # SELL
                # SELL: SL above entry
                if current_price >= sl_price:
                    reason = f"Stop loss hit: ${current_price:,.2f} >= ${sl_price:,.2f} (loss: {pnl_pct*100:.2f}%)"
                    LOG.warning(f"[STOP LOSS] {trade.symbol} {side} - ${current_price:,.2f} >= ${sl_price:,.2f}")
                    return True, reason, 'stop_loss'
        else:
            # Fallback to percentage-based SL if no specific SL set
            if pnl_pct <= -self.stop_loss_pct:
                reason = f"Stop loss hit: {pnl_pct*100:.2f}% loss (SL: -{self.stop_loss_pct*100}%)"
                LOG.warning(f"[STOP LOSS] {trade.symbol} {side} - {pnl_pct*100:.2f}% loss")
                return True, reason, 'stop_loss'
        
        # 2. Check Take Profit (from trade record or default)
        if trade.take_profit:
            tp_price = trade.take_profit
            if side.upper() == 'BUY':
                # BUY: TP above entry
                if current_price >= tp_price:
                    reason = f"Take profit hit: ${current_price:,.2f} >= ${tp_price:,.2f} (profit: {pnl_pct*100:.2f}%)"
                    LOG.info(f"[TAKE PROFIT] {trade.symbol} {side} - ${current_price:,.2f} >= ${tp_price:,.2f}")
                    return True, reason, 'take_profit'
            else:  # SELL
                # SELL: TP below entry
                if current_price <= tp_price:
                    reason = f"Take profit hit: ${current_price:,.2f} <= ${tp_price:,.2f} (profit: {pnl_pct*100:.2f}%)"
                    LOG.info(f"[TAKE PROFIT] {trade.symbol} {side} - ${current_price:,.2f} <= ${tp_price:,.2f}")
                    return True, reason, 'take_profit'
        else:
            # Fallback to percentage-based TP if no specific TP set
            if pnl_pct >= self.take_profit_pct:
                reason = f"Take profit hit: {pnl_pct*100:.2f}% profit (TP: {self.take_profit_pct*100}%)"
                LOG.info(f"[TAKE PROFIT] {trade.symbol} {side} - {pnl_pct*100:.2f}% profit")
                return True, reason, 'take_profit'
        
        # 3. Trailing Stop Loss (if enabled and in profit)
        if self.trailing_stop_enabled and pnl_value > 0:
            # Track highest profit achieved
            highest_price_key = f'highest_price_{trade.id}'
            if not hasattr(self, '_highest_prices'):
                self._highest_prices = {}
            
            if side.upper() == 'BUY':
                # For BUY, track highest price reached
                highest = self._highest_prices.get(highest_price_key, current_price)
                if current_price > highest:
                    highest = current_price
                    self._highest_prices[highest_price_key] = highest
                    LOG.info(f"[NEW HIGH] for trade {trade.id}: ${highest:,.2f}")
                
                # Check if price dropped from highest
                if self.trailing_stop_type == 'percent':
                    trailing_sl = highest * (Decimal('1') - self.trailing_stop_percent)
                    if current_price <= trailing_sl:
                        reason = f"Trailing stop hit: ${current_price:,.2f} <= ${trailing_sl:,.2f} (dropped {self.trailing_stop_percent*100}% from high ${highest:,.2f})"
                        LOG.warning(f"[TRAILING STOP] {trade.symbol} - dropped {self.trailing_stop_percent*100}% from ${highest:,.2f}")
                        return True, reason, 'trailing_stop'
                else:  # amount
                    trailing_sl = highest - self.trailing_stop_amount
                    if current_price <= trailing_sl:
                        reason = f"Trailing stop hit: ${current_price:,.2f} <= ${trailing_sl:,.2f} (dropped ${self.trailing_stop_amount} from high ${highest:,.2f})"
                        LOG.warning(f"[TRAILING STOP] {trade.symbol} - dropped ${self.trailing_stop_amount} from ${highest:,.2f}")
                        return True, reason, 'trailing_stop'
            
            else:  # SELL
                # For SELL, track lowest price reached
                lowest = self._highest_prices.get(highest_price_key, current_price)
                if current_price < lowest:
                    lowest = current_price
                    self._highest_prices[highest_price_key] = lowest
                    LOG.info(f"[NEW LOW] Trade {trade.id}: ${lowest:,.2f}")
                
                # Check if price rose from lowest
                if self.trailing_stop_type == 'percent':
                    trailing_sl = lowest * (Decimal('1') + self.trailing_stop_percent)
                    if current_price >= trailing_sl:
                        reason = f"Trailing stop hit: ${current_price:,.2f} >= ${trailing_sl:,.2f} (rose {self.trailing_stop_percent*100}% from low ${lowest:,.2f})"
                        LOG.warning(f"[TRAILING STOP] {trade.symbol} - rose {self.trailing_stop_percent*100}% from ${lowest:,.2f}")
                        return True, reason, 'trailing_stop'
                else:  # amount
                    trailing_sl = lowest + self.trailing_stop_amount
                    if current_price >= trailing_sl:
                        reason = f"Trailing stop hit: ${current_price:,.2f} >= ${trailing_sl:,.2f} (rose ${self.trailing_stop_amount} from low ${lowest:,.2f})"
                        LOG.warning(f"[TRAILING STOP] {trade.symbol} - rose ${self.trailing_stop_amount} from ${lowest:,.2f}")
                        return True, reason, 'trailing_stop'
        
        # 4. Emergency spike check (10% move)
        abs_pnl_pct = abs(pnl_pct)
        if abs_pnl_pct >= self.emergency_spike_pct:
            reason = f"Emergency exit: {abs_pnl_pct*100:.2f}% spike detected (threshold: {self.emergency_spike_pct*100}%)"
            LOG.warning(f"[EMERGENCY SPIKE] {trade.symbol} {side} - {abs_pnl_pct*100:.2f}% move!")
            return True, reason, 'emergency_spike'
        
        return False, "", ""
    
    def check_all_open_trades(self, price_data: Dict[str, Decimal]) -> List[Dict]:
        """Check all open trades against current prices
        
        Args:
            price_data: Dict mapping symbol -> current_price
            
        Returns:
            List of trades to close with reasons
        """
        LOG.info("=" * 80)
        LOG.info("[RISK CHECK] CHECKING ALL OPEN TRADES FOR RISK MANAGEMENT")
        LOG.info("=" * 80)
        
        trades_to_close = []
        
        with SessionLocal() as db:
            # Get all open trades
            open_trades = db.execute(
                select(Trade).where(Trade.status == 'OPEN')
            ).scalars().all()
            
            if not open_trades:
                LOG.info("No open trades to check")
                return []
            
            LOG.info(f"Found {len(open_trades)} open trade(s) to check")
            
            for trade in open_trades:
                symbol = trade.symbol
                current_price = price_data.get(symbol)
                
                if not current_price:
                    LOG.warning(f"[WARN] No price data for {symbol}, skipping")
                    continue
                
                if current_price <= 0:
                    LOG.warning(f"[WARN] Invalid price ${current_price} for {symbol}, skipping")
                    continue
                
                LOG.info(f"\nChecking: {symbol} {trade.action} @ ${trade.open_price}")
                LOG.info(f"Current price: ${current_price}")
                if trade.stop_loss:
                    LOG.info(f"Stop Loss: ${trade.stop_loss}")
                if trade.take_profit:
                    LOG.info(f"Take Profit: ${trade.take_profit}")
                
                should_close, reason, exit_type = self.should_close_trade(trade, current_price)
                
                if should_close:
                    # Calculate P&L
                    if trade.action.upper() == 'BUY':
                        pnl_value = (current_price - trade.open_price) * trade.quantity
                        pnl_pct = (current_price - trade.open_price) / trade.open_price
                    else:
                        pnl_value = (trade.open_price - current_price) * trade.quantity
                        pnl_pct = (trade.open_price - current_price) / trade.open_price
                    
                    LOG.warning("=" * 80)
                    LOG.warning(f"[WARN] CLOSING TRADE: {symbol} {trade.action}")
                    LOG.warning(f"Entry: ${trade.open_price:,.2f}, Current: ${current_price:,.2f}")
                    LOG.warning(f"P&L: {pnl_pct*100:.2f}% (${pnl_value:,.2f})")
                    LOG.warning(f"Reason: {reason}")
                    LOG.warning(f"Exit Type: {exit_type}")
                    LOG.warning("=" * 80)
                    
                    trades_to_close.append({
                        'trade': trade,
                        'current_price': current_price,
                        'reason': reason,
                        'exit_type': exit_type,
                        'pnl_pct': float(pnl_pct * 100),
                        'pnl_value': float(pnl_value)
                    })
                else:
                    # Calculate current P&L for logging
                    if trade.action.upper() == 'BUY':
                        pnl_pct = (current_price - trade.open_price) / trade.open_price
                    else:
                        pnl_pct = (trade.open_price - current_price) / trade.open_price
                    LOG.info(f"[OK] Trade OK: {symbol} {trade.action} - P&L: {pnl_pct*100:.2f}%")
        
        if trades_to_close:
            LOG.info(f"\n[SUMMARY] {len(trades_to_close)} trade(s) need to be closed")
        else:
            LOG.info("\n[OK] All trades within risk parameters")
        
        return trades_to_close
    
    def close_trade(self, trade: Trade, exit_price: Decimal, reason: str, exit_type: str, db):
        """Close a trade and update database"""
        LOG.info(f"Closing trade {trade.id}: {trade.symbol} {trade.action}")
        
        trade.status = 'CLOSED'
        trade.close_price = exit_price
        trade.close_time = datetime.utcnow()
        
        # Mark if stop loss was triggered
        if exit_type == 'stop_loss':
            trade.stop_loss_triggered = True
        
        # Calculate final P&L
        if trade.action.upper() == 'BUY':
            trade.profit_loss = (exit_price - trade.open_price) * trade.quantity
        else:
            trade.profit_loss = (trade.open_price - exit_price) * trade.quantity
        
        db.commit()
        
        LOG.info(f"[OK] Trade closed: {trade.symbol} {trade.action}")
        LOG.info(f"   Entry: ${trade.open_price}, Exit: ${exit_price}")
        LOG.info(f"   P&L: ${trade.profit_loss}")
        LOG.info(f"   Reason: {reason}")


# Global instance
_risk_manager = None

def get_risk_manager() -> RiskManager:
    """Get or create RiskManager instance"""
    global _risk_manager
    if _risk_manager is None:
        LOG.info("Creating new RiskManager instance...")
        _risk_manager = RiskManager()
    else:
        LOG.debug("Returning cached RiskManager instance")
    return _risk_manager
