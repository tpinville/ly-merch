#!/usr/bin/env python3
"""
Integration test script for LY-Merch API
Tests all endpoints with real data and database
"""

import json
import time
import sys
import requests
from typing import Dict, List, Any, Optional
import csv
import io

# Configuration
API_BASE_URL = "http://localhost:8001"
TEST_DATA_DIR = "../data"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def log_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def log_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def log_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

class APITester:
    """Integration tester for LY-Merch API"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

    def make_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            log_error(f"Request failed: {e}")
            return None

    def assert_status_code(self, response: requests.Response, expected: int, test_name: str):
        """Assert response status code"""
        if response.status_code == expected:
            log_success(f"{test_name}: Status {response.status_code}")
            self.test_results['passed'] += 1
        else:
            log_error(f"{test_name}: Expected {expected}, got {response.status_code}")
            if response.text:
                log_error(f"Response: {response.text[:200]}...")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: Status code mismatch")

    def assert_json_response(self, response: requests.Response, test_name: str) -> Optional[Dict]:
        """Assert response is valid JSON"""
        try:
            data = response.json()
            log_success(f"{test_name}: Valid JSON response")
            return data
        except json.JSONDecodeError as e:
            log_error(f"{test_name}: Invalid JSON response: {e}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: Invalid JSON")
            return None

    def assert_field_exists(self, data: Dict, field: str, test_name: str):
        """Assert field exists in response data"""
        if field in data:
            log_success(f"{test_name}: Field '{field}' exists")
            self.test_results['passed'] += 1
        else:
            log_error(f"{test_name}: Field '{field}' missing")
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: Missing field {field}")

    def test_health_endpoint(self):
        """Test health check endpoint"""
        log_info("Testing health endpoint...")

        response = self.make_request('GET', '/health')
        if not response:
            return

        self.assert_status_code(response, 200, "Health endpoint")
        data = self.assert_json_response(response, "Health endpoint JSON")

        if data:
            self.assert_field_exists(data, 'status', "Health status field")
            self.assert_field_exists(data, 'api_version', "Health API version field")
            self.assert_field_exists(data, 'database', "Health database field")

    def test_root_endpoint(self):
        """Test root endpoint"""
        log_info("Testing root endpoint...")

        response = self.make_request('GET', '/')
        if not response:
            return

        self.assert_status_code(response, 200, "Root endpoint")
        data = self.assert_json_response(response, "Root endpoint JSON")

        if data:
            self.assert_field_exists(data, 'message', "Root message field")
            self.assert_field_exists(data, 'endpoints', "Root endpoints field")

    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        log_info("Testing statistics endpoint...")

        response = self.make_request('GET', '/api/v1/stats')
        if not response:
            return

        self.assert_status_code(response, 200, "Stats endpoint")
        data = self.assert_json_response(response, "Stats endpoint JSON")

        if data:
            required_fields = [
                'total_categories', 'total_verticals', 'total_trends',
                'total_images', 'total_products', 'categories',
                'geo_zones', 'image_types'
            ]

            for field in required_fields:
                self.assert_field_exists(data, field, f"Stats {field} field")

    def test_categories_endpoints(self):
        """Test categories endpoints"""
        log_info("Testing categories endpoints...")

        # Test list categories
        response = self.make_request('GET', '/api/v1/categories/')
        if not response:
            return

        self.assert_status_code(response, 200, "List categories")
        categories = self.assert_json_response(response, "Categories list JSON")

        if categories and len(categories) > 0:
            # Test single category
            category_id = categories[0]['id']
            response = self.make_request('GET', f'/api/v1/categories/{category_id}')

            if response:
                self.assert_status_code(response, 200, "Get single category")
                self.assert_json_response(response, "Single category JSON")

            # Test category with filters
            response = self.make_request('GET', '/api/v1/categories/', params={'limit': 5})
            if response:
                self.assert_status_code(response, 200, "Categories with limit")

        # Test non-existent category
        response = self.make_request('GET', '/api/v1/categories/999999')
        if response:
            self.assert_status_code(response, 404, "Non-existent category")

    def test_verticals_endpoints(self):
        """Test verticals endpoints"""
        log_info("Testing verticals endpoints...")

        # Test list verticals
        response = self.make_request('GET', '/api/v1/verticals/')
        if not response:
            return

        self.assert_status_code(response, 200, "List verticals")
        verticals = self.assert_json_response(response, "Verticals list JSON")

        if verticals and len(verticals) > 0:
            # Test single vertical
            vertical_id = verticals[0]['id']
            response = self.make_request('GET', f'/api/v1/verticals/{vertical_id}')

            if response:
                self.assert_status_code(response, 200, "Get single vertical")

            # Test vertical with trends
            response = self.make_request('GET', f'/api/v1/verticals/{vertical_id}?include_trends=true')
            if response:
                self.assert_status_code(response, 200, "Vertical with trends")

        # Test geo zones
        response = self.make_request('GET', '/api/v1/verticals/search/geo-zones')
        if response:
            self.assert_status_code(response, 200, "Geo zones endpoint")

    def test_trends_endpoints(self):
        """Test trends endpoints"""
        log_info("Testing trends endpoints...")

        # Test list trends
        response = self.make_request('GET', '/api/v1/trends/')
        if not response:
            return

        self.assert_status_code(response, 200, "List trends")
        trends = self.assert_json_response(response, "Trends list JSON")

        if trends and len(trends) > 0:
            # Test single trend
            trend_id = trends[0]['id']
            response = self.make_request('GET', f'/api/v1/trends/{trend_id}')

            if response:
                self.assert_status_code(response, 200, "Get single trend")

            # Test trend with images
            response = self.make_request('GET', f'/api/v1/trends/{trend_id}?include_images=true')
            if response:
                self.assert_status_code(response, 200, "Trend with images")

        # Test full-text search
        response = self.make_request('GET', '/api/v1/trends/search/fulltext', params={'q': 'fashion'})
        if response:
            self.assert_status_code(response, 200, "Trends full-text search")

    def test_images_endpoints(self):
        """Test images endpoints"""
        log_info("Testing images endpoints...")

        # Test list images
        response = self.make_request('GET', '/api/v1/images/')
        if not response:
            return

        self.assert_status_code(response, 200, "List images")
        images = self.assert_json_response(response, "Images list JSON")

        if images and len(images) > 0:
            # Test single image
            image_id = images[0]['id']
            response = self.make_request('GET', f'/api/v1/images/{image_id}')

            if response:
                self.assert_status_code(response, 200, "Get single image")

            # Test images with filters
            response = self.make_request('GET', '/api/v1/images/', params={'image_type': 'positive'})
            if response:
                self.assert_status_code(response, 200, "Images with type filter")

        # Test image stats
        response = self.make_request('GET', '/api/v1/images/stats/summary')
        if response:
            self.assert_status_code(response, 200, "Image statistics")

    def test_products_endpoints(self):
        """Test products endpoints"""
        log_info("Testing products endpoints...")

        # Test list products
        response = self.make_request('GET', '/api/v1/products/')
        if not response:
            return

        self.assert_status_code(response, 200, "List products")
        products = self.assert_json_response(response, "Products list JSON")

        if products and len(products) > 0:
            # Test single product
            product_id = products[0]['id']
            response = self.make_request('GET', f'/api/v1/products/{product_id}')

            if response:
                self.assert_status_code(response, 200, "Get single product")

            # Test products with filters
            response = self.make_request('GET', '/api/v1/products/', params={
                'limit': 10,
                'brand': products[0].get('brand', '')
            })
            if response:
                self.assert_status_code(response, 200, "Products with filters")

        # Test product stats
        response = self.make_request('GET', '/api/v1/products/stats/summary')
        if response:
            self.assert_status_code(response, 200, "Product statistics")

    def test_bulk_upload(self):
        """Test bulk product upload"""
        log_info("Testing bulk product upload...")

        # Create test products data
        test_products = {
            "products": [
                {
                    "product_id": f"INTEGRATION_TEST_{int(time.time())}_001",
                    "name": "Integration Test Product 1",
                    "product_type": "sneakers",
                    "brand": "Test Brand",
                    "price": 99.99,
                    "currency": "USD",
                    "color": "Blue",
                    "size": "10",
                    "gender": "male",
                    "availability_status": "in_stock"
                },
                {
                    "product_id": f"INTEGRATION_TEST_{int(time.time())}_002",
                    "name": "Integration Test Product 2",
                    "product_type": "boots",
                    "brand": "Test Brand",
                    "price": 149.99,
                    "currency": "USD",
                    "color": "Brown",
                    "size": "9",
                    "gender": "female",
                    "availability_status": "pre_order"
                }
            ]
        }

        response = self.make_request('POST', '/api/v1/products/bulk', json=test_products)
        if not response:
            return

        self.assert_status_code(response, 200, "Bulk upload")
        data = self.assert_json_response(response, "Bulk upload JSON")

        if data:
            # Check response structure
            required_fields = ['uploaded_count', 'skipped_count', 'error_count']
            for field in required_fields:
                self.assert_field_exists(data, field, f"Bulk upload {field} field")

            # Verify upload was successful
            if data.get('uploaded_count', 0) > 0:
                log_success(f"Successfully uploaded {data['uploaded_count']} products")
                self.test_results['passed'] += 1
            else:
                log_warning("No products were uploaded")

    def test_pagination_and_limits(self):
        """Test pagination and limit parameters"""
        log_info("Testing pagination and limits...")

        endpoints = [
            '/api/v1/categories/',
            '/api/v1/verticals/',
            '/api/v1/trends/',
            '/api/v1/images/',
            '/api/v1/products/'
        ]

        for endpoint in endpoints:
            # Test with limit
            response = self.make_request('GET', endpoint, params={'limit': 5})
            if response:
                self.assert_status_code(response, 200, f"Pagination limit for {endpoint}")

            # Test with offset
            response = self.make_request('GET', endpoint, params={'limit': 5, 'offset': 10})
            if response:
                self.assert_status_code(response, 200, f"Pagination offset for {endpoint}")

    def test_error_handling(self):
        """Test error handling for various scenarios"""
        log_info("Testing error handling...")

        # Test invalid endpoints
        invalid_endpoints = [
            '/api/v1/nonexistent/',
            '/api/v1/categories/invalid_id',
            '/api/v1/products/not_a_number'
        ]

        for endpoint in invalid_endpoints:
            response = self.make_request('GET', endpoint)
            if response:
                if response.status_code in [404, 422]:
                    log_success(f"Proper error handling for {endpoint}")
                    self.test_results['passed'] += 1
                else:
                    log_error(f"Unexpected status for {endpoint}: {response.status_code}")
                    self.test_results['failed'] += 1

        # Test invalid bulk upload
        invalid_bulk_data = {"invalid": "data"}
        response = self.make_request('POST', '/api/v1/products/bulk', json=invalid_bulk_data)
        if response:
            if response.status_code == 422:
                log_success("Proper validation for invalid bulk upload")
                self.test_results['passed'] += 1
            else:
                log_error(f"Expected 422 for invalid bulk upload, got {response.status_code}")
                self.test_results['failed'] += 1

    def wait_for_api(self, timeout: int = 30) -> bool:
        """Wait for API to be available"""
        log_info(f"Waiting for API at {self.base_url} to be available...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.make_request('GET', '/health')
                if response and response.status_code == 200:
                    log_success("API is available")
                    return True
            except:
                pass

            time.sleep(1)

        log_error(f"API not available after {timeout} seconds")
        return False

    def run_all_tests(self):
        """Run all integration tests"""
        log_info("Starting LY-Merch API Integration Tests")
        print("=" * 60)

        # Wait for API to be available
        if not self.wait_for_api():
            log_error("API is not available. Please start the API server first.")
            return False

        # Run all tests
        test_methods = [
            self.test_health_endpoint,
            self.test_root_endpoint,
            self.test_stats_endpoint,
            self.test_categories_endpoints,
            self.test_verticals_endpoints,
            self.test_trends_endpoints,
            self.test_images_endpoints,
            self.test_products_endpoints,
            self.test_bulk_upload,
            self.test_pagination_and_limits,
            self.test_error_handling
        ]

        for test_method in test_methods:
            try:
                test_method()
                print("-" * 40)
            except Exception as e:
                log_error(f"Test {test_method.__name__} failed with exception: {e}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append(f"{test_method.__name__}: {str(e)}")

        # Print summary
        self.print_summary()

        return self.test_results['failed'] == 0

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        log_info("Test Results Summary")
        print("=" * 60)

        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"{Colors.GREEN}Passed: {self.test_results['passed']}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.test_results['failed']}{Colors.END}")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.test_results['errors']:
            print(f"\n{Colors.RED}Errors:{Colors.END}")
            for error in self.test_results['errors']:
                print(f"  - {error}")

        print("=" * 60)

        if self.test_results['failed'] == 0:
            log_success("All integration tests passed! 🎉")
        else:
            log_error(f"{self.test_results['failed']} tests failed")


def main():
    """Main function"""
    # Parse command line arguments
    api_url = API_BASE_URL
    if len(sys.argv) > 1:
        api_url = sys.argv[1]

    # Create and run tester
    tester = APITester(api_url)
    success = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()