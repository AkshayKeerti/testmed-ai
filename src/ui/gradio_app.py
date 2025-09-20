"""Gradio UI for TrustMed AI conversational agent."""

import gradio as gr
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.rag_pipeline import RAGPipeline
from typing import List, Tuple, Dict, Any

class TrustMedUI:
    """Gradio UI for TrustMed AI."""
    
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.chat_history = []
    
    def chat_with_agent(self, message: str, history: List[List[str]]) -> Tuple[str, List[List[str]], str, str]:
        """Process user message and return response."""
        if not message.strip():
            return "", history, "", ""
        
        # Process query through RAG pipeline
        response = self.rag_pipeline.process_query(message)
        
        # Update chat history
        history.append([message, response['answer']])
        
        # Create sources display
        sources_text = self._format_sources(response['citations'])
        
        # Create confidence display
        confidence_text = f"Confidence: {response['confidence_score']:.2f}"
        
        return "", history, sources_text, confidence_text
    
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
    
    def clear_chat(self) -> Tuple[str, List, str, str]:
        """Clear chat history."""
        self.chat_history = []
        return "", [], "", ""
    
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
        """Create Gradio interface."""
        with gr.Blocks(title="TrustMed AI - Medical Information Assistant", theme=gr.themes.Soft()) as interface:
            
            gr.Markdown("# 🏥 TrustMed AI - Medical Information Assistant")
            gr.Markdown("Ask questions about medical conditions, symptoms, causes, and treatments.")
            
            with gr.Row():
                with gr.Column(scale=2):
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
                        lines=15,
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
                    
                    # Disclaimer
                    disclaimer = gr.Markdown(self.get_disclaimer())
            
            # Event handlers
            send_btn.click(
                self.chat_with_agent,
                inputs=[msg_input, chatbot],
                outputs=[msg_input, chatbot, sources_output, confidence_output]
            )
            
            msg_input.submit(
                self.chat_with_agent,
                inputs=[msg_input, chatbot],
                outputs=[msg_input, chatbot, sources_output, confidence_output]
            )
            
            clear_btn.click(
                self.clear_chat,
                outputs=[msg_input, chatbot, sources_output, confidence_output]
            )
        
        return interface

def main():
    """Launch the Gradio app."""
    ui = TrustMedUI()
    interface = ui.create_interface()
    
    print("🚀 Launching TrustMed AI Interface")
    print("=" * 40)
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()
