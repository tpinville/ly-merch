#!/usr/bin/env python3
"""
Script to upload sample_products.csv to the API for testing
"""

import csv
import json
import requests
import sys

def normalize_gender(value):
    """Normalize gender values"""
    if not value:
        return 'unisex'
    val = str(value).strip().lower()
    if val in ['m', 'male', 'man', 'men']:
        return 'male'
    if val in ['f', 'female', 'woman', 'women']:
        return 'female'
    return 'unisex'

def normalize_availability(value):
    """Normalize availability status"""
    if not value:
        return 'in_stock'
    val = str(value).strip().lower().replace(' ', '_')
    valid_statuses = ['in_stock', 'out_of_stock', 'discontinued', 'pre_order']

    if val in valid_statuses:
        return val

    # Map common variations
    if val in ['available', 'in_stock']:
        return 'in_stock'
    if val in ['unavailable', 'out_of_stock', 'sold_out']:
        return 'out_of_stock'
    if val in ['preorder', 'pre_order', 'coming_soon']:
        return 'pre_order'

    return 'in_stock'

def parse_price(value):
    """Parse price, removing currency symbols"""
    if not value or value == '':
        return None

    # Remove currency symbols and parse
    cleaned = str(value).replace('$', '').replace('£', '').replace('€', '').replace('¥', '').replace(',', '').strip()
    try:
        price = float(cleaned)
        return price if price >= 0 else None
    except ValueError:
        return None

def csv_to_products(csv_file):
    """Convert CSV file to products list"""
    products = []

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for i, row in enumerate(reader, 1):
            # Map CSV columns to API fields
            product = {
                'product_id': row.get('product_id') or row.get('Product ID') or f"CSV_{i:04d}",
                'name': row.get('name') or row.get('Product Name') or row.get('Name', ''),
                'product_type': (row.get('product_type') or row.get('Type') or '').lower().strip(),
                'description': row.get('description') or row.get('Description') or '',
                'brand': row.get('brand') or row.get('Brand Name') or row.get('Brand') or '',
                'price': parse_price(row.get('price') or row.get('Price')),
                'currency': (row.get('currency') or row.get('Currency') or 'USD').upper(),
                'color': row.get('color') or row.get('Color') or '',
                'size': row.get('size') or row.get('Size') or '',
                'material': row.get('material') or row.get('Material') or '',
                'gender': normalize_gender(row.get('gender') or row.get('Target Gender') or row.get('Gender')),
                'season': row.get('season') or row.get('Season') or '',
                'availability_status': normalize_availability(row.get('availability_status') or row.get('Stock Status') or row.get('Status')),
                'image_url': row.get('image_url') or row.get('Image') or row.get('image') or '',
                'product_url': row.get('product_url') or row.get('Website') or row.get('product_url') or '',
                'trend_id': int(row.get('trend_id') or row.get('Trend ID') or 1) if row.get('trend_id') or row.get('Trend ID') else None
            }

            # Skip if missing required fields
            if not product['name'] or not product['product_type']:
                print(f"Skipping row {i}: missing required fields (name or product_type)")
                continue

            products.append(product)

    return products

def upload_products(products, api_url='http://localhost:8000'):
    """Upload products to the API"""
    url = f"{api_url}/api/v1/products/bulk"

    payload = {
        'products': products
    }

    headers = {
        'Content-Type': 'application/json'
    }

    print(f"Uploading {len(products)} products to {url}...")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Uploaded: {result.get('uploaded_count', 0)}")
            print(f"   Skipped: {result.get('skipped_count', 0)}")
            print(f"   Errors: {result.get('error_count', 0)}")

            if result.get('errors'):
                print(f"   Error details:")
                for error in result['errors'][:5]:  # Show first 5 errors
                    print(f"     - {error}")
                if len(result['errors']) > 5:
                    print(f"     ... and {len(result['errors']) - 5} more")

            return True

        else:
            print(f"❌ Upload failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    csv_file = '../data/sample_products.csv'

    print(f"📖 Reading {csv_file}...")

    try:
        products = csv_to_products(csv_file)
        print(f"📝 Parsed {len(products)} products from CSV")

        if len(products) == 0:
            print("❌ No valid products found in CSV")
            return 1

        # Show first few products as preview
        print(f"📋 Preview of first 3 products:")
        for i, product in enumerate(products[:3], 1):
            print(f"   {i}. {product['name']} ({product['product_type']}) - {product.get('brand', 'No brand')} - ${product.get('price', 'No price')}")

        if len(products) > 3:
            print(f"   ... and {len(products) - 3} more products")

        # Upload to API
        success = upload_products(products)

        return 0 if success else 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())