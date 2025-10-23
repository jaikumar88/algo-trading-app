#!/usr/bin/env python3
"""
Delta Exchange Trading Client
A properly structured client for Delta Exchange API with testing capabilities
"""
import hashlib
import hmac
import requests
import time
import json
from typing import Dict, Optional


class DeltaExchangeClient:
    """Delta Exchange API Client with signature authentication"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = 'https://api.india.delta.exchange', mock_mode: bool = False):
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.mock_mode = mock_mode
    
    def generate_signature(self, message: str) -> str:
        """Generate HMAC SHA256 signature"""
        message_bytes = bytes(message, 'utf-8')
        secret_bytes = bytes(self.api_secret, 'utf-8')
        signature_hash = hmac.new(secret_bytes, message_bytes, hashlib.sha256)
        return signature_hash.hexdigest()
    
    def _mock_response(self, method: str, path: str, params: Optional[Dict], payload: str):
        """Generate mock responses for testing"""
        class MockResponse:
            def __init__(self, json_data, status_code=200):
                self.json_data = json_data
                self.status_code = status_code
            
            def json(self):
                return self.json_data
        
        # Mock responses based on path
        if 'wallet/balances' in path:
            return MockResponse({
                "success": True,
                "result": [
                    {"asset_id": 1, "available_balance": "1000.00", "balance": "1000.00"}
                ]
            })
        elif 'orders' in path and method == 'GET':
            return MockResponse({
                "success": True,
                "result": [
                    {"id": 123, "product_id": 1, "side": "buy", "size": 3, "state": "open"}
                ]
            })
        elif 'orders' in path and method == 'POST':
            return MockResponse({
                "success": True,
                "result": {"id": 456, "state": "open", "message": "Order placed successfully (MOCK)"}
            })
        elif 'positions' in path:
            return MockResponse({
                "success": True,
                "result": [
                    {"product_id": 1, "size": 10, "entry_price": "0.0005"}
                ]
            })
        else:
            return MockResponse({"success": True, "result": {}})
    
    def _make_request(self, method: str, path: str, payload: str = '', params: Optional[Dict] = None) -> requests.Response:
        """Make authenticated request to Delta Exchange API"""
        # Mock mode for testing
        if self.mock_mode:
            return self._mock_response(method, path, params, payload)
        
        timestamp = str(int(time.time()))
        url = f'{self.base_url}{path}'
        
        # Build query string for signature
        query_string = ''
        if params:
            query_parts = [f"{k}={v}" for k, v in params.items()]
            query_string = '?' + '&'.join(query_parts)
        
        # Generate signature
        signature_data = method + timestamp + path + query_string + payload
        signature = self.generate_signature(signature_data)
        
        # Prepare headers
        headers = {
            'api-key': self.api_key,
            'timestamp': timestamp,
            'signature': signature,
            'User-Agent': 'python-rest-client',
            'Content-Type': 'application/json'
        }
        
        # Make request
        try:
            response = self.session.request(
                method=method,
                url=url,
                data=payload,
                params=params or {},
                headers=headers,
                timeout=(3, 27)
            )
            
            # Check for API errors
            if response.status_code == 200:
                data = response.json()
                if not data.get('success', True):
                    error_info = data.get('error', {})
                    error_code = error_info.get('code', 'unknown')
                    error_context = error_info.get('context', {})
                    
                    if error_code == 'ip_not_whitelisted_for_api_key':
                        client_ip = error_context.get('client_ip', 'unknown')
                        print(f"⚠️  API Error: IP not whitelisted - {client_ip}")
                        print(f"    Please whitelist this IP in Delta Exchange API settings")
                    else:
                        print(f"⚠️  API Error: {error_code}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            raise
    
    def get_open_orders(self, product_id: int = 1) -> Dict:
        """Get all open orders for a product"""
        method = 'GET'
        path = '/v2/orders'
        params = {'product_id': product_id, 'state': 'open'}
        
        response = self._make_request(method, path, params=params)
        return response.json()
    
    def place_order(self, product_id: int, side: str, size: float, limit_price: str, order_type: str = 'limit_order') -> Dict:
        """Place a new order"""
        method = 'POST'
        path = '/v2/orders'
        
        order_data = {
            "order_type": order_type,
            "size": size,
            "side": side,
            "limit_price": limit_price,
            "product_id": product_id
        }
        
        payload = json.dumps(order_data)
        response = self._make_request(method, path, payload=payload)
        return response.json()
    
    def get_wallet_balance(self) -> Dict:
        """Get wallet balance"""
        method = 'GET'
        path = '/v2/wallet/balances'
        
        response = self._make_request(method, path)
        return response.json()
    
    def get_positions(self, product_id: Optional[int] = None, underlying_asset: Optional[str] = None) -> Dict:
        """Get current positions
        
        Args:
            product_id: Product ID to filter positions
            underlying_asset: Underlying asset symbol (e.g., 'BTC', 'ETH')
        """
        method = 'GET'
        path = '/v2/positions'
        
        params = {}
        if product_id:
            params['product_id'] = product_id
        elif underlying_asset:
            params['underlying_asset_symbol'] = underlying_asset
        
        response = self._make_request(method, path, params=params)
        return response.json()
    
    def cancel_order(self, order_id: int) -> Dict:
        """Cancel an order by ID"""
        method = 'DELETE'
        path = f'/v2/orders/{order_id}'
        
        response = self._make_request(method, path)
        return response.json()

    def get_products(self) -> Dict:
        """Get all available products"""
        method = 'GET'
        path = '/v2/products'
        
        response = self._make_request(method, path)
        return response.json()
    
    def get_product_by_symbol(self, symbol: str) -> Dict:
        """Get product details by symbol (e.g., 'BTCUSD')"""
        method = 'GET'
        path = '/v2/products'
        params = {'symbol': symbol}
        
        response = self._make_request(method, path, params=params)
        return response.json()
    
    def get_product_by_id(self, product_id: int) -> Dict:
        """Get product details by product ID"""
        method = 'GET'
        path = f'/v2/products/{product_id}'
        
        response = self._make_request(method, path)
        return response.json()
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker/price data for a symbol"""
        method = 'GET'
        path = '/v2/tickers'
        params = {'symbol': symbol}
        
        response = self._make_request(method, path, params=params)
        return response.json()
    
    def get_orderbook(self, symbol: str, depth: int = 10) -> Dict:
        """Get orderbook (bids/asks) for a product
        
        Args:
            symbol: Product symbol (e.g., 'BTCUSD')
            depth: Number of price levels to return (default 10)
        """
        method = 'GET'
        path = f'/v2/l2orderbook/{symbol}'
        
        response = self._make_request(method, path)
        return response.json()
        print(r.json())
        return r.json()

def test_client(use_mock: bool = False):
    """Test the Delta Exchange client"""
    
    
    client = DeltaExchangeClient(api_key, api_secret, mock_mode=use_mock)
    
    mode = "MOCK MODE" if use_mock else "LIVE API"
    print(f"🚀 Testing Delta Exchange Trading Client - {mode}")
    print("=" * 50)
    
    # Test 1: Get wallet balance
    print("\n1️⃣ Testing: Get Wallet Balance")
    try:
        balance = client.get_wallet_balance()
        print(f"✅ Success: {json.dumps(balance, indent=2)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 2: Get open orders
    print("\n2️⃣ Testing: Get Open Orders")
    try:
        orders = client.get_open_orders(product_id=1)
        print(f"✅ Success: Found {len(orders.get('result', []))} open orders")
        print(f"   Response: {json.dumps(orders, indent=2)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 3: Get positions
    print("\n3️⃣ Testing: Get Positions (for BTC)")
    try:
        positions = client.get_positions(underlying_asset='BTC')
        print(f"✅ Success: {json.dumps(positions, indent=2)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 4: Get all products
    print("\n4️⃣ Testing: Get All Products")
    try:
        products = client.get_products()
        product_count = len(products.get('result', []))
        print(f"✅ Success: Found {product_count} products")
        if product_count > 0:
            # Show first 3 products as sample
            print(f"   Sample products:")
            for i, product in enumerate(products.get('result', [])[:3]):
                print(f"   - ID: {product.get('id')}, Symbol: {product.get('symbol')}, Description: {product.get('description', 'N/A')}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 5: Get product by symbol
    print("\n5️⃣ Testing: Get Product by Symbol (BTCUSD)")
    try:
        product = client.get_product_by_symbol('BTCUSD')
        if product.get('result'):
            prod_info = product['result'][0] if isinstance(product['result'], list) else product['result']
            print(f"✅ Success:")
            print(f"   ID: {prod_info.get('id')}")
            print(f"   Symbol: {prod_info.get('symbol')}")
            print(f"   Contract Type: {prod_info.get('contract_type')}")
            print(f"   Tick Size: {prod_info.get('tick_size')}")
        else:
            print(f"✅ Response: {json.dumps(product, indent=2)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    
    # Test 6: Place order (commented out to avoid accidental execution)
    print("\n6️⃣ Testing: Place Order (DRY RUN)")
    print("   ⚠️  Order placement is disabled in test mode")
    print("   To enable, uncomment the code block below")
    
    # Uncomment to actually place an order (BE CAREFUL!)
    # try:
    #     order_result = client.place_order(
    #         product_id=16,
    #         side='buy',
    #         size=3,
    #         limit_price='0.0005'
    #     )
    #     print(f"✅ Order placed: {json.dumps(order_result, indent=2)}")
    # except Exception as e:
    #     print(f"❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")


if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    use_mock = '--mock' in sys.argv or '-m' in sys.argv
    
    if use_mock:
        print("Running in MOCK mode (safe testing)")
        test_client(use_mock=True)
    else:
        print("Running in LIVE mode (real API calls)")
        print("Use --mock flag for safe testing without real API calls")
        print()
        test_client(use_mock=False)