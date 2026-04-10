import sqlite3
import json
import os
import sys

# Add app to path to import db_handler if needed, or just define paths here
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "automotive.db")

def create_tables(conn):
    cursor = conn.cursor()
    
    # Vehicles table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        model TEXT PRIMARY KEY,
        type TEXT,
        engine TEXT,
        seats INTEGER,
        towing_capacity TEXT,
        cargo_space TEXT,
        description TEXT,
        safety_features TEXT,
        tech_features TEXT
    )
    ''')
    
    # Maintenance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        type TEXT,
        frequency TEXT,
        details TEXT,
        applicable_models TEXT
    )
    ''')
    
    # Manuals table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS manuals (
        topic TEXT PRIMARY KEY,
        content TEXT,
        category TEXT
    )
    ''')

    # Query Cache table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS query_cache (
        query_text TEXT PRIMARY KEY,
        response_json TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()

def migrate_data(conn):
    cursor = conn.cursor()
    
    # 1. Migrate Vehicles
    vehicles_path = os.path.join(DATA_DIR, "vehicles.json")
    if os.path.exists(vehicles_path):
        with open(vehicles_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                cursor.execute('''
                INSERT OR REPLACE INTO vehicles 
                (model, type, engine, seats, towing_capacity, cargo_space, description, safety_features, tech_features)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('model'), 
                    item.get('type'), 
                    item.get('engine'), 
                    item.get('seats'), 
                    item.get('towing_capacity'), 
                    item.get('cargo_space'), 
                    item.get('description'), 
                    json.dumps(item.get('safety_features', [])), 
                    json.dumps(item.get('tech_features', []))
                ))
        print(f"Migrated vehicles from {vehicles_path}")

    # 2. Migrate Maintenance
    maintenance_path = os.path.join(DATA_DIR, "maintenance.json")
    if os.path.exists(maintenance_path):
        with open(maintenance_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                title = item.get('service') or item.get('warranty')
                item_type = 'service' if 'service' in item else 'warranty'
                cursor.execute('''
                INSERT INTO maintenance 
                (title, type, frequency, details, applicable_models)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    title,
                    item_type,
                    item.get('frequency', 'N/A'),
                    item.get('details'),
                    json.dumps(item.get('applicable_models', []))
                ))
        print(f"Migrated maintenance from {maintenance_path}")

    # 3. Migrate Manuals
    manuals_path = os.path.join(DATA_DIR, "manuals.json")
    if os.path.exists(manuals_path):
        with open(manuals_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                cursor.execute('''
                INSERT OR REPLACE INTO manuals (topic, content, category)
                VALUES (?, ?, ?)
                ''', (
                    item.get('topic'),
                    item.get('content'),
                    item.get('category')
                ))
        print(f"Migrated manuals from {manuals_path}")

    conn.commit()

def main():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    try:
        create_tables(conn)
        migrate_data(conn)
        print(f"Database successfully initialized at {DB_PATH}")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
