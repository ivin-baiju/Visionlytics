import json
import os
import sqlite3
import datetime
import logging
from typing import Any, Dict

import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

# Fallback SQLite config
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "visionlytics_fallback.db")

class DatabaseClient:
    def __init__(self):
        self.use_firebase = False
        self.db = None
        self._init_connection()

    def _init_connection(self):
        # Attempt to load Firebase credentials
        # We look in the root folder (two levels up from backend/db)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cred_path = os.path.join(root_dir, "firebase-adminsdk.json")

        if os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.use_firebase = True
                logger.info("Successfully connected to Firebase Firestore.")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
                self._init_sqlite()
        else:
            logger.warning(f"Firebase credentials not found at {cred_path}. Falling back to SQLite.")
            self._init_sqlite()

    def _init_sqlite(self):
        """Fallback to local SQLite if Firebase isn't configured."""
        self.use_firebase = False
        conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_type TEXT NOT NULL,
                people_count INTEGER NOT NULL,
                density_label TEXT NOT NULL,
                occupancy_ratio REAL NOT NULL,
                confidence REAL NOT NULL,
                features_json TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_analysis(self, source_type: str, features: Dict[str, Any], density_label: str, confidence: float):
        features_subset = {
            "top_region_count": features.get("top_region_count", 0),
            "middle_region_count": features.get("middle_region_count", 0),
            "bottom_region_count": features.get("bottom_region_count", 0),
        }
        
        if self.use_firebase:
            try:
                doc_ref = self.db.collection('analysis_history').document()
                doc_ref.set({
                    'timestamp': firestore.SERVER_TIMESTAMP,
                    'source_type': source_type,
                    'people_count': int(features.get("people_count", 0)),
                    'density_label': density_label,
                    'occupancy_ratio': float(features.get("occupancy_ratio", 0.0)),
                    'confidence': float(confidence),
                    'features': features_subset
                })
            except Exception as e:
                logger.error(f"Failed to save to Firebase: {e}")
        else:
            conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_history 
                (source_type, people_count, density_label, occupancy_ratio, confidence, features_json)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                source_type,
                int(features.get("people_count", 0)),
                density_label,
                float(features.get("occupancy_ratio", 0.0)),
                float(confidence),
                json.dumps(features_subset)
            ))
            conn.commit()
            conn.close()

    def get_recent(self, limit: int = 100) -> list[Dict[str, Any]]:
        if self.use_firebase:
            try:
                docs = self.db.collection('analysis_history').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
                results = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    if 'timestamp' in data and data['timestamp']:
                        # Convert Firestore timestamp to ISO string
                        data['timestamp'] = data['timestamp'].isoformat()
                    results.append(data)
                return results
            except Exception as e:
                logger.error(f"Failed to fetch from Firebase: {e}")
                return []
        else:
            if not os.path.exists(DB_PATH):
                return []
            conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM analysis_history ORDER BY timestamp DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            conn.close()
            
            result = []
            for row in rows:
                record = dict(row)
                if record.get('features_json'):
                    record['features'] = json.loads(record['features_json'])
                result.append(record)
            return result

db_client = DatabaseClient()
