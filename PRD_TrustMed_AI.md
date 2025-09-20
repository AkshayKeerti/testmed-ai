# TrustMed AI - Product Requirements Document (PRD)

## 1. Project Overview

### 1.1 Project Name
TrustMed AI - Conversational Medical Information Agent

### 1.2 Project Type
Educational/Fun Project - Personal Learning Initiative

### 1.3 Core Mission
Create a conversational agent that pulls updates from trusted medical sources, organizes medical information into structured guides, supports natural-language queries, cites authoritative references, and enhances discussion by blending evidence-based insights with community perspectives.

### 1.4 Disclaimer
**IMPORTANT**: This is a fun educational project. Do not take any medical advice seriously. Always consult licensed healthcare professionals for medical concerns.

## 2. Functional Requirements

### 2.1 Core Features

#### 2.1.1 Data Ingestion System
- **Medical Journals**: NEJM, JAMA abstracts via PubMed API
- **Reputable Health Sites**: Mayo Clinic, WebMD disease pages
- **Community Sources**: Reddit (AskDocs, r/medical), HealthBoards, Mayo Connect
- **Medical Ontologies**: UMLS/RxNorm for terminology normalization

#### 2.1.2 Data Processing Pipeline
- **Normalization**: Map symptoms, drugs, side effects using UMLS
- **Structuring**: Convert to standardized JSON schema
- **Indexing**: Dual indexing (structured + semantic search)
- **Storage**: SQLite + Chroma/FAISS vector database

#### 2.1.3 Conversational Agent
- **Natural Language Queries**: Support medical questions in plain English
- **RAG Pipeline**: Retrieve relevant structured guides and community discussions
- **Answer Generation**: Blend evidence-based and community insights
- **Citation System**: Always provide source URLs and credibility indicators

#### 2.1.4 User Interface
- **Chat Interface**: Gradio-based conversational UI
- **Two-Pane Layout**: 
  - Left: Chat responses
  - Right: Evidence sources and community perspectives
- **Source Transparency**: Clear indication of source types and credibility

### 2.2 Data Schema

```json
{
  "condition": "string",
  "symptoms": ["string"],
  "causes": ["string"],
  "treatments": ["string"],
  "drugs": ["string"],
  "side_effects": ["string"],
  "source": "string",
  "source_type": "journal|health_site|community",
  "url": "string",
  "date_added": "datetime",
  "confidence_score": "float",
  "umls_codes": ["string"]
}
```

## 3. Technical Requirements

### 3.1 Technology Stack
- **Language**: Python 3.9+
- **Web Scraping**: Playwright
- **APIs**: PubMed E-utilities, UMLS API
- **Vector Database**: Chroma or FAISS
- **Relational Database**: SQLite
- **ML/AI**: Transformers (Flan-T5/Mistral), Sentence-Transformers
- **UI Framework**: Gradio
- **Data Processing**: Pandas, BeautifulSoup

### 3.2 Performance Requirements
- **Update Frequency**: Weekly data refresh
- **Response Time**: < 5 seconds for conversational queries
- **Storage**: Scalable to 100K+ medical entries
- **Concurrent Users**: Single-user application

### 3.3 Data Quality Requirements
- **Source Validation**: Verify URLs and source authenticity
- **Duplicate Detection**: Identify and merge duplicate entries
- **Terminology Consistency**: UMLS-based normalization
- **Citation Accuracy**: Maintain source attribution integrity

## 4. Non-Functional Requirements

### 4.1 Security & Compliance
- **Rate Limiting**: Respect API rate limits
- **Robots.txt Compliance**: Honor website scraping policies
- **Data Privacy**: No personal health information storage
- **Disclaimer**: Prominent medical advice disclaimer

### 4.2 Reliability
- **Error Handling**: Graceful failure for unavailable sources
- **Data Validation**: Input sanitization and validation
- **Backup Strategy**: Regular data backups
- **Monitoring**: Basic logging and error tracking

## 5. Implementation Phases

### Phase A: Data Ingestion Foundation (Weeks 1-2)

#### A1: PubMed Integration
- **Objective**: Set up PubMed API access for NEJM/JAMA abstracts
- **Deliverables**:
  - PubMed API client with authentication
  - Query functions for specific journals
  - Data extraction and basic parsing
  - Initial database schema implementation

#### A2: Web Scraping Setup
- **Objective**: Implement scraping for Mayo Clinic and WebMD
- **Deliverables**:
  - Playwright-based scraping framework
  - Disease page parsers for structured data extraction
  - Robots.txt compliance checker
  - Rate limiting and respectful scraping

#### A3: Community Sources Integration
- **Objective**: Access Reddit and health forum data
- **Deliverables**:
  - Reddit API integration for medical subreddits
  - Forum scraping for HealthBoards/Mayo Connect
  - Discussion thread parsing
  - Community content filtering

#### A4: UMLS Integration
- **Objective**: Set up medical ontology mapping
- **Deliverables**:
  - UMLS API client setup
  - Terminology normalization functions
  - CUI (Concept Unique Identifier) mapping
  - RxNorm drug name standardization

### Phase B: Data Processing & Storage (Weeks 3-4)

#### B1: Data Normalization Pipeline
- **Objective**: Standardize all ingested data
- **Deliverables**:
  - Data cleaning and validation functions
  - UMLS-based terminology mapping
  - Duplicate detection and merging
  - Quality scoring system

#### B2: Database Architecture
- **Objective**: Implement robust data storage
- **Deliverables**:
  - SQLite schema design and implementation
  - Vector database setup (Chroma/FAISS)
  - Data indexing and search optimization
  - Backup and recovery procedures

#### B3: Data Structuring
- **Objective**: Convert raw data to standardized format
- **Deliverables**:
  - JSON schema implementation
  - Data transformation pipelines
  - Source attribution system
  - Confidence scoring algorithm

### Phase C: RAG & Conversational Agent (Weeks 5-6)

#### C1: Embedding & Retrieval System
- **Objective**: Implement semantic search capabilities
- **Deliverables**:
  - Sentence transformer model integration
  - Vector embedding generation
  - Similarity search implementation
  - Hybrid search (structured + semantic)

#### C2: RAG Pipeline
- **Objective**: Build retrieval-augmented generation system
- **Deliverables**:
  - Query processing and expansion
  - Context retrieval from multiple sources
  - Evidence ranking and selection
  - Source blending algorithms

#### C3: Answer Generation
- **Objective**: Create conversational response system
- **Deliverables**:
  - Language model integration (Flan-T5/Mistral)
  - Prompt engineering for medical context
  - Response formatting and citation
  - Confidence scoring for answers

### Phase D: User Interface & Integration (Weeks 7-8)

#### D1: Gradio Interface Development
- **Objective**: Build user-friendly chat interface
- **Deliverables**:
  - Chat interface design and implementation
  - Two-pane layout (chat + sources)
  - Source credibility indicators
  - Interactive citation system

#### D2: System Integration
- **Objective**: Connect all components
- **Deliverables**:
  - End-to-end pipeline integration
  - Error handling and user feedback
  - Performance optimization
  - System monitoring and logging

#### D3: Testing & Refinement
- **Objective**: Validate system functionality
- **Deliverables**:
  - Comprehensive testing suite
  - User experience optimization
  - Performance tuning
  - Documentation and deployment guide

## 6. Success Metrics

### 6.1 Technical Metrics
- **Data Coverage**: 1000+ medical conditions with structured data
- **Source Diversity**: 3+ source types per condition
- **Response Accuracy**: 80%+ relevant responses
- **System Uptime**: 95%+ availability

### 6.2 User Experience Metrics
- **Query Response Time**: < 5 seconds average
- **Citation Completeness**: 100% responses include sources
- **Source Transparency**: Clear indication of evidence vs. community insights
- **Interface Usability**: Intuitive chat experience

## 7. Risk Assessment & Mitigation

### 7.1 Technical Risks
- **API Rate Limits**: Implement caching and respectful usage
- **Website Changes**: Build robust parsers with fallback options
- **Data Quality**: Implement validation and quality scoring
- **Model Performance**: Test multiple models and fine-tune

### 7.2 Legal/Compliance Risks
- **Terms of Service**: Regular review and compliance checking
- **Medical Disclaimer**: Prominent disclaimers throughout
- **Data Privacy**: No personal information collection
- **Source Attribution**: Maintain accurate citations

## 8. Future Enhancements (Post-MVP)

### 8.1 Advanced Features
- **Real-time Updates**: More frequent data refresh
- **Multi-language Support**: International medical sources
- **Advanced Analytics**: Usage patterns and insights
- **Mobile Interface**: Responsive design

### 8.2 Technical Improvements
- **Distributed Architecture**: Scalable multi-user system
- **Advanced NLP**: Better medical language understanding
- **Machine Learning**: Continuous improvement from usage
- **API Development**: External integration capabilities

## 9. Project Timeline

| Phase | Duration | Key Deliverables | Status |
|-------|----------|------------------|---------|
| Phase A | 2 weeks | Data ingestion from all sources | ✅ **COMPLETE** |
| Phase B | 2 weeks | Data processing and storage | ✅ **COMPLETE** |
| Phase C | 2 weeks | RAG and conversational agent | ✅ **COMPLETE** |
| Phase D | 2 weeks | UI and system integration | ✅ **COMPLETE** |
| **Total** | **8 weeks** | **Fully functional TrustMed AI** | ✅ **100% COMPLETE** |

## 10. Resource Requirements

### 10.1 Development Environment
- Python 3.9+ development environment
- API keys for PubMed, UMLS, Reddit
- Sufficient storage for medical databases
- GPU access for language models (optional)

### 10.2 External Dependencies
- Internet connectivity for API access
- Web scraping permissions
- Medical database access
- Cloud storage for backups (optional)

---

**Note**: This is an educational project for learning purposes. All medical information should be verified with licensed healthcare professionals.

