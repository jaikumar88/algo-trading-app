"""
Trade Monitor - Continuously monitors open trades for risk management
Runs in background to check SL, trailing stops, and emergency exits
"""
import time
import logging
from decimal import Decimal
from threading import Thread, Event
from typing import Dict
from sqlalchemy import select
from src.services.risk_management_service import get_risk_manager
from src.services.delta_exchange_service import get_delta_trader
from src.database.session import SessionLocal
from src.models.base import Trade

LOG = logging.getLogger(__name__)


class TradeMonitor:
    """Background service to monitor trades and enforce risk rules"""
    
    def __init__(self, check_interval: int = 5):
        self.check_interval = check_interval  # seconds
        self.running = False
        self.thread = None
        self.stop_event = Event()
        self.risk_manager = get_risk_manager()
        self.delta_trader = get_delta_trader()
        
        LOG.info("=" * 80)
        LOG.info("[CHART] Trade Monitor Initialized")
        LOG.info(f"Check interval: {check_interval} seconds")
        LOG.info("=" * 80)
    
    def get_current_prices(self) -> Dict[str, Decimal]:
        """Fetch current prices for all symbols with open trades"""
        LOG.debug("Fetching current prices for open trades...")
        
        if not self.delta_trader.client:
            LOG.error("[X] Delta Exchange client not initialized, cannot fetch prices")
            return {}
        
        prices = {}
        
        with SessionLocal() as db:
            # Get unique symbols from open trades
            open_trades = db.execute(
                select(Trade).where(Trade.status == 'OPEN')
            ).scalars().all()
            symbols = list(set(trade.symbol for trade in open_trades))
            
            if not symbols:
                LOG.debug("No open trades, no prices to fetch")
                return {}
            
            LOG.info(f"Fetching real-time prices for {len(symbols)} symbol(s)")
            
            for symbol in symbols:
                try:
                    LOG.debug(f"Fetching orderbook for {symbol}...")
                    # Get orderbook for current price
                    orderbook = self.delta_trader.client.get_orderbook(symbol)
                    
                    if orderbook.get('success'):
                        result = orderbook.get('result', {})
                        buy_orders = result.get('buy', [])
                        sell_orders = result.get('sell', [])
                        
                        if buy_orders and sell_orders:
                            best_bid = Decimal(
                                str(buy_orders[0].get('price', 0))
                            )
                            best_ask = Decimal(
                                str(sell_orders[0].get('price', 0))
                            )
                            
                            # Validate prices are not zero
                            if best_bid <= 0 or best_ask <= 0:
                                LOG.error(
                                    f"[X] {symbol}: Invalid price - "
                                    f"Bid=${best_bid}, Ask=${best_ask}"
                                )
                                continue
                            
                            mid_price = (best_bid + best_ask) / 2
                            
                            prices[symbol] = mid_price
                            LOG.info(
                                f"[OK] {symbol}: ${mid_price:,.2f} "
                                f"(Bid: ${best_bid:,.2f}, "
                                f"Ask: ${best_ask:,.2f})"
                            )
                        else:
                            LOG.warning(
                                f"[WARN] No orderbook data for {symbol}"
                            )
                    else:
                        error = orderbook.get('error', {})
                        error_code = error.get('code', 'unknown')
                        
                        # Log IP whitelist error prominently
                        if error_code == 'ip_not_whitelisted_for_api_key':
                            LOG.error(
                                f"[X] {symbol}: IP NOT WHITELISTED - "
                                f"Add your IP at Delta Exchange API settings"
                            )
                        else:
                            LOG.error(
                                f"[X] Failed to get orderbook for "
                                f"{symbol}: {error}"
                            )
                        
                except Exception as e:
                    LOG.exception(
                        f"[X] Exception fetching price for {symbol}: {e}"
                    )
        
        return prices
    
    def monitor_loop(self):
        """Main monitoring loop"""
        LOG.info("=" * 80)
        LOG.info("[START] TRADE MONITOR STARTED")
        LOG.info("=" * 80)
        
        iteration = 0
        
        while not self.stop_event.is_set():
            try:
                iteration += 1
                LOG.info(f"\n{'=' * 80}")
                LOG.info(f"[CHART] Monitor Check #{iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                LOG.info(f"{'=' * 80}")
                
                # Get current prices from Delta Exchange
                LOG.info("[REFRESH] Fetching real-time prices from Delta Exchange...")
                price_data = self.get_current_prices()
                
                if not price_data:
                    LOG.info("[INFO]  No open trades or no price data available")
                else:
                    LOG.info(f"[OK] Fetched {len(price_data)} price(s) successfully")
                    
                    # Check all trades against risk rules
                    LOG.info("[EVALUATING] trades against risk management rules...")
                    trades_to_close = self.risk_manager.check_all_open_trades(
                        price_data
                    )
                    
                    # Close trades that hit risk limits
                    if trades_to_close:
                        LOG.warning("=" * 80)
                        LOG.warning(
                            f"[WARN]  RISK LIMIT HIT: {len(trades_to_close)} "
                            f"trade(s) need immediate closure"
                        )
                        LOG.warning("=" * 80)
                        
                        with SessionLocal() as db:
                            for idx, trade_info in enumerate(trades_to_close, 1):
                                trade = trade_info['trade']
                                current_price = trade_info['current_price']
                                reason = trade_info['reason']
                                exit_type = trade_info['exit_type']
                                pnl_pct = trade_info['pnl_pct']
                                pnl_value = trade_info['pnl_value']
                                
                                LOG.warning(f"\n[{idx}/{len(trades_to_close)}] "
                                          f"Closing {trade.symbol} {trade.action}")
                                LOG.warning(f"Entry: ${trade.open_price:,.2f}")
                                LOG.warning(f"Exit: ${current_price:,.2f}")
                                LOG.warning(f"P&L: {pnl_pct:.2f}% "
                                          f"(${pnl_value:,.2f})")
                                LOG.warning(f"Reason: {exit_type}")
                                
                                # Close in database
                                self.risk_manager.close_trade(
                                    trade, current_price, reason, 
                                    exit_type, db
                                )
                                
                                # Place closing order on Delta Exchange
                                if self.delta_trader.enabled:
                                    opposite_side = (
                                        'sell' if trade.action.upper() == 'BUY' 
                                        else 'buy'
                                    )
                                    
                                    LOG.info(
                                        f"📤 Placing closing order: "
                                        f"{opposite_side.upper()} "
                                        f"{trade.symbol} @ ${current_price:,.2f}"
                                    )
                                    
                                    order_result = self.delta_trader.place_order(
                                        symbol=trade.symbol,
                                        side=opposite_side,
                                        price=float(current_price),
                                        size=1
                                    )
                                    
                                    if order_result.get('success'):
                                        order_id = order_result.get('order_id')
                                        LOG.info(
                                            f"[OK] Closing order placed successfully"
                                        )
                                        LOG.info(f"   Order ID: {order_id}")
                                        LOG.info(
                                            f"   Status: "
                                            f"{order_result.get('status')}"
                                        )
                                    else:
                                        LOG.error(
                                            f"[X] Failed to place closing order"
                                        )
                                        LOG.error(
                                            f"   Error: "
                                            f"{order_result.get('message')}"
                                        )
                                else:
                                    LOG.info(
                                        "[INFO]  Delta Exchange trading disabled, "
                                        "trade closed in DB only"
                                    )
                        
                        LOG.info("=" * 80)
                        LOG.info(
                            f"[OK] Completed closure of {len(trades_to_close)} "
                            f"trade(s)"
                        )
                        LOG.info("=" * 80)
                    else:
                        LOG.info("[OK] All trades within risk parameters")
                
                # Wait before next check
                LOG.info(
                    f"\n[WAIT] Next check in {self.check_interval} seconds..."
                )
                self.stop_event.wait(self.check_interval)
                
            except Exception as e:
                LOG.exception(f"Error in monitor loop: {e}")
                LOG.info(f"Continuing after error...")
                self.stop_event.wait(self.check_interval)
        
        LOG.info("=" * 80)
        LOG.info("[STOPPED] TRADE MONITOR STOPPED")
        LOG.info("=" * 80)
    
    def start(self):
        """Start the monitoring thread"""
        if self.running:
            LOG.warning("Monitor already running")
            return
        
        LOG.info("Starting trade monitor...")
        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self.monitor_loop, daemon=True, name="TradeMonitor")
        self.thread.start()
        LOG.info("[OK] Trade monitor started in background thread")
    
    def stop(self):
        """Stop the monitoring thread"""
        if not self.running:
            LOG.warning("Monitor not running")
            return
        
        LOG.info("Stopping trade monitor...")
        self.running = False
        self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=10)
        
        LOG.info("[OK] Trade monitor stopped")
    
    def is_running(self) -> bool:
        """Check if monitor is running"""
        return self.running and self.thread and self.thread.is_alive()


# Global instance
_trade_monitor = None

def get_trade_monitor(check_interval: int = 5) -> TradeMonitor:
    """Get or create TradeMonitor instance"""
    global _trade_monitor
    if _trade_monitor is None:
        LOG.info(f"Creating new TradeMonitor instance (check_interval={check_interval}s)...")
        _trade_monitor = TradeMonitor(check_interval)
    return _trade_monitor
