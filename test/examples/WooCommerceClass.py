from typing import Dict, Any, Optional, List
import requests
from urllib.parse import urlencode, quote, urljoin
import time
import random
import string
import hmac
import hashlib
import base64
import logging
from dataclasses import dataclass
from enum import Enum

class WooCommerceAuthType(str, Enum):
    """Authentication types supported by WooCommerce"""
    BASIC = "basic"
    OAUTH = "oauth"

@dataclass
class WooCommerceConfig:
    """Configuration class for WooCommerce settings"""
    store_url: str
    consumer_key: str
    consumer_secret: str
    api_version: str = "wc/v3"
    is_https: bool = False
    auth_type: WooCommerceAuthType = WooCommerceAuthType.BASIC
    verify_ssl: bool = True
    timeout: int = 30
    query_string_auth: bool = False

class WooCommerceError(Exception):
    """Custom exception for WooCommerce-related errors"""
    pass

class WooCommerceClass:
    """Helper class to handle WooCommerce API operations"""
    
    def __init__(self, config: WooCommerceConfig):
        self.config = config
        self._validate_config()
        self.base_url = self._get_base_url()
        logging.info(f"WooCommerce client initialized for store: {self.config.store_url}")

    def _validate_config(self) -> None:
        if not all([self.config.store_url, self.config.consumer_key, self.config.consumer_secret]):
            raise WooCommerceError("Missing required configuration parameters")
        
        if self.config.store_url.startswith('https://'):
            self.config.is_https = True
        
        if not self.config.is_https:
            self.config.auth_type = WooCommerceAuthType.OAUTH
            self.config.query_string_auth = True

    def _get_base_url(self) -> str:
        return urljoin(
            self.config.store_url.rstrip('/') + '/',
            f"wp-json/{self.config.api_version}/"
        )

    def _get_oauth_params(self, method: str, url: str) -> Dict[str, str]:
        params = {
            'oauth_consumer_key': self.config.consumer_key,
            'oauth_nonce': ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            'oauth_signature_method': 'HMAC-SHA256',
            'oauth_timestamp': str(int(time.time()))
        }
        
        base_string = '&'.join([
            method,
            quote(url, safe=''),
            quote(urlencode(sorted(params.items())), safe='')
        ])
        
        key = f"{self.config.consumer_secret}&"
        signature = base64.b64encode(
            hmac.new(
                key.encode(),
                base_string.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        
        params['oauth_signature'] = signature
        return params

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        headers = {'Content-Type': 'application/json'}
        request_params = params or {}

        try:
            if self.config.auth_type == WooCommerceAuthType.BASIC:
                auth = (self.config.consumer_key, self.config.consumer_secret)
                if self.config.query_string_auth:
                    request_params.update({
                        'consumer_key': self.config.consumer_key,
                        'consumer_secret': self.config.consumer_secret
                    })
                    auth = None
            else:
                auth = None
                request_params.update(self._get_oauth_params(method, url))

            response = requests.request(
                method=method,
                url=url,
                params=request_params,
                json=data,
                headers=headers,
                auth=auth,
                verify=self.config.verify_ssl,
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"WooCommerce API request failed: {str(e)}")
            if response := getattr(e, 'response', None):
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', str(e))
                except ValueError:
                    error_message = str(e)
            else:
                error_message = str(e)
            raise WooCommerceError(f"API request failed: {error_message}")

    # Product Methods
    def get_products(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get products with optional filtering"""
        return self.request('GET', 'products', params=params)

    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get a single product by ID"""
        return self.request('GET', f'products/{product_id}')

    def create_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product"""
        return self.request('POST', 'products', data=data)

    def update_product(self, product_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product"""
        return self.request('PUT', f'products/{product_id}', data=data)

    def delete_product(self, product_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a product"""
        return self.request('DELETE', f'products/{product_id}', params={'force': force})
    
    def get_product_categories(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all product categories"""
        return self.request('GET', 'products/categories', params=params)

    # Order Methods
    def get_orders(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get orders with optional filtering"""
        return self.request('GET', 'orders', params=params)

    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get a single order by ID"""
        return self.request('GET', f'orders/{order_id}')

    def create_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        return self.request('POST', 'orders', data=data)

    def update_order(self, order_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an order"""
        return self.request('PUT', f'orders/{order_id}', data=data)

    def delete_order(self, order_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete an order"""
        return self.request('DELETE', f'orders/{order_id}', params={'force': force})

    # Customer Methods
    def get_customers(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get customers with optional filtering"""
        return self.request('GET', 'customers', params=params)

    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Get a single customer by ID"""
        return self.request('GET', f'customers/{customer_id}')

    def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer"""
        return self.request('POST', 'customers', data=data)

    def update_customer(self, customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a customer"""
        return self.request('PUT', f'customers/{customer_id}', data=data)

    def delete_customer(self, customer_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a customer"""
        return self.request('DELETE', f'customers/{customer_id}', params={'force': force})

    def get_customer_downloads(self, customer_id: int) -> List[Dict[str, Any]]:
        """Get customer downloads"""
        return self.request('GET', f'customers/{customer_id}/downloads')

    # Product Review Methods
    def get_product_reviews(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get product reviews with optional filtering"""
        return self.request('GET', 'products/reviews', params=params)

    def get_product_review(self, review_id: int) -> Dict[str, Any]:
        """Get a single product review by ID"""
        return self.request('GET', f'products/reviews/{review_id}')

    def create_product_review(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product review"""
        return self.request('POST', 'products/reviews', data=data)

    def update_product_review(self, review_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product review"""
        return self.request('PUT', f'products/reviews/{review_id}', data=data)

    def delete_product_review(self, review_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a product review"""
        return self.request('DELETE', f'products/reviews/{review_id}', params={'force': force})

    # Refund Methods
    def get_refunds(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all refunds with optional filtering"""
        return self.request('GET', 'refunds', params=params)

    def get_order_refunds(self, order_id: int, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get refunds for a specific order"""
        return self.request('GET', f'orders/{order_id}/refunds', params=params)

    def get_order_refund(self, order_id: int, refund_id: int) -> Dict[str, Any]:
        """Get a specific refund from an order"""
        return self.request('GET', f'orders/{order_id}/refunds/{refund_id}')

    def create_order_refund(self, order_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a refund for an order"""
        return self.request('POST', f'orders/{order_id}/refunds', data=data)

    def delete_order_refund(self, order_id: int, refund_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a refund from an order"""
        return self.request('DELETE', f'orders/{order_id}/refunds/{refund_id}', params={'force': force})

    # Report Methods
    def get_reports(self) -> List[Dict[str, Any]]:
        """Get all available reports"""
        return self.request('GET', 'reports')

    def get_sales_report(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get sales report"""
        return self.request('GET', 'reports/sales', params=params)

    def get_top_sellers_report(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get top sellers report"""
        return self.request('GET', 'reports/top_sellers', params=params)

    def get_orders_totals(self) -> List[Dict[str, Any]]:
        """Get orders totals"""
        return self.request('GET', 'reports/orders/totals')

    def get_customers_totals(self) -> List[Dict[str, Any]]:
        """Get customers totals"""
        return self.request('GET', 'reports/customers/totals')

    # Shipping Class Methods 
    def get_shipping_classes(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all shipping classes"""
        return self.request('GET', 'products/shipping_classes', params=params)

    def get_shipping_class(self, shipping_class_id: int) -> Dict[str, Any]:
        """Get a single shipping class"""
        return self.request('GET', f'products/shipping_classes/{shipping_class_id}')

    def create_shipping_class(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new shipping class"""
        return self.request('POST', 'products/shipping_classes', data=data)

    def update_shipping_class(self, shipping_class_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a shipping class"""
        return self.request('PUT', f'products/shipping_classes/{shipping_class_id}', data=data)

    def delete_shipping_class(self, shipping_class_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a shipping class"""
        return self.request('DELETE', f'products/shipping_classes/{shipping_class_id}', params={'force': force})
    
    # Product Tag Methods
    def get_product_tags(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all product tags"""
        return self.request('GET', 'products/tags', params=params)
    
    def get_product_tag(self, tag_id: int) -> Dict[str, Any]:
        """Get a single product tag"""
        return self.request('GET', f'products/tags/{tag_id}')
    
    def create_product_tag(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product tag"""
        return self.request('POST', 'products/tags', data=data)
    
    def update_product_tag(self, tag_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product tag"""
        return self.request('PUT', f'products/tags/{tag_id}', data=data)
    
    def delete_product_tag(self, tag_id: int, force: bool = False) -> Dict[str, Any]:
        """Delete a product tag"""
        return self.request('DELETE', f'products/tags/{tag_id}', params={'force': force})
    
    # Coupon Methods
    def get_coupons(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all coupons"""
        return self.request('GET', 'coupons', params=params)
    
    def get_coupon(self, coupon_id: int) -> Dict[str, Any]:
        """Get a single coupon"""
        return self.request('GET', f'coupons/{coupon_id}')
    
    def create_coupon(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new coupon"""
        return self.request('POST', 'coupons', data=data)
    
    def update_coupon(self, coupon_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a coupon"""
        return self.request('PUT', f'coupons/{coupon_id}', data=data)
    
    def delete_coupon(self, coupon_id: int, force: bool = True) -> Dict[str, Any]:
        """Delete a coupon"""
        return self.request('DELETE', f'coupons/{coupon_id}', params={'force': force})

    # Batch Methods
    def batch_update_products(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete products"""
        return self.request('POST', 'products/batch', data=data)

    def batch_update_orders(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete orders"""
        return self.request('POST', 'orders/batch', data=data)

    def batch_update_customers(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete customers"""
        return self.request('POST', 'customers/batch', data=data)

    def batch_update_reviews(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete product reviews"""
        return self.request('POST', 'products/reviews/batch', data=data)
    
    def batch_update_refunds(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete refunds"""
        return self.request('POST', 'refunds/batch', data=data)
    
    def batch_update_shipping_classes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete shipping classes"""
        return self.request('POST', 'products/shipping_classes/batch', data=data)
    
    def batch_update_product_tags(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete product tags"""
        return self.request('POST', 'products/tags/batch', data=data)
    
    def batch_update_coupons(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Batch create/update/delete coupons"""
        return self.request('POST', 'coupons/batch', data=data)