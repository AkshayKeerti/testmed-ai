"""Chat session management for TrustMed AI."""

from typing import List, Dict, Any
from datetime import datetime
import json

class ChatManager:
    """Manage chat sessions and conversation history."""
    
    def __init__(self):
        self.sessions = {}
        self.current_session_id = None
    
    def create_session(self) -> str:
        """Create a new chat session."""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.sessions[session_id] = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'topics': set(),
            'total_queries': 0,
            'confidence_scores': []
        }
        
        self.current_session_id = session_id
        return session_id
    
    def add_message(self, session_id: str, user_message: str, bot_response: Dict[str, Any]) -> None:
        """Add message to session."""
        if session_id not in self.sessions:
            return
        
        message = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response,
            'confidence': bot_response.get('confidence_score', 0.0)
        }
        
        self.sessions[session_id]['messages'].append(message)
        self.sessions[session_id]['total_queries'] += 1
        self.sessions[session_id]['confidence_scores'].append(message['confidence'])
        
        # Extract topics
        topics = self._extract_topics(user_message)
        self.sessions[session_id]['topics'].update(topics)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get session summary."""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        confidence_scores = session['confidence_scores']
        
        return {
            'session_id': session_id,
            'created_at': session['created_at'],
            'total_queries': session['total_queries'],
            'topics': list(session['topics']),
            'avg_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
            'total_sources': sum(len(msg['bot_response'].get('citations', [])) for msg in session['messages'])
        }
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for session."""
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id]['messages']
    
    def _extract_topics(self, message: str) -> List[str]:
        """Extract medical topics from message."""
        topics = []
        message_lower = message.lower()
        
        medical_conditions = [
            'diabetes', 'hypertension', 'cancer', 'heart disease', 'stroke',
            'depression', 'anxiety', 'arthritis', 'asthma', 'migraine'
        ]
        
        for condition in medical_conditions:
            if condition in message_lower:
                topics.append(condition.title())
        
        return topics
    
    def export_session(self, session_id: str) -> str:
        """Export session to JSON."""
        if session_id not in self.sessions:
            return ""
        
        session_data = {
            'session_summary': self.get_session_summary(session_id),
            'conversation_history': self.get_conversation_history(session_id)
        }
        
        return json.dumps(session_data, indent=2)
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all session summaries."""
        return [self.get_session_summary(session_id) for session_id in self.sessions.keys()]

def main():
    """Test chat manager."""
    manager = ChatManager()
    
    # Create session
    session_id = manager.create_session()
    print(f"✅ Created session: {session_id}")
    
    # Add messages
    test_response = {
        'answer': 'Common symptoms include thirst and frequent urination.',
        'confidence_score': 0.8,
        'citations': [{'source': 'Mayo Clinic', 'title': 'Diabetes Overview'}]
    }
    
    manager.add_message(session_id, "What are the symptoms of diabetes?", test_response)
    manager.add_message(session_id, "What causes diabetes?", test_response)
    
    # Get summary
    summary = manager.get_session_summary(session_id)
    print(f"✅ Session summary: {summary}")
    
    # Export session
    export_data = manager.export_session(session_id)
    print(f"✅ Exported session data: {len(export_data)} characters")

if __name__ == "__main__":
    main()
