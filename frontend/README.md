# PaperMind AI - Frontend

The frontend user interface for PaperMind AI is built with React 19, Vite, and modern CSS design tokens, following an editorial typography and minimalism aesthetic.

## Purpose

The frontend provides an interactive workspace for researchers and students to:
- Upload and inspect academic research PDFs.
- View real-time PyMuPDF text extraction status and NLTK linguistic statistics.
- Trigger and view structured paper analyses (overview, objectives, methodology, models, benchmarks, limitations, future work, and keywords).
- Engage in document-grounded question answering with formatted Markdown responses and copyable code blocks.
- Export comprehensive Markdown reports.
- Manage and test Gemini API configuration directly within the UI.

## Technologies

- **React 19:** Component-based UI library with hooks.
- **Vite 8:** Fast modern frontend tooling and development server with HMR.
- **Lucide React:** Lightweight, consistent icon set.
- **React Markdown & Remark GFM:** Safe, rich Markdown rendering with GitHub Flavored Markdown support (tables, lists, inline code, and syntax blocks).
- **Oxlint:** High-performance JavaScript and React linter.
- **CSS Design Tokens:** Custom typography and color system using DM Serif Display and Inter fonts.

## Installation

From the project root:

```bash
cd frontend
npm install
```

## Development Server

Start the local Vite development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`.

### Backend Proxy Configuration

During development, API requests directed to `/api/*` are automatically forwarded to the FastAPI backend running on port 8000. This is configured in `vite.config.js`:

```javascript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    },
  },
}
```

Ensure the FastAPI backend server is running concurrently (for example, via `uvicorn server:app --reload --port 8000`).

## Production Build

Compile the React frontend into static assets:

```bash
npm run build
```

The compiled bundles and HTML shell are written to `frontend/dist/`. In production mode, the FastAPI backend server directly mounts and serves this directory at the root URL (`http://localhost:8000/`).

## Linting

Run Oxlint to check for code quality and syntax issues:

```bash
npm run lint
```

## Folder Structure

```
frontend/
├── index.html                   # HTML entry point loading Google Fonts
├── package.json                 # Node dependencies and scripts
├── vite.config.js               # Vite config and API dev proxy
├── public/
│   ├── favicon.svg              # Application favicon
│   └── icons.svg                # Vector symbol definitions
└── src/
    ├── App.jsx                  # Root application component and state coordinator
    ├── index.css                # Global design system, theme variables, and markdown styling
    ├── main.jsx                 # React DOM mount point
    ├── services/
    │   └── api.js               # Centralized REST API service communicating with FastAPI
    └── components/
        ├── layout/
        │   └── AppHeader.jsx    # Editorial header, responsive drawer, and API key trigger
        ├── upload/
        │   └── UploadZone.jsx   # Drag-and-drop PDF upload zone with extraction status
        ├── analysis/
        │   ├── DocumentHeader.jsx # Title, author tags, and analysis trigger with retry
        │   ├── MetricsRow.jsx   # Page count, word count, sentence count, vocabulary size
        │   ├── OverviewTab.jsx  # Executive summary, problem statement, and conclusions
        │   ├── AnalysisTab.jsx  # 2-column grid of objectives, methodology, and limitations
        │   └── KeywordsTab.jsx  # Technical keyword tags with one-click copy
        ├── chat/
        │   ├── ChatTab.jsx      # Grounded Q&A conversation panel with prompt suggestions
        │   └── ChatMessage.jsx  # Markdown renderer with code block copying and tables
        ├── report/
        │   └── ReportTab.jsx    # Markdown report previewer and download trigger
        └── common/
            └── ApiKeyModal.jsx  # Modal for entering and testing Gemini API keys
```

## How the Frontend Communicates with FastAPI

All network interactions are centralized in `src/services/api.js`. This module provides async helper functions:

1. `fetchSystemConfig()`: Queries `GET /api/config` on mount to verify API key status and active document state.
2. `updateApiKey(apiKey)`: Sends `POST /api/config/api-key` to update and test credentials in memory.
3. `uploadPdfDocument(file)`: Sends `POST /api/upload` as `multipart/form-data` with the selected PDF file.
4. `analyzeResearchPaper(docId)`: Sends `POST /api/analyze` to trigger Gemini structured extraction.
5. `sendChatMessage(docId, question)`: Sends `POST /api/chat` with user queries for context-grounded answers.
6. `clearChatHistory(docId)`: Sends `POST /api/chat/clear` to reset conversation turns.
7. `resetWorkspaceSession()`: Sends `POST /api/reset` to flush current document state.
8. `getReportDownloadUrl(docId)`: Generates the URL for `GET /api/report/download?doc_id=...` to download the generated Markdown report.

Responses are handled uniformly with clear error message extraction to prevent unhandled exceptions or broken UI states.
