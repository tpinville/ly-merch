#!/usr/bin/env python3
"""
Simple data import script using pymysql (pure Python MySQL client)
"""

import json
import re
import sys

# Pure Python MySQL client - no external dependencies
class MySQLClient:
    def __init__(self, host, port, user, password, database):
        import socket
        import struct
        import hashlib

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.socket = None

    def connect(self):
        print("Note: This is a simplified version. Please install mysql-connector-python for full functionality.")
        print("Run: pip3 install mysql-connector-python --user")
        print("Then run the full import_data.py script")
        return False

def parse_json_file(filepath):
    """Parse the alls.json file with multiple JSON objects"""
    print(f"📖 Reading {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by '}{'
    json_objects_raw = re.split(r'}\s*{', content)
    print(f"Found {len(json_objects_raw)} JSON objects")

    # Fix split objects
    if len(json_objects_raw) == 1:
        return [json.loads(content)]

    json_objects_raw[0] += '}'
    for i in range(1, len(json_objects_raw)-1):
        json_objects_raw[i] = '{' + json_objects_raw[i] + '}'
    json_objects_raw[-1] = '{' + json_objects_raw[-1]

    # Parse each object
    parsed_objects = []
    for i, obj_str in enumerate(json_objects_raw):
        try:
            obj = json.loads(obj_str)
            parsed_objects.append(obj)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON object {i+1}: {e}")

    print(f"✅ Successfully parsed {len(parsed_objects)} JSON objects")
    return parsed_objects

def generate_sql(json_objects):
    """Generate SQL statements from parsed JSON"""
    statements = []

    # Clear existing data
    statements.extend([
        "SET FOREIGN_KEY_CHECKS = 0;",
        "TRUNCATE TABLE trend_images;",
        "TRUNCATE TABLE trends;",
        "TRUNCATE TABLE verticals;",
        "DELETE FROM categories WHERE id NOT IN (1,2,3,4,5,6);",  # Keep predefined categories
        "SET FOREIGN_KEY_CHECKS = 1;",
        ""
    ])

    vertical_id_map = {}
    trend_id_map = {}
    category_id_map = {}
    vertical_counter = 1
    trend_counter = 1
    category_counter = 7  # Start after predefined categories

    def get_category_id(category_name):
        if category_name not in category_id_map:
            # Check if it's a predefined category
            predefined = {
                'sneakers': 1, 'sandals': 2, 'dress_shoes': 3,
                'boots': 4, 'flats': 5, 'heels': 6
            }
            if category_name in predefined:
                category_id_map[category_name] = predefined[category_name]
            else:
                category_id_map[category_name] = category_counter
                statements.append(
                    f"INSERT INTO categories (id, name) VALUES ({category_counter}, '{category_name}');"
                )
                nonlocal category_counter
                category_counter += 1
        return category_id_map[category_name]

    for obj in json_objects:
        verticals = obj.get('verticals', [])

        for vertical in verticals:
            # Insert vertical
            vertical_uuid = vertical['vertical_id']
            if vertical_uuid not in vertical_id_map:
                vertical_id_map[vertical_uuid] = vertical_counter
                name_escaped = vertical['name'].replace("'", "\\'")

                # Extract category from vertical_id
                category_name = vertical_uuid.split(':')[0]
                category_id = get_category_id(category_name)

                statements.append(
                    f"INSERT INTO verticals (id, vertical_id, category_id, name, geo_zone) VALUES "
                    f"({vertical_counter}, '{vertical_uuid}', {category_id}, '{name_escaped}', '{vertical['geo_zone']}');"
                )
                vertical_counter += 1

            db_vertical_id = vertical_id_map[vertical_uuid]

            for trend in vertical.get('trends', []):
                # Insert trend
                trend_uuid = trend['trend_id']
                if trend_uuid not in trend_id_map:
                    trend_id_map[trend_uuid] = trend_counter
                    name = trend['name'].replace("'", "\\'")
                    description = trend.get('description', '').replace("'", "\\'").replace('\n', '\\n')
                    image = trend.get('image', '')

                    statements.append(
                        f"INSERT INTO trends (id, trend_id, vertical_id, name, description, image_hash) VALUES "
                        f"({trend_counter}, '{trend_uuid}', {db_vertical_id}, '{name}', '{description}', '{image}');"
                    )

                    # Insert images
                    for img in trend.get('positive_images', []):
                        img_desc = img.get('description', '').replace("'", "\\'")
                        statements.append(
                            f"INSERT INTO trend_images (trend_id, image_type, md5_hash, description) VALUES "
                            f"({trend_counter}, 'positive', '{img['md5']}', '{img_desc}');"
                        )

                    for img in trend.get('negative_images', []):
                        img_desc = img.get('description', '').replace("'", "\\'")
                        statements.append(
                            f"INSERT INTO trend_images (trend_id, image_type, md5_hash, description) VALUES "
                            f"({trend_counter}, 'negative', '{img['md5']}', '{img_desc}');"
                        )

                    trend_counter += 1

    return statements

def main():
    print("🚀 Converting alls.json to SQL statements")

    try:
        # Parse JSON
        json_objects = parse_json_file('alls.json')

        # Generate SQL
        print("📝 Generating SQL statements...")
        sql_statements = generate_sql(json_objects)

        # Write to file
        output_file = 'import_data.sql'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_statements))

        print(f"✅ Generated {len(sql_statements)} SQL statements in {output_file}")
        print(f"📊 Ready to import data!")

        # Show summary
        categories = sum(1 for stmt in sql_statements if 'INSERT INTO categories' in stmt)
        verticals = sum(1 for stmt in sql_statements if 'INSERT INTO verticals' in stmt)
        trends = sum(1 for stmt in sql_statements if 'INSERT INTO trends' in stmt)
        images = sum(1 for stmt in sql_statements if 'INSERT INTO trend_images' in stmt)

        print(f"📈 Summary: {categories} categories, {verticals} verticals, {trends} trends, {images} images")
        print(f"\n🔧 To import the data, run:")
        print(f"   ./run_import.sh")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())