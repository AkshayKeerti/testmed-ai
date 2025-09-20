"""Main application entry point for TrustMed AI."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.enhanced_gradio_app import EnhancedTrustMedUI

def main():
    """Launch TrustMed AI application."""
    print("🏥 TrustMed AI - Medical Information Assistant")
    print("=" * 50)
    print("🚀 Starting application...")
    
    # Initialize UI
    ui = EnhancedTrustMedUI()
    interface = ui.create_interface()
    
    print("✅ Application initialized successfully")
    print("🌐 Launching web interface...")
    print("📱 Access the interface at: http://localhost:7860")
    print("⚠️  Remember: This is for educational purposes only!")
    print("=" * 50)
    
    # Launch interface
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()
