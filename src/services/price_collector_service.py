"""
Price Data Collector Service
Collects real-time price data every second for enabled symbols
Stores in historical_prices table for charting and analysis
"""
import os
import sys
import time
import logging
import threading
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.exc import IntegrityError

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../tools'))

from src.database.session import SessionLocal
from src.models.base import HistoricalPrice, AllowedInstrument
from src.services.delta_exchange_service import get_delta_trader

LOG = logging.getLogger(__name__)


class PriceCollector:
    """Collects and stores real-time price data for enabled symbols"""
    
    def __init__(self, collection_interval: int = 1):
        """
        Initialize price collector
        
        Args:
            collection_interval: Seconds between collections (default: 1)
        """
        LOG.info(
            f"Creating new PriceCollector instance "
            f"(interval={collection_interval}s)..."
        )
        self.collection_interval = collection_interval
        self.running = False
        self.thread = None
        self.delta_trader = None
        self.enabled_symbols = []
        
        LOG.info("=" * 80)
        LOG.info("[PRICE COLLECTOR] Initialized")
        LOG.info(f"Collection interval: {collection_interval} second(s)")
        LOG.info("=" * 80)
    
    def get_enabled_symbols(self) -> List[str]:
        """Get list of enabled symbols from database"""
        session = SessionLocal()
        try:
            instruments = session.query(AllowedInstrument).filter(
                AllowedInstrument.enabled.is_(True)
            ).all()
            
            symbols = [inst.symbol for inst in instruments]
            symbols_str = ', '.join(symbols)
            LOG.info(f"Found {len(symbols)} enabled symbols: {symbols_str}")
            return symbols
        except Exception as e:
            LOG.error(f"Error getting enabled symbols: {e}")
            return []
        finally:
            session.close()
    
    def collect_price_data(self, symbol: str) -> Optional[Dict]:
        """
        Collect current price data for a symbol
        
        Returns:
            Dict with bid, ask, mid, spread data or None
        """
        try:
            if not self.delta_trader:
                self.delta_trader = get_delta_trader()
            
            # Get orderbook
            orderbook = self.delta_trader.client.get_orderbook(symbol)
            
            if not orderbook.get('success'):
                error = orderbook.get('error', {})
                error_code = error.get('code', 'unknown')
                
                # Log specific errors
                if error_code == 'ip_not_whitelisted_for_api_key':
                    LOG.error(
                        f"[{symbol}] IP NOT WHITELISTED - "
                        f"Add your IP to Delta Exchange API key settings"
                    )
                else:
                    LOG.warning(
                        f"[{symbol}] Failed to get orderbook: {error}"
                    )
                return None
            
            result = orderbook.get('result', {})
            buy_orders = result.get('buy', [])
            sell_orders = result.get('sell', [])
            
            if not buy_orders or not sell_orders:
                LOG.warning(f"[{symbol}] No orderbook data available")
                return None
            
            # Extract price data
            bid_price = Decimal(str(buy_orders[0].get('price', 0)))
            ask_price = Decimal(str(sell_orders[0].get('price', 0)))
            
            # Validate prices are not zero
            if bid_price <= 0 or ask_price <= 0:
                LOG.error(
                    f"[{symbol}] Invalid price data: "
                    f"bid=${bid_price}, ask=${ask_price}"
                )
                return None
            
            mid_price = (bid_price + ask_price) / 2
            spread = ask_price - bid_price
            if mid_price > 0:
                spread_pct = spread / mid_price * 100
            else:
                spread_pct = Decimal(0)
            
            # Extract volumes
            volume_bid = Decimal(str(buy_orders[0].get('size', 0)))
            volume_ask = Decimal(str(sell_orders[0].get('size', 0)))
            
            return {
                'symbol': symbol,
                'timestamp': datetime.utcnow(),
                'bid_price': bid_price,
                'ask_price': ask_price,
                'mid_price': mid_price,
                'spread': spread,
                'spread_pct': spread_pct,
                'volume_bid': volume_bid,
                'volume_ask': volume_ask
            }
            
        except Exception as e:
            LOG.error(f"[{symbol}] Error collecting price data: {e}")
            return None
    
    def save_price_data(self, price_data: Dict) -> bool:
        """
        Save price data to database
        
        Returns:
            True if saved successfully, False otherwise
        """
        session = SessionLocal()
        try:
            price_record = HistoricalPrice(
                symbol=price_data['symbol'],
                timestamp=price_data['timestamp'],
                bid_price=price_data['bid_price'],
                ask_price=price_data['ask_price'],
                mid_price=price_data['mid_price'],
                spread=price_data['spread'],
                spread_pct=price_data['spread_pct'],
                volume_bid=price_data['volume_bid'],
                volume_ask=price_data['volume_ask']
            )
            
            session.add(price_record)
            session.commit()
            return True
            
        except IntegrityError:
            session.rollback()
            LOG.debug(f"[{price_data['symbol']}] Duplicate price record, skipping")
            return False
        except Exception as e:
            session.rollback()
            LOG.error(f"[{price_data['symbol']}] Error saving price data: {e}")
            return False
        finally:
            session.close()
    
    def collection_loop(self):
        """Main collection loop - runs in background thread"""
        LOG.info("[PRICE COLLECTOR] Started")
        iteration = 0
        
        while self.running:
            iteration += 1
            try:
                LOG.info("\n" + "=" * 80)
                LOG.info(f"[COLLECTION] Cycle #{iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
                LOG.info("=" * 80)
                
                # Refresh enabled symbols every 10 cycles
                if iteration % 10 == 1:
                    self.enabled_symbols = self.get_enabled_symbols()
                
                if not self.enabled_symbols:
                    LOG.warning("[COLLECTION] No enabled symbols found")
                    time.sleep(self.collection_interval)
                    continue
                
                # Collect price data for all enabled symbols
                collected_count = 0
                saved_count = 0
                
                for symbol in self.enabled_symbols:
                    price_data = self.collect_price_data(symbol)
                    
                    if price_data:
                        collected_count += 1
                        if self.save_price_data(price_data):
                            saved_count += 1
                            LOG.info(
                                f"[{symbol}] Mid: ${price_data['mid_price']:,.2f} | "
                                f"Bid: ${price_data['bid_price']:,.2f} | "
                                f"Ask: ${price_data['ask_price']:,.2f} | "
                                f"Spread: {price_data['spread_pct']:.4f}%"
                            )
                
                LOG.info(f"\n[SUMMARY] Collected: {collected_count}/{len(self.enabled_symbols)} | Saved: {saved_count}")
                LOG.info(f"[NEXT] Collection in {self.collection_interval} second(s)...\n")
                
            except Exception as e:
                LOG.exception(f"[ERROR] Collection loop error: {e}")
            
            # Sleep until next collection
            time.sleep(self.collection_interval)
        
        LOG.info("[PRICE COLLECTOR] Stopped")
    
    def start(self):
        """Start price collection in background thread"""
        if self.running:
            LOG.warning("[PRICE COLLECTOR] Already running")
            return
        
        LOG.info("Starting price collector...")
        self.running = True
        self.thread = threading.Thread(target=self.collection_loop, daemon=True)
        self.thread.start()
        
        LOG.info("=" * 80)
        LOG.info("[OK] Price collector started in background thread")
        LOG.info("=" * 80)
    
    def stop(self):
        """Stop price collection"""
        if not self.running:
            LOG.warning("[PRICE COLLECTOR] Not running")
            return
        
        LOG.info("Stopping price collector...")
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=5)
        
        LOG.info("[OK] Price collector stopped")


# Global instance
_price_collector = None

def get_price_collector(collection_interval: int = 1) -> PriceCollector:
    """Get or create price collector instance"""
    global _price_collector
    if _price_collector is None:
        LOG.info("Creating new PriceCollector instance...")
        _price_collector = PriceCollector(collection_interval=collection_interval)
        LOG.info("PriceCollector instance created and cached")
    else:
        LOG.debug("Returning cached PriceCollector instance")
    return _price_collector
