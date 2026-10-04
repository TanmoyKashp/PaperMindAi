# PaperMind AI

An AI-powered research paper analysis assistant that transforms academic PDFs into structured insights and enables document-grounded conversations.

---

## 1. Project Overview

PaperMind AI is an academic research assistant designed to streamline the literature review process for students, researchers, and engineers. Scientific research papers published in conferences and journals are typically dense, multi-page PDF documents formatted in two-column layouts. Manually reading through dozens of papers to identify research questions, baseline benchmarks, specific model architectures, and experimental limitations requires significant time and effort.

PaperMind AI addresses this challenge by combining classical Natural Language Processing (NLP) text processing techniques with modern Large Language Model (LLM) intelligence powered by Google Gemini. The system extracts clean digital text from academic PDFs, calculates explainable linguistic statistics, synthesizes structured paper components according to academic standards, and allows users to ask grounded questions directly about the uploaded document.

The application includes both a modern React web interface designed with an editorial aesthetic for focused reading and a standalone Streamlit application preserved as a fallback.

---

## 2. Key Features

- **PDF Upload and Text Extraction:** Ingest academic PDF files with automated layout cleaning, hyphenation repair, and multi-page text aggregation using PyMuPDF.
- **Research Paper Analysis Using Google Gemini:** Generate structured academic summaries via the official Google Gen AI Python SDK using low-temperature inference (0.2) for analytical consistency.
- **Executive Summary:** High-level narrative summary explaining the core purpose and context of the research.
- **Problem Statement:** Explicit identification of the scientific gap or research challenge addressed by the authors.
- **Research Objectives:** Itemized breakdown of primary research aims and investigative targets.
- **Proposed Methodology:** Step-by-step description of the proposed experimental and theoretical approach.
- **Algorithms and Models:** Extraction of named neural architectures, statistical algorithms, and computational techniques utilized.
- **Datasets and Benchmarks:** Catalog of training corpora, evaluation benchmarks, and experimental test suites referenced.
- **Key Findings and Experimental Results:** Summary of quantitative results, performance comparisons, and author claims.
- **Limitations:** Explicit cataloging of stated model assumptions, computational constraints, and experimental boundaries.
- **Future Research Directions:** Author-suggested next steps and open problems for future academic investigation.
- **Keyword Extraction:** Identification of technical domain keywords while filtering out generic academic stop words.
- **Document-Grounded Q&A:** Interactive conversational question answering where answers are strictly derived from the paper's text content, avoiding hallucinations and stating when evidence is absent.
- **Conversation History:** Multi-turn dialogue memory allowing contextual follow-up questions within the active paper session.
- **Markdown Report Export:** One-click generation and download of complete academic reports in standardized Markdown format.
- **NLP Document Statistics:** Quantitative linguistic metrics computed via NLTK, including word counts, sentence counts, vocabulary size, lexical density, and estimated reading time.
- **API Key Configuration:** In-application Gemini API key setup and validation with immediate connectivity testing.
- **Reliability and Retry Handling:** Bounded exponential backoff retry mechanism (2s, 4s, 8s) for transient HTTP 503 high-demand spikes, HTTP 429 rate limits, and network timeouts.
- **React-Based Interface:** Clean, distraction-free web application inspired by editorial design principles, built with React 19, Vite, and custom CSS design tokens.
- **Streamlit Fallback:** Fully independent Streamlit implementation (`app.py`) for rapid local execution without Node.js dependencies.

---

## 3. Application Screenshots

<!-- Screenshots can be added to the repository in an assets/ or docs/ directory and linked here. -->

> Note: Screenshots of the PaperMind AI interface can be placed in `docs/screenshots/` and referenced below.

| Screen | Description | Path |
| :--- | :--- | :--- |
| **Workspace & Upload** | Editorial hero section with drag-and-drop PDF upload and extraction progress. | `docs/screenshots/workspace_upload.png` *(placeholder)* |
| **Document Overview** | Executive summary, problem statement, and key contributions. | `docs/screenshots/document_overview.png` *(placeholder)* |
| **Component Analysis** | Two-column grid detailing methodology, models, benchmarks, and limitations. | `docs/screenshots/component_analysis.png` *(placeholder)* |
| **Grounded Q&A** | Conversational chat interface rendering rich Markdown responses and code blocks. | `docs/screenshots/grounded_chat.png` *(placeholder)* |
| **Report Preview** | Formatted Markdown research report preview and download trigger. | `docs/screenshots/report_preview.png` *(placeholder)* |

---

## 4. Technology Stack

### Frontend
- **React 19:** Modular component architecture managing application state and tab views.
- **Vite 8:** Frontend development server and optimized production bundler.
- **JavaScript (ES Modules):** Modern ECMAScript client-side logic.
- **CSS3:** Custom design tokens, editorial typography (DM Serif Display and Inter), and responsive layouts.
- **Lucide React:** Consistent, lightweight vector icon system.
- **React Markdown & Remark GFM:** Safe, rich Markdown rendering with support for tables, lists, blockquotes, and copyable code blocks.

### Backend
- **Python 3.12 / 3.10+:** Core runtime environment for server and NLP pipelines.
- **FastAPI:** High-performance, asynchronous REST API framework serving document intelligence endpoints.
- **Uvicorn:** Production-ready ASGI web server.
- **Google Gen AI SDK (`google-genai`):** Official Python client for Google Gemini models.
- **PyMuPDF (`pymupdf`):** High-speed PDF text extraction and document layout parsing.
- **NLTK:** Natural Language Toolkit for sentence segmentation, tokenization, and linguistic statistics.
- **Pydantic 2:** Strict schema validation and data sanitization for structured model outputs.
- **PyYAML:** Configuration parsing for centralized application parameters.
- **python-multipart:** Streaming multi-part form handling for PDF uploads.
- **python-dotenv:** Environment variable management.

### Fallback Frontend
- **Streamlit:** Python-based interactive dashboard framework for running the application without a Node.js runtime.

### Testing & Code Quality
- **Pytest:** Comprehensive backend test runner verifying extraction, NLP metrics, reliability retries, and API endpoints.
- **Oxlint:** Fast JavaScript and React linter ensuring clean frontend code.

---

## 5. Architecture

PaperMind AI connects digital PDF processing, classical NLP tokenization, and generative LLM inference through a clean modular structure.

### Processing Workflows

#### Document Analysis Flow
```
PDF Upload (Frontend)
       │
       ▼
FastAPI Server (POST /api/upload)
       │
       ▼
PyMuPDF Processor (Text Extraction, Column Repair, Hyphenation Reconnect)
       │
       ▼
NLTK Text Preprocessor (Tokenization, Sentence Segmentation, Linguistic Statistics)
       │
       ▼
Paper Analyzer Module (Prompt Construction & Schema Definitions)
       │
       ▼
Gemini Client (Bounded Exponential Backoff & Low-Temperature Inference)
       │
       ▼
Pydantic Validator (Structure Verification & Graceful Fallback Recovery)
       │
       ▼
React Frontend (Interactive Overview, Components, Keywords, Metrics)
```

#### Grounded Q&A Flow
```
User Question (React Chat Tab)
       │
       ▼
FastAPI Server (POST /api/chat)
       │
       ▼
Relevant Context Retriever (Heuristic Keyword-Overlap Matching)
       │
       ▼
QA Engine (Grounded Academic Prompt + Conversation History)
       │
       ▼
Gemini Client (Document-Constrained Generation)
       │
       ▼
FastAPI Response (Answer + Updated Chat History)
       │
       ▼
React Markdown Renderer (Tables, Formatted Text, Code Blocks with Copy Action)
```

### Architectural Roles
- **FastAPI Server (`server.py`):** Coordinates document sessions, enforces duplicate request protection, maps HTTP exceptions to clear user messages, and mounts the built React frontend.
- **PDF Processor (`modules/pdf_processor.py`):** Handles raw byte ingestion, detects scanned/empty documents, removes layout noise, and partitions long documents into processing chunks.
- **Text Preprocessor (`modules/text_preprocessor.py`):** Performs deterministic NLP computations using NLTK to provide objective document metrics independent of LLM evaluation.
- **Gemini Client (`modules/gemini_client.py`):** Encapsulates API interactions, manages authentication, classifies error codes, and applies bounded exponential backoff.
- **Paper Analyzer (`modules/paper_analyzer.py`):** Enforces structured JSON output matching the academic paper schema and applies fallback sanitization when fields are absent.
- **QA Engine (`modules/qa_engine.py`):** Restricts answers to the extracted document text, ensuring claims cite the paper or state when information is unavailable.
- **Report Generator (`modules/report_generator.py`):** Compiles document metrics, author metadata, analysis sections, and keywords into a publication-ready Markdown file.

---

## 6. Project Structure

```
PaperMindAi/
├── config/
│   └── config.yaml             # Central configuration (model, NLP, and Q&A parameters)
├── frontend/
│   ├── index.html              # HTML shell loading Google Fonts (DM Serif Display, Inter)
│   ├── package.json            # Frontend dependencies and npm scripts
│   ├── vite.config.js          # Vite configuration with API dev proxy
│   ├── README.md               # Frontend-specific documentation
│   ├── public/                 # Static assets (favicons and SVG icons)
│   └── src/
│       ├── App.jsx             # Main React view controller and tab coordinator
│       ├── index.css           # Design tokens, typography rules, and markdown styles
│       ├── main.jsx            # React root mount point
│       ├── services/
│       │   └── api.js          # Centralized REST API client
│       └── components/
│           ├── layout/
│           │   └── AppHeader.jsx      # Navigation bar, mobile menu drawer, and settings
│           ├── upload/
│           │   └── UploadZone.jsx     # Drag-and-drop PDF upload zone
│           ├── analysis/
│           │   ├── DocumentHeader.jsx # Title, metadata, and analyze action with retry
│           │   ├── MetricsRow.jsx     # Linguistic statistics display cards
│           │   ├── OverviewTab.jsx    # Executive summary, problem, and conclusions
│           │   ├── AnalysisTab.jsx    # Structured 2-column breakdown of paper components
│           │   └── KeywordsTab.jsx    # Domain keyword pills with copy action
│           ├── chat/
│           │   ├── ChatTab.jsx        # Context-grounded Q&A panel
│           │   └── ChatMessage.jsx    # react-markdown renderer with copyable code blocks
│           ├── report/
│           │   └── ReportTab.jsx      # Markdown report preview and export button
│           └── common/
│               └── ApiKeyModal.jsx    # In-app Gemini API key validator modal
├── modules/
│   ├── __init__.py
│   ├── gemini_client.py        # Gemini client with bounded backoff and error classification
│   ├── paper_analyzer.py       # Structured paper analysis and Pydantic validation
│   ├── pdf_processor.py        # PyMuPDF text extraction, chunking, and cleaning
│   ├── qa_engine.py            # Document-grounded Q&A with heuristic context retrieval
│   ├── report_generator.py     # Academic Markdown report synthesis
│   └── text_preprocessor.py    # NLTK tokenization, sentence segmentation, and metrics
├── prompts/
│   ├── analysis_prompt.txt     # Few-shot prompt for structured component extraction
│   ├── qa_prompt.txt           # Grounded Q&A system prompt preventing hallucination
│   └── system_prompt.txt       # Base persona and academic instructions
├── sample_papers/
│   └── README.md               # Guidance on test papers for literature evaluation
├── tests/
│   ├── test_components.py      # Unit tests for PaperAnalyzer, QAEngine, and GeminiClient
│   ├── test_pdf_processor.py   # Unit tests for PDF parsing, corrupted files, and chunking
│   ├── test_preprocessor.py    # Unit tests for NLTK text processing and metrics
│   └── test_reliability.py     # Unit tests for retries, backoff, 503, 429, and auth errors
├── app.py                      # Standalone Streamlit application (preserved fallback)
├── pytest.ini                  # Pytest configuration with pythonpath set to root
├── requirements.txt            # Python dependencies
├── server.py                   # FastAPI application server and static React host
├── .env.example                # Example environment variable file
└── .gitignore                  # Git ignore rules for venv, secrets, and caches
```

---

## 7. Prerequisites

Before setting up PaperMind AI, ensure your environment meets the following requirements:

- **Python:** Version 3.10, 3.11, or 3.12 (tested on Python 3.12).
- **Node.js & npm:** Node.js version 18.0 or higher (tested on Node v24) and npm 9.0 or higher.
- **Git:** Version 2.30 or higher.
- **Google Gemini API Key:** A free or paid API key from Google AI Studio.

---

## 8. Installation and Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/TanmoyKashp/PaperMindAi.git
cd PaperMindAi
```

### Step 2: Set Up Python Virtual Environment

**On macOS and Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Step 3: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 9. Gemini API Configuration

PaperMind AI requires a Google Gemini API key for document analysis and grounded Q&A.

### Obtaining an API Key
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **Get API key** and generate a new key.

### Configuring the Key

**Option A: Environment File (`.env`)**
Create a `.env` file in the root directory based on `.env.example`:
```bash
cp .env.example .env
```
Edit `.env` and set your key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> **Important Security Note:** The `.env` file is excluded from Git tracking via `.gitignore`. Never commit your real API key to any public or private repository.

**Option B: In-Application Configuration**
You can also launch the application without a pre-set key and click the **API Key** button in the header to enter and verify your key directly in the browser session.

### Configurable Model Settings
Model parameters are defined in `config/config.yaml`:
```yaml
model:
  name: "gemini-3.5-flash"
  temperature: 0.2
  max_output_tokens: 4096
  top_p: 0.95
```
You can adjust the temperature or model name here if needed.

---

## 10. Running the Application

PaperMind AI supports three distinct operational modes depending on your workflow.

### Mode 1: Unified Application (Recommended)
This runs the FastAPI backend and serves the compiled React application from a single port (`8000`).

1. Build the React frontend:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```
2. Start the unified server:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   python server.py
   ```
3. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

### Mode 2: Frontend Development Mode (Hot Reload)
Use this mode when modifying React components with immediate Vite Hot Module Replacement (HMR).

**Terminal 1 (Backend API):**
```bash
source .venv/bin/activate
uvicorn server:app --reload --port 8000
```

**Terminal 2 (Vite Frontend):**
```bash
cd frontend
npm run dev
```

Open your browser at:
```
http://localhost:5173
```
Vite automatically proxies API requests to `http://localhost:8000/api`.

### Mode 3: Streamlit Fallback
If Node.js is unavailable in your environment, you can run the original Streamlit application:
```bash
source .venv/bin/activate
streamlit run app.py
```
Open your browser at:
```
http://localhost:8501
```

---

## 11. Usage Instructions

1. **Launch PaperMind AI:** Start the server using Mode 1 or Mode 2 and open the application in your browser.
2. **Configure API Key:** Check the API status badge in the top right. If unconfigured, click the key icon to input your Google Gemini API key.
3. **Upload an Academic Paper:** Drag and drop an academic PDF file into the upload zone or click to select a file (up to 20 MB).
4. **Text Extraction & Linguistic Metrics:** The system automatically extracts text via PyMuPDF and renders document metrics (page count, total words, sentence count, vocabulary size, and estimated reading time).
5. **Run AI Synthesis:** Click **Analyze Research Paper**. The system sends the extracted text to Gemini using structured prompts.
6. **Explore Extracted Components:**
   - **Overview:** Read the high-level executive summary, problem statement, key contributions, and conclusions.
   - **Analysis:** Inspect the two-column breakdown of research objectives, proposed methodology, algorithms/models, datasets, experimental findings, limitations, and future scope.
   - **Keywords:** Review extracted domain keywords and click **Copy All** to save them to your clipboard.
7. **Ask Grounded Questions:** Navigate to the **Ask Paper** tab. Type a question or select a suggested prompt. Answers cite the paper content and explicitly note when an answer is not in the text.
8. **Export Academic Report:** Switch to the **Report** tab to preview the structured summary and click **Download Markdown Report (.md)** for offline documentation.
9. **Reset Workspace:** Click **Upload New Paper** in the header to clear the active session and process another document.

---

## 12. API Endpoints

The FastAPI server (`server.py`) exposes RESTful endpoints for integration:

| Method | Endpoint | Description | Request Payload / Params | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/config` | Returns system config, active model name, and API key status. | None | `{ "app_name": str, "model_name": str, "is_api_configured": bool, ... }` |
| `POST` | `/api/config/api-key` | Updates active Gemini API key in memory and verifies connectivity. | `{ "api_key": str }` | `{ "success": bool, "message": str, "is_configured": bool }` |
| `POST` | `/api/config/test-connection` | Verifies active Gemini API credentials by sending a test ping. | None | `{ "success": bool, "message": str }` |
| `POST` | `/api/upload` | Ingests PDF file, extracts text via PyMuPDF, and computes NLTK metrics. | `multipart/form-data` with `file: UploadFile` | `{ "doc_id": str, "filename": str, "page_count": int, "stats": dict }` |
| `GET` | `/api/document/{doc_id}` | Retrieves document metadata, analysis results, and chat history. | Path param: `doc_id` | Document record with stats, analysis, and chat history |
| `POST` | `/api/analyze` | Executes structured Gemini research synthesis with duplicate protection. | `{ "doc_id": str }` | `{ "success": bool, "analysis": dict }` (Returns 409 if already analyzing) |
| `POST` | `/api/chat` | Performs grounded question answering against the active paper. | `{ "doc_id": str, "question": str }` | `{ "success": bool, "answer": str, "chat_history": list }` |
| `POST` | `/api/chat/clear` | Clears conversation history for the specified document session. | `{ "doc_id": str }` | `{ "success": bool }` |
| `GET` | `/api/report/download` | Generates and downloads the Markdown research report. | Query param: `?doc_id=...` | File download (`text/markdown` attachment) |
| `POST` | `/api/reset` | Clears active document and session state in memory. | None | `{ "success": bool }` |

---

## 13. Reliability and Error Handling

External AI services can experience temporary spikes in traffic, quota limitations, or network latency. PaperMind AI implements resilient error handling across both backend and frontend layers:

- **Bounded Exponential Backoff:** The Gemini client automatically retries transient failures up to 3 times:
  - Attempt 1: ~2 seconds delay
  - Attempt 2: ~4 seconds delay
  - Attempt 3: ~8 seconds delay
- **Transient Error Classification:**
  - HTTP 503 (`UNAVAILABLE`): Temporary high demand on Google servers.
  - HTTP 429 (`RESOURCE_EXHAUSTED`): Rate limits and quota exhaustion.
  - Network timeouts and connection drops.
- **Server Retry-After Header Parsing:** If the Gemini SDK or server returns a `Retry-After` header or delay directive, the client respects that duration instead of default backoff intervals.
- **Non-Retry Policy for Permanent Errors:** Authentication failures (HTTP 401/403, invalid API key), malformed requests (HTTP 400), and invalid arguments fail immediately on the first attempt without redundant retries.
- **Duplicate Request Prevention:** The backend implements an in-flight execution lock per document. If a concurrent analysis request is triggered for the same document, the server responds with `HTTP 409 Conflict`.
- **Session State Preservation:** If an analysis or Q&A attempt fails, the uploaded document, its extracted text, and its linguistic metrics remain intact. The user is provided with a **Retry Analysis** button without needing to re-upload the PDF.
- **Human-Readable Error Messages:** Raw Python exceptions and SDK stack traces are translated into user-friendly notices (for example, explaining high model demand or rate limits) while logging technical details securely on the server.

---

## 14. Testing

The project includes unit tests for backend modules and reliability routines, as well as static analysis for the frontend.

### Running Python Tests
Activate your virtual environment and run Pytest:
```bash
.venv/bin/pytest -v
```

**Test Suite Coverage (29 Passed Tests):**
- **Component Tests (`tests/test_components.py`):** Configured and unconfigured Gemini client behaviors, mock-based paper analysis, Pydantic field sanitization, and grounded Q&A extraction.
- **PDF Processor Tests (`tests/test_pdf_processor.py`):** Multi-page valid PDF extraction, corrupted file handling, invalid extension rejection, empty file detection, scanned PDF detection, hyphenation cleaning, and token chunking.
- **Preprocessor Tests (`tests/test_preprocessor.py`):** Text normalization, sentence segmentation, NLTK statistical calculations, relevant context extraction, and Markdown report formatting.
- **Reliability Tests (`tests/test_reliability.py`):** Bounded backoff retry sequence on 503 errors, repeated 503 exhaustion, 429 rate limit handling, Retry-After header parsing, immediate rejection of invalid API keys, timeout recovery, duplicate analysis prevention (HTTP 409), and document preservation after failure.

> Note on Test Strategy: All unit tests in the test suite utilize deterministic mocks. They do not consume live Google Gemini API quota or require active network access during automated test runs.

### Running Frontend Verification
From the `frontend/` directory:
```bash
cd frontend

# Run Oxlint
npm run lint

# Run production build
npm run build
```
The linter completes with zero errors and zero warnings across all project files.

---

## 15. Limitations

To ensure realistic expectations, users should note the following constraints:

- **Scanned PDFs and Optical Character Recognition (OCR):** The current implementation relies on digital text extraction via PyMuPDF. PDFs containing scanned images of pages without an underlying text layer cannot be parsed without external OCR pre-processing.
- **Complex Two-Column Tables and Mathematical Notations:** While PyMuPDF extracts text streams effectively, intricate multi-column tables, inline LaTeX equations, and vector diagrams may suffer from linearized ordering in raw extracted text.
- **External Service Availability:** Analysis and question answering depend on Google Gemini API uptime and user quota allowances. High demand periods on Google servers may trigger transient delays.
- **Analysis Quality Dependency:** The accuracy of the synthesized research components directly reflects the clarity and completeness of the author's writing in the source document.

---

## 16. Security

- **Local Credential Storage:** API keys are never stored on external databases or central servers. They reside only in local `.env` files or temporary browser session memory.
- **Git Exclusions:** The repository `.gitignore` explicitly prevents `.env`, `.env.*` (excluding `.env.example`), virtual environments, and local build artifacts from being committed.
- **No Embedded Secrets:** Frontend source code contains no hardcoded API tokens or sensitive credentials.
- **Safe Rendering:** The chat interface uses `react-markdown` with strict component mappings, avoiding `dangerouslySetInnerHTML` to prevent Cross-Site Scripting (XSS) risks from untrusted document content.

---

## 17. Future Improvements

Potential enhancements planned for subsequent iterations:

- **Integrated OCR Engine:** Incorporating Tesseract or Google Cloud Vision OCR to support scanned archival papers and historical manuscripts.
- **Citation-Level Verification:** Linking extracted claims directly to specific page and paragraph numbers in the original PDF.
- **Hybrid Retrieval-Augmented Generation (RAG):** Adding vector embeddings (such as ChromaDB or FAISS) for semantic chunk search over lengthy doctoral dissertations or multi-volume proceedings.
- **Additional Export Formats:** Providing export options for PDF summaries, BibTeX bibliographic citations, and LaTeX summary slides.
- **Batch Processing:** Allowing users to upload multiple related papers simultaneously to produce comparative literature review matrices.

---

## 18. Academic Project Information

PaperMind AI was developed as a final-year academic project in Computer Science and Engineering, focusing on Natural Language Processing and practical Large Language Model integration. The project demonstrates the application of classical computational linguistics (tokenization, sentence boundary detection, lexical diversity) alongside modern generative AI capabilities to solve real-world information retrieval challenges.

---

## 19. License

This repository does not currently include a formal open-source license. Licensing information may be added separately by the project author. All rights are reserved by the original creators.
