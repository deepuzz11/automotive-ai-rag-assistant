import sqlite3
import os
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def fetch_all_vehicles(self):
        """Fetches all vehicle records for indexing and recommendation."""
        query = "SELECT * FROM vehicles"
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                # Convert rows to list of dicts and parse JSON fields
                vehicles = []
                for row in rows:
                    v = dict(row)
                    v['safety_features'] = json.loads(v['safety_features'])
                    v['tech_features'] = json.loads(v['tech_features'])
                    vehicles.append(v)
                return vehicles
        except sqlite3.Error as e:
            logger.error(f"Database error fetching vehicles: {e}")
            return []

    def fetch_all_maintenance(self):
        """Fetches all maintenance and warranty records."""
        query = "SELECT * FROM maintenance"
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                maintenance = []
                for row in rows:
                    m = dict(row)
                    m['applicable_models'] = json.loads(m['applicable_models'])
                    maintenance.append(m)
                return maintenance
        except sqlite3.Error as e:
            logger.error(f"Database error fetching maintenance: {e}")
            return []

    def fetch_all_manuals(self):
        """Fetches all manual topics/content."""
        query = "SELECT * FROM manuals"
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database error fetching manuals: {e}")
            return []

# Singleton instance for the app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "automotive.db")
db_handler = DatabaseHandler(DB_PATH)
