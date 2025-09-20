"""Database models and operations for Phase B."""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class MedicalDatabase:
    """SQLite database for medical information."""
    
    def __init__(self, db_path: str = "trustmed_ai.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition TEXT,
                title TEXT,
                symptoms TEXT,  -- JSON array
                causes TEXT,    -- JSON array
                treatments TEXT, -- JSON array
                drugs TEXT,     -- JSON array
                side_effects TEXT, -- JSON array
                content TEXT,
                source TEXT,
                source_type TEXT,
                url TEXT UNIQUE,
                confidence_score REAL,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_entry(self, data: Dict[str, Any]) -> int:
        """Add medical entry to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert lists to JSON strings
        for key in ['symptoms', 'causes', 'treatments', 'drugs', 'side_effects']:
            if key in data and isinstance(data[key], list):
                data[key] = json.dumps(data[key])
        
        cursor.execute('''
            INSERT OR REPLACE INTO medical_entries 
            (condition, title, symptoms, causes, treatments, drugs, side_effects, 
             content, source, source_type, url, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('condition', ''),
            data.get('title', ''),
            data.get('symptoms', '[]'),
            data.get('causes', '[]'),
            data.get('treatments', '[]'),
            data.get('drugs', '[]'),
            data.get('side_effects', '[]'),
            data.get('content', ''),
            data.get('source', ''),
            data.get('source_type', ''),
            data.get('url', ''),
            data.get('confidence_score', 0.0)
        ))
        
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return entry_id
    
    def get_entries_by_condition(self, condition: str) -> List[Dict]:
        """Get entries by condition."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM medical_entries 
            WHERE condition LIKE ? OR title LIKE ?
        ''', (f'%{condition}%', f'%{condition}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_all_entries(self, limit: int = 100) -> List[Dict]:
        """Get all entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM medical_entries LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def search_entries(self, query: str) -> List[Dict]:
        """Search entries by text."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM medical_entries 
            WHERE content LIKE ? OR title LIKE ? OR condition LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary."""
        columns = ['id', 'condition', 'title', 'symptoms', 'causes', 'treatments', 
                  'drugs', 'side_effects', 'content', 'source', 'source_type', 
                  'url', 'confidence_score', 'date_added']
        
        data = dict(zip(columns, row))
        
        # Convert JSON strings back to lists
        for key in ['symptoms', 'causes', 'treatments', 'drugs', 'side_effects']:
            if data[key]:
                try:
                    data[key] = json.loads(data[key])
                except json.JSONDecodeError:
                    data[key] = []
            else:
                data[key] = []
        
        return data

def main():
    """Test database operations."""
    db = MedicalDatabase()
    
    # Test data
    test_data = {
        'condition': 'Diabetes',
        'title': 'Diabetes Overview',
        'symptoms': ['Thirst', 'Frequent urination'],
        'causes': ['Insulin resistance'],
        'treatments': ['Medication', 'Diet'],
        'drugs': ['Metformin'],
        'side_effects': ['Nausea'],
        'content': 'Diabetes is a chronic condition...',
        'source': 'Mayo Clinic',
        'source_type': 'health_site',
        'url': 'https://example.com/diabetes',
        'confidence_score': 0.8
    }
    
    print("Testing database operations...")
    entry_id = db.add_entry(test_data)
    print(f"✅ Added entry with ID: {entry_id}")
    
    entries = db.get_entries_by_condition('Diabetes')
    print(f"✅ Found {len(entries)} entries for Diabetes")
    
    if entries:
        print(f"   First entry: {entries[0]['title']}")

if __name__ == "__main__":
    main()
