"""
Delta Exchange Trading Integration
Handles real order placement with price verification
"""
import os
import sys
import logging
from decimal import Decimal
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../tools'))

from TradingClient import DeltaExchangeClient

LOG = logging.getLogger(__name__)

# Delta Exchange API endpoints
DELTA_PRODUCTS_API = "https://api.india.delta.exchange/v2/products"


class DeltaExchangeTrader:
    """Delta Exchange live trading integration"""
    
    def __init__(self):
        LOG.info("Initializing DeltaExchangeTrader...")
        self.api_key = os.getenv('DELTA_API_KEY')
        self.api_secret = os.getenv('DELTA_API_SECRET')
        self.enabled = os.getenv('DELTA_TRADING_ENABLED', 'false').lower() == 'true'
        
        LOG.info(f"Trading enabled: {self.enabled}")
        LOG.info(f"API key configured: {bool(self.api_key)}")
        LOG.info(f"API secret configured: {bool(self.api_secret)}")
        
        if not self.api_key or not self.api_secret:
            LOG.warning("[WARN] Delta Exchange credentials not configured - orders will not be placed")
            self.client = None
        else:
            LOG.info("[OK] Creating Delta Exchange client with provided credentials")
            self.client = DeltaExchangeClient(self.api_key, self.api_secret)
            LOG.info("[OK] Delta Exchange client initialized successfully")
    
    def verify_price(self, symbol: str, expected_price: float, tolerance: float = 0.02) -> Tuple[bool, float, str]:
        """Verify that the signal price matches current market price
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSD')
            expected_price: Expected price from signal
            tolerance: Acceptable price difference as percentage (default 2%)
            
        Returns:
            (is_valid, current_price, message)
        """
        LOG.info(f"[VERIFY] Verifying price for {symbol}: expected=${expected_price:.2f}, tolerance={tolerance*100}%")
        
        if not self.client:
            LOG.error("[X] Cannot verify price: Delta Exchange client not initialized")
            return False, 0.0, "Delta Exchange client not initialized"
        
        try:
            LOG.debug(f"Fetching orderbook for {symbol}...")
            # Get current orderbook
            orderbook = self.client.get_orderbook(symbol)
            
            if not orderbook.get('success'):
                error = orderbook.get('error', {})
                LOG.error(f"[X] Failed to get orderbook for {symbol}: {error}")
                return False, 0.0, f"Failed to get orderbook: {error}"
            
            result = orderbook.get('result', {})
            buy_orders = result.get('buy', [])
            sell_orders = result.get('sell', [])
            
            LOG.debug(f"Orderbook retrieved: {len(buy_orders)} buy orders, {len(sell_orders)} sell orders")
            
            if not buy_orders or not sell_orders:
                LOG.error(f"[X] No market data available for {symbol}")
                return False, 0.0, "No market data available"
            
            # Get best bid and ask
            best_bid = float(buy_orders[0].get('price', 0))
            best_ask = float(sell_orders[0].get('price', 0))
            mid_price = (best_bid + best_ask) / 2
            
            print(f"[MARKET] {symbol}: Bid=${best_bid:.2f}, Ask=${best_ask:.2f}, Mid=${mid_price:.2f}")
            LOG.info(f"[MARKET] {symbol}: Bid=${best_bid:.2f}, Ask=${best_ask:.2f}, Mid=${mid_price:.2f}")
            
            # Calculate price difference
            price_diff_pct = abs(mid_price - expected_price) / mid_price * 100
            
            if price_diff_pct > (tolerance * 100):
                print(f"[FAIL] Price verification FAILED for {symbol}: expected ${expected_price:.2f}, current ${mid_price:.2f} (diff: {price_diff_pct:.2f}% > {tolerance*100}%)")
                LOG.warning(f"[FAIL] Price verification FAILED for {symbol}: expected ${expected_price:.2f}, current ${mid_price:.2f} (diff: {price_diff_pct:.2f}% > {tolerance*100}%)")
                return False, mid_price, f"Price mismatch: expected {expected_price}, current {mid_price:.2f} (diff: {price_diff_pct:.2f}%)"
            
            print(f"[OK] Price verified for {symbol}: signal=${expected_price:.2f}, market=${mid_price:.2f}, diff={price_diff_pct:.2f}%")
            LOG.info(f"[OK] Price verified for {symbol}: signal=${expected_price:.2f}, market=${mid_price:.2f}, diff={price_diff_pct:.2f}%")
            return True, mid_price, "Price verified"
            
        except Exception as e:
            LOG.exception(f"[X] Exception during price verification for {symbol}: {e}")
            return False, 0.0, f"Price verification error: {str(e)}"
    
    def get_product_id(self, symbol: str) -> Optional[int]:
        """Get product ID for a symbol"""
        LOG.debug(f"Looking up product ID for symbol: {symbol}")
        
        if not self.client:
            LOG.error("[X] Cannot get product ID: Delta Exchange client not initialized")
            return None
        
        try:
            # Common symbol mapping (Product IDs from Delta Exchange API)
            symbol_map = {
                'BTCUSD': 27,     # Bitcoin perpetual
                'ETHUSD': 3136,   # Ethereum perpetual (CORRECT ID)
                'BTCUSDT': 27,    # Map to BTCUSD
                'ETHUSDT': 3136,  # Map to ETHUSD
            }
            
            # Try direct mapping first
            if symbol.upper() in symbol_map:
                product_id = symbol_map[symbol.upper()]
                LOG.info(f"[OK] Found product ID for {symbol} via mapping: {product_id}")
                return product_id
            
            LOG.debug(f"Symbol {symbol} not in mapping, searching products API...")
            
            # Otherwise search products
            products = self.client.get_products()
            if products.get('success'):
                all_products = products.get('result', [])
                LOG.debug(f"Searching {len(all_products)} products for {symbol}...")
                
                for product in all_products:
                    if product.get('symbol', '').upper() == symbol.upper():
                        if 'perpetual' in product.get('contract_type', '').lower():
                            product_id = product.get('id')
                            LOG.info(f"[OK] Found product ID for {symbol} via API search: {product_id}")
                            return product_id
            
            LOG.warning(f"[WARN] Product ID not found for symbol: {symbol}")
            return None
            
        except Exception as e:
            LOG.exception(f"[X] Error getting product ID for {symbol}: {e}")
            return None
    
    def place_order(self, symbol: str, side: str, price: float, size: int = 1) -> Dict:
        """Place a limit order on Delta Exchange
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSD')
            side: 'buy' or 'sell'
            price: Limit price
            size: Order size (default 1)
            
        Returns:
            Order result dict with success status and details
        """
        LOG.info(f"📤 Place order request: {side.upper()} {size} {symbol} @ ${price:.2f}")
        
        if not self.enabled:
            LOG.warning("🔧 Trading is DISABLED - order will not be placed (dry run mode)")
            return {
                'success': False,
                'message': 'Delta Exchange trading is disabled (set DELTA_TRADING_ENABLED=true to enable)',
                'dry_run': True
            }
        
        if not self.client:
            LOG.error("[X] Cannot place order: Delta Exchange client not initialized")
            return {
                'success': False,
                'message': 'Delta Exchange client not initialized',
                'error': 'Missing credentials'
            }
        
        try:
            # Get product ID
            LOG.info(f"Step 1/3: Getting product ID for {symbol}...")
            product_id = self.get_product_id(symbol)
            if not product_id:
                LOG.error(f"[X] Product ID not found for symbol: {symbol}")
                return {
                    'success': False,
                    'message': f'Product ID not found for symbol: {symbol}',
                    'error': 'Invalid symbol'
                }
            
            LOG.info(f"[OK] Product ID found: {product_id}")
            
            # Verify price before placing order
            LOG.info(f"Step 2/3: Verifying price for {symbol}...")
            is_valid, current_price, msg = self.verify_price(symbol, price)
            if not is_valid:
                LOG.warning(f"[WARN] Price verification failed for {symbol}: {msg}")
                return {
                    'success': False,
                    'message': f'Price verification failed: {msg}',
                    'error': 'Price mismatch',
                    'expected_price': price,
                    'current_price': current_price
                }
            
            # Place the order
            LOG.info(f"Step 3/3: Placing order on Delta Exchange...")
            LOG.info(f"📋 Order details: side={side.lower()}, size={size}, price=${price:.2f}, product_id={product_id}")
            
            order_result = self.client.place_order(
                product_id=product_id,
                side=side.lower(),
                size=size,
                limit_price=str(price)
            )
            
            if order_result.get('success'):
                result_data = order_result.get('result', {})
                order_id = result_data.get('id')
                order_status = result_data.get('state')
                LOG.info(f"[OK] ORDER PLACED SUCCESSFULLY!")
                LOG.info(f"   Order ID: {order_id}")
                LOG.info(f"   Status: {order_status}")
                LOG.info(f"   Side: {side.upper()}")
                LOG.info(f"   Symbol: {symbol}")
                LOG.info(f"   Size: {size}")
                LOG.info(f"   Price: ${price:.2f}")
                LOG.info(f"   Verified Market Price: ${current_price:.2f}")
                return {
                    'success': True,
                    'message': f'Order placed: {side} {size} {symbol} @ {price}',
                    'order_id': order_id,
                    'status': order_status,
                    'product_id': product_id,
                    'verified_price': current_price
                }
            else:
                error = order_result.get('error', {})
                LOG.error(f"[X] ORDER PLACEMENT FAILED!")
                LOG.error(f"   Symbol: {symbol}")
                LOG.error(f"   Side: {side.upper()}")
                LOG.error(f"   Price: ${price:.2f}")
                LOG.error(f"   Error: {error}")
                return {
                    'success': False,
                    'message': f'Order placement failed: {error}',
                    'error': error
                }
                
        except Exception as e:
            LOG.exception(f"[X] EXCEPTION during order placement for {symbol}!")
            LOG.error(f"   Exception type: {type(e).__name__}")
            LOG.error(f"   Exception message: {str(e)}")
            return {
                'success': False,
                'message': f'Order placement error: {str(e)}',
                'error': str(e)
            }
    
    def get_status(self) -> Dict:
        """Get trading system status"""
        status = {
            'enabled': self.enabled,
            'client_ready': self.client is not None,
            'api_key_configured': bool(self.api_key),
            'api_secret_configured': bool(self.api_secret)
        }
        LOG.debug(f"Trading system status: {status}")
        return status
    
    def fetch_all_products(self) -> List[Dict]:
        """
        Fetch all products from Delta Exchange API with pagination
        
        Returns:
            List of product dictionaries
        """
        all_products = []
        page_size = 100
        after_cursor = None
        page = 1
        
        LOG.info("[FETCH] Starting to fetch products from Delta Exchange...")
        
        try:
            while True:
                # Build URL with pagination
                url = f"{DELTA_PRODUCTS_API}?page_size={page_size}"
                if after_cursor:
                    url += f"&after={after_cursor}"
                
                LOG.info(f"[PAGE {page}] Fetching from: {url}")
                
                # Make API request
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get('success'):
                    error_msg = data.get('error', 'Unknown error')
                    LOG.error(f"[ERROR] API returned error: {error_msg}")
                    break
                
                result = data.get('result', [])
                meta = data.get('meta', {})
                
                if not result:
                    LOG.info("[DONE] No more products to fetch")
                    break
                
                # Add products to list
                all_products.extend(result)
                LOG.info(f"[PAGE {page}] Fetched {len(result)} products")
                
                # Check if there are more pages
                after_cursor = meta.get('after')
                if not after_cursor:
                    LOG.info("[DONE] Reached last page")
                    break
                
                page += 1
            
            LOG.info(f"[SUMMARY] Total products fetched: {len(all_products)}")
            return all_products
            
        except requests.exceptions.RequestException as e:
            LOG.error(f"[ERROR] Failed to fetch products: {e}")
            return []
        except Exception as e:
            LOG.error(f"[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def sync_symbols_to_db(
        self,
        auto_enable: bool = False,
        product_types: Optional[List[str]] = None
    ) -> Dict:
        """
        Sync symbols from Delta Exchange to database
        
        Args:
            auto_enable: If True, automatically enable perpetual futures
            product_types: Filter by product types
                          (e.g., ['future', 'perpetual_futures'])
        
        Returns:
            Dictionary with sync statistics
        """
        from src.database.session import SessionLocal
        from src.models.base import AllowedInstrument
        
        LOG.info("")
        LOG.info("=" * 80)
        LOG.info("[SYNC] Starting symbol synchronization from Delta Exchange")
        LOG.info("=" * 80)
        
        # Fetch all products
        products = self.fetch_all_products()
        
        if not products:
            LOG.warning("[SYNC] No products fetched, aborting sync")
            return {
                'success': False,
                'added': 0,
                'updated': 0,
                'total': 0
            }
        
        # Filter by product types if specified
        if product_types:
            original_count = len(products)
            products = [
                p for p in products
                if p.get('contract_type') in product_types
            ]
            LOG.info(
                f"[FILTER] Filtered {original_count} -> {len(products)} "
                f"products by types: {product_types}"
            )
        
        added = 0
        updated = 0
        session = SessionLocal()
        
        try:
            for product in products:
                symbol = product.get('symbol')
                if not symbol:
                    continue
                
                # Check if symbol exists
                existing = session.query(AllowedInstrument).filter(
                    AllowedInstrument.symbol == symbol
                ).first()
                
                # Determine if should be enabled
                should_enable = False
                if auto_enable:
                    contract_type = product.get('contract_type', '')
                    # Auto-enable perpetual futures
                    should_enable = contract_type == 'perpetual_futures'
                
                if existing:
                    # Update existing
                    existing.name = product.get('description', symbol)
                    existing.instrument_type = product.get(
                        'contract_type',
                        'perpetual_futures'
                    )
                    existing.base_currency = product.get(
                        'underlying_asset',
                        {}
                    ).get('symbol', '')
                    existing.quote_currency = product.get(
                        'settling_asset',
                        {}
                    ).get('symbol', '')
                    
                    # Only enable if auto_enable is True
                    # Don't disable existing enabled symbols
                    if should_enable and not existing.enabled:
                        existing.enabled = True
                    
                    updated += 1
                    if updated <= 10:  # Log first 10
                        status = "[ENABLED]" if existing.enabled else "[DISABLED]"
                        LOG.info(f"  [UPDATE] {status} {symbol}")
                else:
                    # Add new
                    instrument = AllowedInstrument(
                        symbol=symbol,
                        name=product.get('description', symbol),
                        instrument_type=product.get(
                            'contract_type',
                            'perpetual_futures'
                        ),
                        base_currency=product.get(
                            'underlying_asset',
                            {}
                        ).get('symbol', ''),
                        quote_currency=product.get(
                            'settling_asset',
                            {}
                        ).get('symbol', ''),
                        enabled=should_enable
                    )
                    session.add(instrument)
                    added += 1
                    if added <= 10:  # Log first 10
                        status = "[ENABLED]" if should_enable else "[DISABLED]"
                        LOG.info(f"  [ADD] {status} {symbol}")
            
            # Commit changes
            session.commit()
            
            LOG.info("")
            LOG.info("=" * 80)
            LOG.info("[SUMMARY] Symbol sync completed")
            LOG.info(f"  Added: {added}")
            LOG.info(f"  Updated: {updated}")
            LOG.info(f"  Total processed: {len(products)}")
            LOG.info("=" * 80)
            LOG.info("")
            
            return {
                'success': True,
                'added': added,
                'updated': updated,
                'total': len(products),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            session.rollback()
            LOG.error(f"[ERROR] Failed to sync symbols: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'added': added,
                'updated': updated,
                'total': len(products)
            }
        finally:
            session.close()


# Global instance
_delta_trader = None

def get_delta_trader() -> DeltaExchangeTrader:
    """Get or create Delta Exchange trader instance"""
    global _delta_trader
    if _delta_trader is None:
        LOG.info("Creating new DeltaExchangeTrader instance...")
        _delta_trader = DeltaExchangeTrader()
        LOG.info("DeltaExchangeTrader instance created and cached")
    else:
        LOG.debug("Returning cached DeltaExchangeTrader instance")
    return _delta_trader
