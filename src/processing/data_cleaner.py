"""Data cleaning and validation for medical information."""

import re
from typing import Dict, List, Any
from src.utils.logging import logger

class DataCleaner:
    """Clean and validate medical data."""
    
    def __init__(self):
        self.medical_terms = {
            'symptoms': ['pain', 'fever', 'nausea', 'fatigue', 'headache', 'dizziness'],
            'treatments': ['medication', 'therapy', 'surgery', 'exercise', 'diet'],
            'drugs': ['aspirin', 'ibuprofen', 'metformin', 'insulin', 'penicillin']
        }
    
    def clean_medical_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate medical data."""
        cleaned_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                cleaned_data[key] = self._clean_text(value)
            elif isinstance(value, list):
                cleaned_data[key] = self._clean_list(value)
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def _clean_text(self, text: str) -> str:
        """Clean individual text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'\[.*?\]',  # Remove brackets
            r'\(.*?\)',  # Remove parentheses
            r'<.*?>',     # Remove HTML tags
            r'http[s]?://\S+',  # Remove URLs
        ]
        
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text)
        
        return text.strip()
    
    def _clean_list(self, items: List[str]) -> List[str]:
        """Clean list of items."""
        cleaned_items = []
        
        for item in items:
            if isinstance(item, str):
                cleaned_item = self._clean_text(item)
                if cleaned_item and len(cleaned_item) > 3:  # Skip very short items
                    cleaned_items.append(cleaned_item)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in cleaned_items:
            if item.lower() not in seen:
                seen.add(item.lower())
                unique_items.append(item)
        
        return unique_items
    
    def validate_medical_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate medical content quality."""
        validation_results = {
            'is_valid': True,
            'issues': [],
            'confidence_score': 0.0
        }
        
        # Check required fields
        required_fields = ['title', 'source', 'url']
        for field in required_fields:
            if not data.get(field):
                validation_results['issues'].append(f"Missing required field: {field}")
                validation_results['is_valid'] = False
        
        # Check content quality
        if data.get('symptoms'):
            validation_results['confidence_score'] += 0.3
        if data.get('causes'):
            validation_results['confidence_score'] += 0.2
        if data.get('treatments'):
            validation_results['confidence_score'] += 0.3
        if data.get('content'):
            validation_results['confidence_score'] += 0.2
        
        # Check source credibility
        credible_sources = ['Mayo Clinic', 'WebMD', 'JAMA', 'NEJM', 'BMJ']
        if data.get('source') in credible_sources:
            validation_results['confidence_score'] += 0.2
        
        validation_results['confidence_score'] = min(validation_results['confidence_score'], 1.0)
        
        return validation_results
    
    def deduplicate_data(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entries."""
        seen_urls = set()
        unique_data = []
        
        for data in data_list:
            url = data.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_data.append(data)
        
        logger.info(f"Deduplicated {len(data_list)} items to {len(unique_data)} unique items")
        return unique_data

def main():
    """Test the data cleaner."""
    cleaner = DataCleaner()
    
    # Test data cleaning
    test_data = {
        'title': 'Diabetes   [Updated]',
        'symptoms': ['Feeling thirsty', 'Frequent urination', 'Feeling thirsty'],  # Duplicate
        'causes': ['Unknown cause (more research needed)'],
        'treatments': ['Medication', 'Diet changes', 'Exercise'],
        'content': 'Diabetes is a chronic condition...'
    }
    
    print("Testing data cleaning...")
    cleaned_data = cleaner.clean_medical_data(test_data)
    
    print(f"Original symptoms: {test_data['symptoms']}")
    print(f"Cleaned symptoms: {cleaned_data['symptoms']}")
    
    # Test validation
    validation = cleaner.validate_medical_content(cleaned_data)
    print(f"Validation: {validation}")

if __name__ == "__main__":
    main()
