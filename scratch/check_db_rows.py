import sqlite3
import os

DB_PATH = "data/automotive.db"

def check():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ["vehicles", "maintenance", "manuals"]
    for table in tables:
        cursor.execute(f"SELECT count(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Table {table}: {count} rows")
        
    conn.close()

if __name__ == "__main__":
    check()
