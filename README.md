````markdown
# LNMIIT Chatbot (RAG-based)

A Retrieval-Augmented Generation (RAG) chatbot designed to answer queries about **The LNM Institute of Information Technology (LNMIIT)**.
 This application scrapes the institute's website (HTML and PDFs), processes the data into chunks, indexes it using a vector database,
and uses Google's Gemini model to generate accurate,context-aware responses via a conversational interface.

##  Features

* **Automated Scraping**: "Polite" crawler that fetches content from `lnmiit.ac.in`, including web pages and PDF documents.
* **RAG Pipeline**:
    * **Retrieval**: Uses `sentence-transformers` and **Milvus Lite** for efficient semantic search.
    * **Generation**: Powered by **Google Gemini (Flash model)** for concise and accurate answers.
* **Modern UI**: A Streamlit-based frontend featuring a custom, floating chat widget that overlays the main page.
* **API-First Design**: FastAPI backend handles query processing, making the system extensible.

##  Project Structure


LNMIIT-Chatbot/
├── backend/
│   ├── main.py                # FastAPI application entry point
│   ├── requirements.txt       # Python dependencies
│   └── rag/
│       ├── scraper.py         # Web scraper (Trafilatura + PyPDF)
│       ├── processor.py       # Data cleaning and chunking
│       ├── indexer.py         # Embedding generation and Milvus indexing
│       ├── retriever.py       # Search logic
│       ├── generator.py       # Google Gemini integration
│       └── pipeline.py        # Orchestrates retrieval and generation
├── Frontend/
│   ├── ui.py                  # Streamlit frontend application
│   ├── campus_bg.png          # Background asset
│   └── logo.png               # Logo asset
├── data/                      # (Generated) Stores raw, processed, and indexed data
└── .gitignore
````

##  Prerequisites

  * **Python 3.8+**
  * **Google Gemini API Key**: You need an API key from Google AI Studio.

##  Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd LNMIIT-Chatbot
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r backend/requirements.txt
    pip install streamlit  # Ensure streamlit is installed for the frontend
    ```

##  Configuration

You must set the `GEMINI_API_KEY` environment variable for the LLM to work.

**On Linux/macOS:**

```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

**On Windows (PowerShell):**

```powershell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

*Alternatively, you can create a `.env` file (if you add `python-dotenv` to your setup) or hardcode it in `backend/rag/generator.py` for testing (not recommended).*

##  Data Pipeline Setup (Important)

Before running the chat application, you must populate the knowledge base.

**1. Scrape Data:**
Crawls the website and saves raw JSONL files to `backend/data/raw/`.

```bash
python backend/rag/scraper.py --seed [https://lnmiit.ac.in](https://lnmiit.ac.in) --max-pages 200
```

*Note: You can also point it to a local folder of PDFs using `--local-pdf-folder /path/to/pdfs`.*

**2. Process Data:**
Cleans and chunks the raw data, saving it to `backend/data/processed/`.

```bash
python backend/rag/processor.py
```

**3. Index Data:**
Generates embeddings and builds the Milvus vector database in `backend/data/milvus.db`.

```bash
python backend/rag/indexer.py
```

##  Running the Application

You need to run the Backend and Frontend in separate terminals.

### 1\. Start the Backend API

```bash
python backend/main.py
```

  * The API will start at `http://0.0.0.0:8000`.
  * Swagger documentation is available at `http://localhost:8000/docs`.

### 2\. Start the Frontend UI

Open a new terminal, activate the environment, and run:

```bash
streamlit run Frontend/ui.py
```

  * The UI will open in your browser (usually at `http://localhost:8501`).
  * Click the **" Ask LNMIIT"** pill in the top-right corner to open the chat widget.

##  Tech Stack

  * **Frameworks**: FastAPI, Streamlit
  * **LLM**: Google Gemini (gemini-2.5-flash)
  * **Vector DB**: Milvus Lite (`pymilvus`)
  * **Embeddings**: `all-MiniLM-L6-v2` (via `sentence-transformers`)
  * **Scraping**: `trafilatura`, `pypdf`, `beautifulsoup4`

<!-- end list -->

```
```
