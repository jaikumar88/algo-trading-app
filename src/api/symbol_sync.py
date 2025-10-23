"""
Symbol Sync API Endpoints
Endpoints for synchronizing symbols from Delta Exchange
"""
import logging
from flask import Blueprint, jsonify, request

from src.services.delta_exchange_service import get_delta_trader


LOG = logging.getLogger(__name__)

symbol_sync_bp = Blueprint('symbol_sync', __name__, url_prefix='/api/delta')


@symbol_sync_bp.route('/sync/symbols', methods=['POST'])
def sync_symbols():
    """
    Sync symbols from Delta Exchange API
    
    Request body (optional):
        {
            "auto_enable": true,  // Auto-enable perpetual futures
            "product_types": ["perpetual_futures", "future"]
        }
    
    Returns:
        {
            "success": true,
            "added": 10,
            "updated": 50,
            "total": 60,
            "timestamp": "2025-10-22T..."
        }
    """
    try:
        data = request.get_json() or {}
        auto_enable = data.get('auto_enable', False)
        product_types = data.get('product_types')
        
        LOG.info(f"[API] Syncing symbols (auto_enable={auto_enable})")
        
        trader = get_delta_trader()
        result = trader.sync_symbols_to_db(
            auto_enable=auto_enable,
            product_types=product_types
        )
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        LOG.error(f"[API] Error syncing symbols: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@symbol_sync_bp.route('/sync/perpetuals', methods=['POST'])
def sync_perpetuals_only():
    """
    Sync only perpetual futures and auto-enable them
    
    Returns:
        {
            "success": true,
            "added": 5,
            "updated": 25,
            "total": 30
        }
    """
    try:
        LOG.info("[API] Syncing perpetual futures only")
        
        trader = get_delta_trader()
        result = trader.sync_symbols_to_db(
            auto_enable=True,
            product_types=['perpetual_futures']
        )
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        LOG.error(f"[API] Error syncing perpetuals: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@symbol_sync_bp.route('/products', methods=['GET'])
def get_products():
    """
    Get all products from Delta Exchange API
    
    Returns:
        {
            "success": true,
            "products": [...],
            "count": 150
        }
    """
    try:
        LOG.info("[API] Fetching products from Delta Exchange")
        
        trader = get_delta_trader()
        products = trader.fetch_all_products()
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        }), 200
        
    except Exception as e:
        LOG.error(f"[API] Error fetching products: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@symbol_sync_bp.route('/status', methods=['GET'])
def get_delta_status():
    """
    Get Delta Exchange integration status
    
    Returns:
        {
            "enabled": true,
            "client_ready": true,
            "api_key_configured": true,
            "api_secret_configured": true
        }
    """
    try:
        trader = get_delta_trader()
        status = trader.get_status()
        
        return jsonify(status), 200
        
    except Exception as e:
        LOG.error(f"[API] Error getting status: {e}")
        return jsonify({
            'error': str(e)
        }), 500
