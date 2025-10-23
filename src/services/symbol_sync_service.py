"""
Symbol Synchronization Service
Fetches available products from Delta Exchange API and updates database
"""
import logging
from typing import Dict, List, Optional
import requests
from datetime import datetime

from src.database.session import SessionLocal
from src.models.base import AllowedInstrument


LOG = logging.getLogger(__name__)

# Delta Exchange API endpoint
DELTA_PRODUCTS_API = "https://api.india.delta.exchange/v2/products"


class SymbolSyncService:
    """Service to sync symbols from Delta Exchange"""
    
    def __init__(self):
        """Initialize symbol sync service"""
        self.session = SessionLocal()
        LOG.info("=" * 80)
        LOG.info("[SYMBOL SYNC] Service initialized")
        LOG.info("=" * 80)
    
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
    
    def sync_symbols(
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
        LOG.info("")
        LOG.info("=" * 80)
        LOG.info("[SYNC] Starting symbol synchronization")
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
                if p.get('product_type') in product_types
            ]
            LOG.info(
                f"[FILTER] Filtered {original_count} -> {len(products)} "
                f"products by types: {product_types}"
            )
        
        added = 0
        updated = 0
        
        try:
            for product in products:
                symbol = product.get('symbol')
                if not symbol:
                    continue
                
                # Check if symbol exists
                existing = self.session.query(AllowedInstrument).filter(
                    AllowedInstrument.symbol == symbol
                ).first()
                
                # Determine if should be enabled
                should_enable = False
                if auto_enable:
                    product_type = product.get('product_type', '')
                    # Auto-enable perpetual futures
                    should_enable = product_type == 'perpetual_futures'
                
                if existing:
                    # Update existing
                    existing.name = product.get('description', symbol)
                    existing.instrument_type = product.get(
                        'product_type',
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
                    status = "[ENABLED]" if existing.enabled else "[DISABLED]"
                    LOG.debug(f"  [UPDATE] {status} {symbol}")
                else:
                    # Add new
                    instrument = AllowedInstrument(
                        symbol=symbol,
                        name=product.get('description', symbol),
                        instrument_type=product.get(
                            'product_type',
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
                    self.session.add(instrument)
                    added += 1
                    status = "[ENABLED]" if should_enable else "[DISABLED]"
                    LOG.debug(f"  [ADD] {status} {symbol}")
            
            # Commit changes
            self.session.commit()
            
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
            self.session.rollback()
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
            self.session.close()
    
    def get_enabled_symbols(self) -> List[str]:
        """Get list of enabled symbols"""
        try:
            instruments = self.session.query(AllowedInstrument).filter(
                AllowedInstrument.enabled == True  # noqa: E712
            ).all()
            
            symbols = [inst.symbol for inst in instruments]
            LOG.info(f"[ENABLED] Found {len(symbols)} enabled symbols")
            return symbols
            
        except Exception as e:
            LOG.error(f"[ERROR] Failed to get enabled symbols: {e}")
            return []
        finally:
            self.session.close()


# Singleton instance
_symbol_sync_service = None


def get_symbol_sync_service() -> SymbolSyncService:
    """Get singleton instance of SymbolSyncService"""
    global _symbol_sync_service
    if _symbol_sync_service is None:
        _symbol_sync_service = SymbolSyncService()
    return _symbol_sync_service
