import sqlite3
import os
import json
from typing import List, Dict, Any
from datetime import datetime

# Place the database in the outputs folder to ensure it doesn't clutter the root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "visionlytics.db")

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the analysis_history table
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

def save_analysis_record(source_type: str, features: Dict[str, Any], density_label: str, confidence: float):
    """Save a single analysis record to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Remove large arrays if any, just keep basic stats for JSON
    features_subset = {
        "top_region_count": features.get("top_region_count", 0),
        "middle_region_count": features.get("middle_region_count", 0),
        "bottom_region_count": features.get("bottom_region_count", 0),
        "avg_distance": features.get("avg_distance", 0.0),
        "min_distance": features.get("min_distance", 0.0)
    }
    
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

def get_recent_history(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve the most recent analysis records."""
    if not os.path.exists(DB_PATH):
        return []
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM analysis_history 
        ORDER BY timestamp DESC LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        record = dict(row)
        if record.get('features_json'):
            record['features'] = json.loads(record['features_json'])
        result.append(record)
        
    return result
