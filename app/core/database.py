import sqlite3
import os
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cache = {} # In-memory cache for data
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def fetch_all_vehicles(self):
        """Fetches all vehicle records with in-memory caching."""
        if 'vehicles' in self._cache:
            return self._cache['vehicles']
            
        query = "SELECT * FROM vehicles"
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                vehicles = []
                for row in rows:
                    v = dict(row)
                    v['safety_features'] = json.loads(v['safety_features'])
                    v['tech_features'] = json.loads(v['tech_features'])
                    vehicles.append(v)
                self._cache['vehicles'] = vehicles
                return vehicles
        except sqlite3.Error as e:
            logger.error(f"Database error fetching vehicles: {e}")
            return []

    def fetch_all_maintenance(self):
        """Fetches all maintenance records with in-memory caching."""
        if 'maintenance' in self._cache:
            return self._cache['maintenance']
            
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
                self._cache['maintenance'] = maintenance
                return maintenance
        except sqlite3.Error as e:
            logger.error(f"Database error fetching maintenance: {e}")
            return []

    def fetch_all_manuals(self):
        """Fetches all manual records with in-memory caching."""
        if 'manuals' in self._cache:
            return self._cache['manuals']
            
        query = "SELECT * FROM manuals"
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                manuals = [dict(row) for row in rows]
                self._cache['manuals'] = manuals
                return manuals
        except sqlite3.Error as e:
            logger.error(f"Database error fetching manuals: {e}")
            return []

    def get_cached_query(self, query_text: str):
        """Retrieves a cached response for a given query text."""
        query = "SELECT response_json FROM query_cache WHERE query_text = ?"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (query_text.strip().lower(),))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
        except sqlite3.Error as e:
            logger.error(f"Database error fetching cache: {e}")
            return None

    def set_cached_query(self, query_text: str, response_dict: dict):
        """Stores a response in the cache."""
        query = "INSERT OR REPLACE INTO query_cache (query_text, response_json) VALUES (?, ?)"
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (query_text.strip().lower(), json.dumps(response_dict)))
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database error setting cache: {e}")

# Singleton instance for the app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "automotive.db")
db_handler = DatabaseHandler(DB_PATH)
