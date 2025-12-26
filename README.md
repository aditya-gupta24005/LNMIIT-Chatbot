# LNMIIT Chatbot

<div align="center">

![LNMIIT Chatbot](https://img.shields.io/badge/AI-Chatbot-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B)

**An intelligent RAG-based chatbot for The LNM Institute of Information Technology**

</div>

## About

The LNMIIT Chatbot is a Retrieval-Augmented Generation (RAG) system designed to provide accurate, context-aware answers to questions about The LNM Institute of Information Technology. By combining web scraping, vector databases, and Google's Gemini AI, this chatbot serves as an intelligent information assistant for students, faculty, and visitors.

## Key Features

- **Intelligent Data Scraping**: Automatically crawls and extracts content from the LNMIIT website, including both web pages and PDF documents
- **RAG Architecture**: Combines retrieval-based and generative AI approaches for accurate responses
- **Semantic Search**: Uses sentence transformers and Milvus vector database for efficient similarity search
- **Google Gemini Integration**: Powered by Google's Gemini Flash model for natural language generation
- **Modern User Interface**: Clean Streamlit-based chat interface with floating widget design
- **RESTful API**: FastAPI backend enables easy integration with other applications

## Architecture

```
User Query → Frontend (Streamlit) → Backend (FastAPI) 
                                         ↓
                                    RAG Pipeline
                                         ↓
                        ┌────────────────┴────────────────┐
                        ↓                                 ↓
                   Retriever                          Generator
                (Milvus Search)                    (Google Gemini)
                        ↓                                 ↓
                   Relevant Docs ──────────────→  Final Answer
```

## Project Structure

```
LNMIIT-Chatbot/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   └── rag/
│       ├── scraper.py         # Web scraper (Trafilatura + PyPDF)
│       ├── processor.py       # Data cleaning and chunking
│       ├── indexer.py         # Embedding generation and Milvus indexing
│       ├── retriever.py       # Semantic search logic
│       ├── generator.py       # Google Gemini integration
│       └── pipeline.py        # Orchestrates retrieval and generation
├── Frontend/
│   ├── ui.py                  # Streamlit chat interface
│   ├── campus_bg.png          # Background image
│   └── logo.png               # LNMIIT logo
├── data/                      # Generated during data pipeline
│   ├── raw/                   # Scraped data
│   ├── processed/             # Cleaned and chunked data
│   └── milvus.db              # Vector database
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))
- 2GB+ free disk space for vector database

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/aditya-gupta24005/LNMIIT-Chatbot.git
cd LNMIIT-Chatbot
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r backend/requirements.txt
pip install streamlit
```

### Configuration

Set up your Google Gemini API key as an environment variable:

**Linux/macOS:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

## Data Pipeline Setup

Before using the chatbot, you need to build the knowledge base. Follow these steps in order:

### Step 1: Scrape Data
Extract content from the LNMIIT website:
```bash
python backend/rag/scraper.py --seed https://lnmiit.ac.in --max-pages 200
```

**Options:**
- `--seed`: Starting URL to crawl
- `--max-pages`: Maximum number of pages to scrape
- `--local-pdf-folder`: Path to local PDF folder (optional)

### Step 2: Process Data
Clean and chunk the scraped content:
```bash
python backend/rag/processor.py
```

This step:
- Removes HTML artifacts and special characters
- Splits text into optimal chunk sizes
- Saves processed data to `backend/data/processed/`

### Step 3: Index Data
Generate embeddings and build the vector database:
```bash
python backend/rag/indexer.py
```

This creates the Milvus database at `backend/data/milvus.db` with semantic embeddings.

## Running the Application

You need to run both the backend and frontend simultaneously:

### Terminal 1: Start Backend API
```bash
python backend/main.py
```
- API runs at: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

### Terminal 2: Start Frontend UI
```bash
streamlit run Frontend/ui.py
```
- Web interface opens at: `http://localhost:8501`
- Click the **"Ask LNMIIT"** button to start chatting

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | FastAPI |
| **Frontend Framework** | Streamlit |
| **LLM** | Google Gemini 2.5 Flash |
| **Vector Database** | Milvus Lite |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Web Scraping** | trafilatura, pypdf, beautifulsoup4 |
| **HTTP Client** | httpx |

## API Endpoints

### `POST /query`
Submit a question to the chatbot.

**Request Body:**
```json
{
  "question": "What are the admission requirements for B.Tech?"
}
```

**Response:**
```json
{
  "answer": "The admission requirements include...",
  "sources": [
    {
      "title": "Admissions",
      "url": "https://lnmiit.ac.in/admissions"
    }
  ]
}
```

### `GET /health`
Check if the API is running.

## How It Works

1. **User Query**: User asks a question through the chat interface
2. **Retrieval**: The system searches the vector database for relevant chunks of information
3. **Context Building**: Top matching documents are retrieved and formatted
4. **Generation**: Google Gemini generates a natural response using the retrieved context
5. **Response**: The answer is displayed with source citations

## Features in Detail

### Smart Scraping
- Polite crawler with rate limiting
- Extracts text from both HTML pages and PDF documents
- Maintains document metadata (URLs, titles, timestamps)

### Vector Search
- Uses state-of-the-art sentence embeddings
- Fast semantic similarity search with Milvus
- Configurable top-k retrieval

### Context-Aware Generation
- Provides accurate answers grounded in source documents
- Includes source citations for transparency
- Handles multi-turn conversations

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Authors

- [@aditya-gupta24005](https://github.com/aditya-gupta24005)

## Acknowledgments

- The LNM Institute of Information Technology for the data source
- Google for providing the Gemini API
- The open-source community for the excellent tools and libraries

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the project structure and logs

## Roadmap

- [ ] Add conversation memory for multi-turn dialogues
- [ ] Implement user feedback mechanism
- [ ] Add support for more document types
- [ ] Deploy to cloud platform
- [ ] Add multilingual support
- [ ] Implement advanced filtering options

---

<div align="center">

**Built with care for the LNMIIT community**

[Report Bug](https://github.com/aditya-gupta24005/LNMIIT-Chatbot/issues) · [Request Feature](https://github.com/aditya-gupta24005/LNMIIT-Chatbot/issues)

</div>
