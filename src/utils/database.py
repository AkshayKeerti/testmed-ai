"""Database models and operations."""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.utils.config import DATABASE_URL
import logging
logger = logging.getLogger(__name__)

Base = declarative_base()

class MedicalEntry(Base):
    """Medical information entry."""
    __tablename__ = 'medical_entries'
    
    id = Column(Integer, primary_key=True)
    condition = Column(String(255))
    title = Column(String(500))
    symptoms = Column(JSON)
    causes = Column(JSON)
    treatments = Column(JSON)
    drugs = Column(JSON)
    side_effects = Column(JSON)
    content = Column(Text)
    source = Column(String(100))
    source_type = Column(String(50))
    url = Column(String(500))
    confidence_score = Column(Float)
    date_added = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<MedicalEntry(id={self.id}, condition='{self.condition}', source='{self.source}')>"

class DatabaseManager:
    """Database operations manager."""
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_entry(self, data: dict) -> MedicalEntry:
        """Add a new medical entry."""
        entry = MedicalEntry(**data)
        self.session.add(entry)
        self.session.commit()
        logger.debug(f"Added medical entry: {entry.condition}")
        return entry
    
    def get_entries_by_condition(self, condition: str) -> list:
        """Get entries by condition."""
        return self.session.query(MedicalEntry).filter(
            MedicalEntry.condition.ilike(f'%{condition}%')
        ).all()
    
    def get_entries_by_source(self, source: str) -> list:
        """Get entries by source."""
        return self.session.query(MedicalEntry).filter(
            MedicalEntry.source == source
        ).all()
    
    def get_all_entries(self, limit: int = 100) -> list:
        """Get all entries."""
        return self.session.query(MedicalEntry).limit(limit).all()
    
    def search_entries(self, query: str) -> list:
        """Search entries by text."""
        return self.session.query(MedicalEntry).filter(
            MedicalEntry.content.ilike(f'%{query}%')
        ).all()
    
    def close(self):
        """Close database session."""
        self.session.close()

def main():
    """Test database operations."""
    db = DatabaseManager()
    
    # Test adding entry
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
    entry = db.add_entry(test_data)
    print(f"✅ Added entry: {entry}")
    
    # Test retrieval
    entries = db.get_entries_by_condition('Diabetes')
    print(f"✅ Found {len(entries)} entries for Diabetes")
    
    db.close()

if __name__ == "__main__":
    main()
