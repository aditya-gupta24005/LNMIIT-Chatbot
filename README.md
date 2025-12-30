# LNMIIT Chatbot

<div align="center">

![LNMIIT Chatbot](https://img.shields.io/badge/AI-Chatbot-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-black)
![Tailwind](https://img.shields.io/badge/Tailwind-CSS-38B2AC)

**An intelligent RAG-based chatbot for The LNM Institute of Information Technology**

</div>

## About

The LNMIIT Chatbot is a Retrieval-Augmented Generation (RAG) system designed to provide accurate, context-aware answers to questions about The LNM Institute of Information Technology. By combining web scraping, vector databases, and Google's Gemini AI, this chatbot serves as an intelligent information assistant for students, faculty, and visitors.

## Key Features

- **Intelligent Data Scraping**: Automatically crawls and extracts content from the LNMIIT website, including both web pages and PDF documents
- **RAG Architecture**: Combines retrieval-based and generative AI approaches for accurate responses
- **Semantic Search**: Uses sentence transformers and Milvus vector database for efficient similarity search
- **Google Gemini Integration**: Powered by Google's Gemini Flash model for natural language generation
- **Modern User Interface**: Aesthetic Next.js frontend with glassmorphism design and smooth animations
- **RESTful API**: FastAPI backend enables easy integration with other applications

## Architecture

```
User Query → Frontend (Next.js) → Backend (FastAPI) 
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
├── frontend/
│   ├── app/                   # Next.js App Router pages
│   ├── components/            # React components (ChatWidget, etc.)
│   ├── public/                # Static assets (images, icons)
│   └── package.json           # Frontend dependencies
├── data/                      # Generated during data pipeline
│   ├── raw/                   # Scraped data
│   ├── processed/             # Cleaned and chunked data
│   └── milvus.db              # Vector database
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))
- 2GB+ free disk space for vector database

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/aditya-gupta24005/LNMIIT-Chatbot.git
cd LNMIIT-Chatbot
```

2. **Backend Setup**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
cd ..
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

## Data Pipeline Setup

Before using the chatbot, you must build the knowledge base.

1. **Scrape Data**:
   ```bash
   python backend/rag/scraper.py --seed https://lnmiit.ac.in --max-pages 200
   ```
2. **Process Data**:
   ```bash
   python backend/rag/processor.py
   ```
3. **Index Data**:
   ```bash
   python backend/rag/indexer.py
   ```

## Running the Application

You need to run both the backend and frontend simultaneously in separate terminals.

### Terminal 1: Backend API
```bash
# Make sure you are in the root directory and venv is activated
source .venv/bin/activate
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API runs at: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### Terminal 2: Frontend UI
```bash
cd frontend
npm run dev
```
- Open `http://localhost:3000` in your browser.

## Deployment

### Frontend (Vercel)
1. Push this repo to GitHub.
2. Import the project into Vercel.
3. Set **Root Directory** to `frontend`.
4. Add Environment Variable: `NEXT_PUBLIC_BACKEND_URL` pointing to your deployed backend.

### Backend (Render/Railway/Heroku)
1. Deploy the `backend/` directory.
2. Ensure `GEMINI_API_KEY` is set in the cloud environment.
3. Install dependencies from `backend/requirements.txt`.
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | FastAPI |
| **Frontend Framework** | Next.js 14, React, Tailwind CSS |
| **LLM** | Google Gemini 2.5 Flash |
| **Vector Database** | Milvus Lite |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Web Scraping** | trafilatura, pypdf, beautifulsoup4 |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License

## Authors

- [@aditya-gupta24005](https://github.com/aditya-gupta24005)
