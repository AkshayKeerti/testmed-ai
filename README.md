# TrustMed AI - Medical Information Assistant

A conversational agent that pulls updates from trusted medical sources, organizes medical information into structured guides, supports natural-language queries, cites authoritative references, and enhances discussion by blending evidence-based insights with community perspectives.

## ⚠️ Important Disclaimer

**This is an educational project for learning purposes only.** The information provided should not be considered as medical advice. Always consult with a licensed healthcare professional for medical concerns, diagnosis, or treatment decisions.

## 🚀 Features

- **Conversational Interface**: Natural language queries about medical conditions
- **Evidence-Based Responses**: Information from Mayo Clinic, WebMD, Medical Journals
- **Community Insights**: Integration with Reddit medical discussions
- **Source Citations**: Transparent attribution of all information sources
- **Confidence Scoring**: Quality assessment for each response
- **Session Management**: Track conversation history and topics

## 📋 Requirements

- Python 3.9+
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AkshayKeerti/testmed-ai.git
   cd testmed-ai
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. **Set up environment variables** (optional)
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys if needed
   ```

## 🏃‍♂️ Running the Application

**Launch the web interface:**
```bash
python app.py
```

Access the interface at: http://localhost:7860

## 🧪 Testing Components

**Test data ingestion:**
```bash
python test_ingestion.py
```

**Test individual components:**
```bash
python src/rag/rag_pipeline.py
python src/ui/chat_manager.py
```

## 📁 Project Structure

```
trustmed-ai/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── src/
│   ├── ingestion/                  # Data sources
│   │   ├── pubmed_client.py       # PubMed API client
│   │   ├── mayo_scraper.py        # Mayo Clinic scraper
│   │   ├── webmd_scraper.py       # WebMD scraper
│   │   ├── reddit_scraper.py      # Reddit scraper
│   │   └── scraper_base.py        # Base scraper class
│   ├── processing/                 # Data processing
│   │   ├── database.py            # SQLite database
│   │   ├── vector_store.py         # Chroma vector database
│   │   ├── data_cleaner.py        # Data cleaning
│   │   └── data_pipeline.py       # End-to-end pipeline
│   ├── rag/                       # RAG system
│   │   ├── query_processor.py     # Query processing
│   │   ├── context_retriever.py   # Context retrieval
│   │   ├── answer_generator.py    # Answer generation
│   │   ├── hybrid_search.py       # Hybrid search
│   │   └── rag_pipeline.py        # Complete RAG pipeline
│   ├── ui/                        # User interface
│   │   ├── gradio_app.py          # Basic Gradio UI
│   │   ├── enhanced_gradio_app.py # Enhanced UI with sessions
│   │   └── chat_manager.py        # Session management
│   └── utils/                     # Utilities
│       ├── config.py              # Configuration
│       └── logging.py             # Logging setup
└── test_ingestion.py              # Test script
```

## 🔧 Configuration

Edit `src/utils/config.py` to customize:
- Medical journals to track
- Reddit subreddits to monitor
- Scraping delays and limits
- Model configurations

## 📊 Data Sources

- **Evidence-Based**: Mayo Clinic, WebMD, PubMed (JAMA, NEJM, BMJ)
- **Community**: Reddit medical subreddits (AskDocs, r/medical)
- **Processing**: Data cleaning, validation, and structured storage

## 🎯 Usage Examples

**Ask about symptoms:**
- "What are the symptoms of diabetes?"
- "What causes high blood pressure?"

**Ask about treatments:**
- "How do you treat migraines?"
- "What medications are used for depression?"

**General medical questions:**
- "Tell me about heart disease"
- "What is asthma?"

## 🚧 Development Status

- ✅ **Phase A**: Data ingestion from all sources
- ✅ **Phase B**: Data processing and storage
- ✅ **Phase C**: RAG and conversational agent
- ✅ **Phase D**: UI and system integration

**Project Status**: 100% Complete - Fully functional conversational medical agent

## 🤝 Contributing

This is an educational project. Feel free to:
- Report issues
- Suggest improvements
- Fork for learning purposes

## 📄 License

This project is for educational purposes only. Please respect the terms of service of all data sources used.

## 🙏 Acknowledgments

- Medical data sources: Mayo Clinic, WebMD, PubMed
- Community insights: Reddit medical communities
- Open source libraries: Gradio, Transformers, Chroma, Playwright
