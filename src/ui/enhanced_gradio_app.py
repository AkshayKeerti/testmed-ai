"""Enhanced Gradio UI with session management."""

import gradio as gr
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.rag_pipeline import RAGPipeline
from src.ui.chat_manager import ChatManager
from typing import List, Tuple, Dict, Any

class EnhancedTrustMedUI:
    """Enhanced Gradio UI with session management."""
    
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.chat_manager = ChatManager()
        self.current_session = None
    
    def start_new_session(self) -> Tuple[str, List, str, str, str]:
        """Start a new chat session."""
        session_id = self.chat_manager.create_session()
        self.current_session = session_id
        
        return f"New session started: {session_id}", [], "", "", session_id
    
    def chat_with_agent(self, message: str, history: List[List[str]], session_id: str) -> Tuple[str, List[List[str]], str, str, str]:
        """Process user message and return response."""
        if not message.strip():
            return "", history, "", "", session_id
        
        if not session_id:
            session_id = self.start_new_session()[4]
        
        # Process query through RAG pipeline
        response = self.rag_pipeline.process_query(message)
        
        # Add to chat manager
        self.chat_manager.add_message(session_id, message, response)
        
        # Update chat history - use simple tuple format
        history.append([message, response['answer']])
        
        # Create sources display
        sources_text = self._format_sources(response['citations'])
        
        # Create confidence display
        confidence_text = f"Confidence: {response['confidence_score']:.2f}"
        
        # Get session info
        session_info = self._get_session_info(session_id)
        
        return "", history, sources_text, confidence_text, session_info
    
    def _format_sources(self, citations: List[Dict[str, str]]) -> str:
        """Format citations for display."""
        if not citations:
            return "No sources available"
        
        sources_text = "**Sources:**\n\n"
        
        for i, citation in enumerate(citations, 1):
            sources_text += f"{i}. **{citation['type']}** - {citation['source']}\n"
            sources_text += f"   Title: {citation['title']}\n"
            sources_text += f"   URL: {citation['url']}\n"
            sources_text += f"   Confidence: {citation['confidence']:.2f}\n\n"
        
        return sources_text
    
    def _get_session_info(self, session_id: str) -> str:
        """Get session information."""
        if not session_id:
            return "No active session"
        
        summary = self.chat_manager.get_session_summary(session_id)
        
        info = f"""
        **Session Info:**
        - ID: {summary.get('session_id', 'Unknown')}
        - Queries: {summary.get('total_queries', 0)}
        - Topics: {', '.join(summary.get('topics', []))}
        - Avg Confidence: {summary.get('avg_confidence', 0.0):.2f}
        - Sources Used: {summary.get('total_sources', 0)}
        """
        
        return info
    
    def clear_chat(self, session_id: str) -> Tuple[str, List, str, str, str]:
        """Clear chat history."""
        if session_id:
            session_id = self.start_new_session()[4]
        
        return "", [], "", "", session_id
    
    def get_disclaimer(self) -> str:
        """Get medical disclaimer."""
        return """
        **⚠️ Medical Disclaimer**
        
        This is an educational project for learning purposes. The information provided should not be considered as medical advice. Always consult with a licensed healthcare professional for medical concerns, diagnosis, or treatment decisions.
        
        **Data Sources:**
        - Evidence-based: Mayo Clinic, WebMD, Medical Journals
        - Community insights: Reddit medical discussions
        """
    
    def create_interface(self) -> gr.Blocks:
        """Create enhanced Gradio interface."""
        with gr.Blocks(title="TrustMed AI - Medical Information Assistant", theme=gr.themes.Soft()) as interface:
            
            gr.Markdown("# 🏥 TrustMed AI - Medical Information Assistant")
            gr.Markdown("Ask questions about medical conditions, symptoms, causes, and treatments.")
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Session management
                    with gr.Row():
                        new_session_btn = gr.Button("New Session", variant="secondary")
                        session_display = gr.Textbox(label="Current Session", interactive=False)
                    
                    # Chat interface
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        height=400,
                        show_label=True
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            placeholder="Ask about medical conditions, symptoms, treatments...",
                            label="Your Question",
                            lines=2
                        )
                        send_btn = gr.Button("Send", variant="primary")
                    
                    with gr.Row():
                        clear_btn = gr.Button("Clear Chat", variant="secondary")
                
                with gr.Column(scale=1):
                    # Sources panel
                    sources_output = gr.Textbox(
                        label="Sources & Citations",
                        lines=10,
                        interactive=False,
                        show_label=True
                    )
                    
                    # Confidence score
                    confidence_output = gr.Textbox(
                        label="Response Confidence",
                        lines=2,
                        interactive=False,
                        show_label=True
                    )
                    
                    # Session info
                    session_info = gr.Textbox(
                        label="Session Information",
                        lines=6,
                        interactive=False,
                        show_label=True
                    )
                    
                    # Disclaimer
                    disclaimer = gr.Markdown(self.get_disclaimer())
            
            # Event handlers
            new_session_btn.click(
                self.start_new_session,
                outputs=[session_display, chatbot, sources_output, confidence_output, session_info]
            )
            
            send_btn.click(
                self.chat_with_agent,
                inputs=[msg_input, chatbot, session_display],
                outputs=[msg_input, chatbot, sources_output, confidence_output, session_info]
            )
            
            msg_input.submit(
                self.chat_with_agent,
                inputs=[msg_input, chatbot, session_display],
                outputs=[msg_input, chatbot, sources_output, confidence_output, session_info]
            )
            
            clear_btn.click(
                self.clear_chat,
                inputs=[session_display],
                outputs=[session_display, chatbot, sources_output, confidence_output, session_info]
            )
        
        return interface

def main():
    """Launch the enhanced Gradio app."""
    ui = EnhancedTrustMedUI()
    interface = ui.create_interface()
    
    print("🚀 Launching Enhanced TrustMed AI Interface")
    print("=" * 50)
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()
