/**
 * PaperMind AI API Service.
 * Centralized, type-safe API communication with the FastAPI backend.
 */

const BASE_URL = '';

/**
 * Handle API responses with uniform error extraction.
 */
async function handleResponse(response, defaultErrorMsg = 'Request failed') {
  if (!response.ok) {
    let errorDetail = defaultErrorMsg;
    try {
      const data = await response.json();
      errorDetail = data.detail?.message || data.detail || defaultErrorMsg;
    } catch {
      // Non-JSON response
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

/**
 * Fetch application configuration and Gemini API readiness.
 */
export async function fetchSystemConfig() {
  const response = await fetch(`${BASE_URL}/api/config`);
  return handleResponse(response, 'Failed to retrieve system configuration');
}

/**
 * Update the active Gemini API key in-memory.
 */
export async function updateApiKey(apiKey) {
  const response = await fetch(`${BASE_URL}/api/config/api-key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: apiKey }),
  });
  return handleResponse(response, 'Failed to update API key');
}

/**
 * Verify connectivity to the Google Gemini API.
 */
export async function testApiConnection() {
  const response = await fetch(`${BASE_URL}/api/config/test-connection`, {
    method: 'POST',
  });
  return handleResponse(response, 'API connection test failed');
}

/**
 * Upload an academic PDF document for text extraction and NLP statistics.
 */
export async function uploadPdfDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(response, 'Failed to extract text from PDF document');
}

/**
 * Retrieve metadata, statistics, and analysis state for an active document.
 */
export async function getDocumentDetails(docId) {
  const response = await fetch(`${BASE_URL}/api/document/${encodeURIComponent(docId)}`);
  return handleResponse(response, 'Failed to fetch document details');
}

/**
 * Trigger structured AI research component extraction via Gemini.
 */
export async function analyzeResearchPaper(docId) {
  const response = await fetch(`${BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ doc_id: docId }),
  });
  return handleResponse(response, 'Failed to analyze research paper');
}

/**
 * Send a question to the document-grounded Q&A engine.
 */
export async function sendChatMessage(docId, question) {
  const response = await fetch(`${BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ doc_id: docId, question }),
  });
  return handleResponse(response, 'Failed to answer question');
}

/**
 * Clear conversational history for an active document.
 */
export async function clearChatHistory(docId) {
  const response = await fetch(`${BASE_URL}/api/chat/clear`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ doc_id: docId }),
  });
  return handleResponse(response, 'Failed to clear chat history');
}

/**
 * Reset workspace session and clear in-memory document state.
 */
export async function resetWorkspaceSession() {
  const response = await fetch(`${BASE_URL}/api/reset`, {
    method: 'POST',
  });
  return handleResponse(response, 'Failed to reset workspace');
}

/**
 * Generate report download URL.
 */
export function getReportDownloadUrl(docId) {
  return `${BASE_URL}/api/report/download?doc_id=${encodeURIComponent(docId)}`;
}
