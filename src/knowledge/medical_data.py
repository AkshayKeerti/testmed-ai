"""
Medical Knowledge Base for TrustMed AI
Curated medical information from trusted sources
"""

from typing import List, Dict, Any
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class MedicalKnowledgeBase:
    """Medical knowledge base with curated information"""
    
    def __init__(self):
        self.medical_data = self._load_medical_data()
        logger.info(f"Loaded {len(self.medical_data)} medical entries")
    
    def _load_medical_data(self) -> List[Dict[str, Any]]:
        """Load curated medical data"""
        return [
            {
                "condition": "diabetes",
                "title": "Diabetes Overview",
                "content": "Diabetes is a chronic health condition that affects how your body turns food into energy. There are three main types: Type 1, Type 2, and gestational diabetes. Type 1 diabetes is an autoimmune condition where the body attacks insulin-producing cells. Type 2 diabetes occurs when the body becomes resistant to insulin or doesn't produce enough. Gestational diabetes develops during pregnancy.",
                "symptoms": ["increased thirst", "frequent urination", "fatigue", "blurred vision", "slow healing wounds", "tingling in hands/feet"],
                "causes": ["genetic factors", "obesity", "physical inactivity", "age", "family history"],
                "treatments": ["insulin therapy", "oral medications", "diet management", "exercise", "blood sugar monitoring"],
                "sources": ["American Diabetes Association", "Mayo Clinic", "CDC"]
            },
            {
                "condition": "hypertension",
                "title": "High Blood Pressure (Hypertension)",
                "content": "Hypertension is a condition where the force of blood against artery walls is consistently too high. It's often called the 'silent killer' because it typically has no symptoms until it causes serious health problems. Normal blood pressure is less than 120/80 mmHg. Stage 1 hypertension is 130-139/80-89 mmHg, and Stage 2 is 140/90 mmHg or higher.",
                "symptoms": ["headaches", "shortness of breath", "nosebleeds", "dizziness", "chest pain"],
                "causes": ["age", "family history", "obesity", "lack of exercise", "high sodium diet", "stress"],
                "treatments": ["ACE inhibitors", "diuretics", "beta-blockers", "lifestyle changes", "diet modification"],
                "sources": ["American Heart Association", "Mayo Clinic", "WHO"]
            },
            {
                "condition": "asthma",
                "title": "Asthma",
                "content": "Asthma is a chronic respiratory condition that causes inflammation and narrowing of the airways, making breathing difficult. It affects people of all ages but often starts in childhood. Symptoms can range from mild to severe and may be triggered by various factors including allergens, exercise, cold air, or respiratory infections.",
                "symptoms": ["wheezing", "shortness of breath", "chest tightness", "coughing", "difficulty breathing"],
                "causes": ["genetic factors", "allergies", "respiratory infections", "environmental factors", "exercise"],
                "treatments": ["inhalers", "bronchodilators", "corticosteroids", "avoiding triggers", "action plan"],
                "sources": ["American Lung Association", "Mayo Clinic", "CDC"]
            },
            {
                "condition": "depression",
                "title": "Depression",
                "content": "Depression is a common and serious mood disorder that affects how you feel, think, and handle daily activities. It's more than just feeling sad or going through a rough patch. Depression can cause persistent feelings of sadness, hopelessness, and loss of interest in activities. It can affect sleep, appetite, energy levels, and concentration.",
                "symptoms": ["persistent sadness", "loss of interest", "fatigue", "sleep problems", "appetite changes", "difficulty concentrating"],
                "causes": ["genetic factors", "brain chemistry", "life events", "medical conditions", "medications"],
                "treatments": ["therapy", "medications", "lifestyle changes", "support groups", "exercise"],
                "sources": ["National Institute of Mental Health", "Mayo Clinic", "WHO"]
            },
            {
                "condition": "heart_disease",
                "title": "Heart Disease",
                "content": "Heart disease refers to several types of heart conditions, with coronary artery disease being the most common. It occurs when plaque builds up in the coronary arteries, reducing blood flow to the heart. This can lead to chest pain (angina), heart attacks, and other serious complications. Risk factors include high blood pressure, high cholesterol, smoking, diabetes, and family history.",
                "symptoms": ["chest pain", "shortness of breath", "fatigue", "irregular heartbeat", "swelling in legs"],
                "causes": ["high blood pressure", "high cholesterol", "smoking", "diabetes", "obesity", "family history"],
                "treatments": ["medications", "lifestyle changes", "surgery", "stents", "bypass surgery"],
                "sources": ["American Heart Association", "Mayo Clinic", "CDC"]
            }
        ]
    
    def get_condition_info(self, condition: str) -> Dict[str, Any]:
        """Get information about a specific condition"""
        for entry in self.medical_data:
            if entry["condition"] == condition.lower():
                return entry
        return {}
    
    def search_conditions(self, query: str) -> List[Dict[str, Any]]:
        """Search for conditions matching query"""
        query_lower = query.lower()
        results = []
        
        for entry in self.medical_data:
            if (query_lower in entry["condition"] or 
                query_lower in entry["title"].lower() or
                any(query_lower in symptom.lower() for symptom in entry["symptoms"]) or
                any(query_lower in cause.lower() for cause in entry["causes"])):
                results.append(entry)
        
        return results
    
    def get_all_conditions(self) -> List[str]:
        """Get list of all available conditions"""
        return [entry["condition"] for entry in self.medical_data]
    
    def to_documents(self) -> List[Document]:
        """Convert medical data to Langchain documents"""
        documents = []
        
        for entry in self.medical_data:
            # Create comprehensive document
            content = f"""
Title: {entry['title']}
Condition: {entry['condition']}

Overview:
{entry['content']}

Symptoms:
{', '.join(entry['symptoms'])}

Causes:
{', '.join(entry['causes'])}

Treatments:
{', '.join(entry['treatments'])}

Sources: {', '.join(entry['sources'])}
            """.strip()
            
            doc = Document(
                page_content=content,
                metadata={
                    "condition": entry["condition"],
                    "title": entry["title"],
                    "sources": entry["sources"],
                    "type": "medical_condition"
                }
            )
            documents.append(doc)
        
        return documents

# Test the knowledge base
if __name__ == "__main__":
    kb = MedicalKnowledgeBase()
    
    print("Available conditions:")
    for condition in kb.get_all_conditions():
        print(f"- {condition}")
    
    print("\nSearching for 'diabetes':")
    results = kb.search_conditions("diabetes")
    for result in results:
        print(f"- {result['title']}")
    
    print(f"\nTotal documents: {len(kb.to_documents())}")
