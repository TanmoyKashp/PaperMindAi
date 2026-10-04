"""Unit tests for Gemini API Reliability, Bounded Exponential Backoff, and Error Handling.

These tests use deterministic mocked responses to verify:
1. Simulated 503 followed by successful retry.
2. Repeated 503 exhausting all retries.
3. 429 rate limit (RESOURCE_EXHAUSTED).
4. Invalid API key (immediate failure, no retries).
5. Malformed client request (immediate failure, no retries).
6. Network timeout and connection errors.
7. Retry-After header / delay parsing and respect.
8. Controlled model fallback behavior.
9. Prevention of concurrent duplicate analysis requests on FastAPI server.
10. Preservation of uploaded PDF and text metadata after failure.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from modules.gemini_client import (
    GeminiClient,
    GeminiAPIError,
    GeminiAPIKeyError,
    GeminiQuotaError,
    GeminiUnavailableError,
    GeminiTransientError,
    MSG_UNAVAILABLE,
    MSG_QUOTA_EXCEEDED,
    MSG_AUTH_FAILED,
    MSG_TIMEOUT,
)
from modules.paper_analyzer import PaperAnalyzer, PaperAnalysisResult
from server import app, DOCUMENTS


class MockSDKError(Exception):
    """Simulates google.genai.errors.APIError."""
    def __init__(self, code: int, status: str, message: str, headers: dict = None):
        super().__init__(f"{code} {status}: {message}")
        self.code = code
        self.status = status
        self.message = message
        self.headers = headers or {}
        self.response = MagicMock()
        self.response.headers = self.headers


# ============================================================================
# 1. RETRY MECHANISM TESTS (Bounded Exponential Backoff)
# ============================================================================

def test_simulated_503_followed_by_successful_retry():
    """Verify transient 503 error is retried and succeeds on attempt 2."""
    sleep_calls = []
    client = GeminiClient(
        api_key="valid_key",
        max_retries=3,
        retry_delays=(2.0, 4.0, 8.0),
        sleep_fn=lambda s: sleep_calls.append(s),
    )

    # 1st attempt: 503 UNAVAILABLE
    # 2nd attempt: Success
    mock_success_response = MagicMock()
    mock_success_response.text = '{"title": "Attention Is All You Need"}'

    error_503 = MockSDKError(503, "UNAVAILABLE", "This model is currently experiencing high demand.")

    with patch.object(
        client._client.models,
        "generate_content",
        side_effect=[error_503, mock_success_response],
    ) as mock_gen:
        result = client.generate_content("Analyze paper")
        assert result == '{"title": "Attention Is All You Need"}'
        assert mock_gen.call_count == 2
        assert len(sleep_calls) == 1
        assert sleep_calls[0] == 2.0  # First backoff delay


def test_repeated_503_exhausting_all_retries():
    """Verify repeated 503 exhausts 3 retries (4 total attempts) and raises GeminiUnavailableError."""
    sleep_calls = []
    client = GeminiClient(
        api_key="valid_key",
        max_retries=3,
        retry_delays=(2.0, 4.0, 8.0),
        sleep_fn=lambda s: sleep_calls.append(s),
    )

    error_503 = MockSDKError(503, "UNAVAILABLE", "This model is currently experiencing high demand.")

    with patch.object(
        client._client.models,
        "generate_content",
        side_effect=[error_503, error_503, error_503, error_503],
    ) as mock_gen:
        with pytest.raises(GeminiUnavailableError) as exc_info:
            client.generate_content("Analyze paper")

        assert MSG_UNAVAILABLE in str(exc_info.value)
        assert mock_gen.call_count == 4  # 1 initial + 3 retries
        assert sleep_calls == [2.0, 4.0, 8.0]  # Full backoff sequence


def test_429_rate_limit_exhausting_retries():
    """Verify 429 RESOURCE_EXHAUSTED retries and raises GeminiQuotaError with clear message."""
    sleep_calls = []
    client = GeminiClient(
        api_key="valid_key",
        max_retries=3,
        retry_delays=(2.0, 4.0, 8.0),
        sleep_fn=lambda s: sleep_calls.append(s),
    )

    error_429 = MockSDKError(429, "RESOURCE_EXHAUSTED", "Quota exceeded for quota metric.")

    with patch.object(
        client._client.models,
        "generate_content",
        side_effect=error_429,
    ) as mock_gen:
        with pytest.raises(GeminiQuotaError) as exc_info:
            client.generate_content("Analyze paper")

        assert MSG_QUOTA_EXCEEDED in str(exc_info.value)
        assert mock_gen.call_count == 4
        assert sleep_calls == [2.0, 4.0, 8.0]


def test_retry_after_header_respected():
    """Verify Retry-After header delay is used instead of default backoff delay."""
    sleep_calls = []
    client = GeminiClient(
        api_key="valid_key",
        max_retries=3,
        retry_delays=(2.0, 4.0, 8.0),
        sleep_fn=lambda s: sleep_calls.append(s),
    )

    # Server instructs client to wait 5 seconds via header
    error_with_retry_after = MockSDKError(
        503,
        "UNAVAILABLE",
        "High demand",
        headers={"retry-after": "5"},
    )
    mock_resp = MagicMock()
    mock_resp.text = "Success after retry-after"

    with patch.object(
        client._client.models,
        "generate_content",
        side_effect=[error_with_retry_after, mock_resp],
    ):
        res = client.generate_content("Prompt")
        assert res == "Success after retry-after"
        assert sleep_calls == [5.0]


# ============================================================================
# 2. NON-RETRYABLE CLIENT ERROR TESTS
# ============================================================================

def test_invalid_api_key_not_retried():
    """Verify authentication errors fail immediately without retrying."""
    sleep_calls = []
    client = GeminiClient(
        api_key="invalid_bad_key",
        max_retries=3,
        sleep_fn=lambda s: sleep_calls.append(s),
    )

    error_400_key = MockSDKError(400, "API_KEY_INVALID", "API key not valid. Please pass a valid API key.")

    with patch.object(
        client._client.models,
        "generate_content",
        side_effect=error_400_key,
    ) as mock_gen:
        with pytest.raises(GeminiAPIKeyError) as exc_info:
            client.generate_content("Analyze")

        assert MSG_AUTH_FAILED in str(exc_info.value)
        assert mock_gen.call_count == 1  # Only 1 attempt, zero retries
        assert len(sleep_calls) == 0


def test_malformed_client_error_not_retried():
    """Verify 400 INVALID_ARGUMENT fails immediately without retrying."""
    sleep_calls = []
    client = GeminiClient(
        api_key="valid_key",
        max_retries=3,
        sleep_fn=lambda s: sleep_calls.append(s),
    )

    error_400 = MockSDKError(400, "INVALID_ARGUMENT", "Contents cannot be empty.")

    with patch.object(
        client._client.models,
        "generate_content",
        side_effect=error_400,
    ) as mock_gen:
        with pytest.raises(GeminiAPIError):
            client.generate_content("Analyze")

        assert mock_gen.call_count == 1
        assert len(sleep_calls) == 0


def test_network_timeout_retried_and_raises_transient_error():
    """Verify connection timeouts are retried up to max_retries and raise GeminiTransientError."""
    sleep_calls = []
    client = GeminiClient(
        api_key="valid_key",
        max_retries=3,
        retry_delays=(2.0, 4.0, 8.0),
        sleep_fn=lambda s: sleep_calls.append(s),
    )

    timeout_err = TimeoutError("The read operation timed out")

    with patch.object(
        client._client.models,
        "generate_content",
        side_effect=timeout_err,
    ) as mock_gen:
        with pytest.raises(GeminiTransientError) as exc_info:
            client.generate_content("Analyze")

        assert MSG_TIMEOUT in str(exc_info.value)
        assert mock_gen.call_count == 4
        assert sleep_calls == [2.0, 4.0, 8.0]


# ============================================================================
# 3. MODEL FALLBACK TESTS
# ============================================================================

def test_no_fallback_model_configured_by_default():
    """Verify when no fallback model is configured, model is not silently changed."""
    client = GeminiClient(api_key="valid_key")
    assert client.fallback_model is None
    assert client.model_name in ["gemini-3.5-flash", "gemini-2.5-flash"]


def test_controlled_fallback_when_explicitly_configured():
    """Verify that if a secondary model is configured, controlled fallback activates on 503."""
    sleep_calls = []
    client = GeminiClient(
        api_key="valid_key",
        model_name="gemini-3.5-flash",
        max_retries=1,
        retry_delays=(1.0,),
        sleep_fn=lambda s: sleep_calls.append(s),
    )
    client.fallback_model = "gemini-2.5-flash"

    error_503 = MockSDKError(503, "UNAVAILABLE", "Model overloaded")
    success_resp = MagicMock()
    success_resp.text = "Fallback model response"

    def side_effect_fn(model, contents, config):
        if model == "gemini-3.5-flash":
            raise error_503
        elif model == "gemini-2.5-flash":
            return success_resp
        raise ValueError(f"Unexpected model {model}")

    with patch.object(
        client._client.models,
        "generate_content",
        side_effect=side_effect_fn,
    ):
        res = client.generate_content("Prompt")
        assert res == "Fallback model response"


# ============================================================================
# 4. FASTAPI ENDPOINT & DUPLICATE REQUEST PREVENTION TESTS
# ============================================================================

def test_server_prevents_duplicate_analysis_while_processing():
    """Verify 409 Conflict is returned when analysis is already in progress for a document."""
    test_client = TestClient(app)
    doc_id = "test_doc_duplicate_prevention"
    DOCUMENTS[doc_id] = {
        "doc_id": doc_id,
        "filename": "sample_paper.pdf",
        "full_text": "Attention Is All You Need. Ashish Vaswani et al.",
        "page_count": 5,
        "total_words": 1500,
        "stats": {"word_count": 1500},
        "analysis": None,
        "chat_history": [],
        "is_analyzing": True,  # Analysis already in flight!
    }

    try:
        res = test_client.post("/api/analyze", json={"doc_id": doc_id})
        assert res.status_code == 409
        assert "already in progress" in res.json()["detail"].lower()
    finally:
        DOCUMENTS.pop(doc_id, None)


def test_server_preserves_document_after_503_analysis_failure():
    """Verify that when 503 occurs during analysis, the document and extracted text are preserved."""
    test_client = TestClient(app)
    doc_id = "test_doc_preservation"
    doc_record = {
        "doc_id": doc_id,
        "filename": "transformer_paper.pdf",
        "full_text": "Attention Is All You Need. Vaswani et al. Transformer self-attention architecture.",
        "page_count": 8,
        "total_words": 3200,
        "stats": {"word_count": 3200, "sentence_count": 120, "vocabulary_size": 800},
        "analysis": None,
        "chat_history": [],
        "is_analyzing": False,
    }
    DOCUMENTS[doc_id] = doc_record

    # Mock analyzer to raise GeminiUnavailableError
    with patch("server.analyzer.analyze_paper", side_effect=GeminiUnavailableError(MSG_UNAVAILABLE)):
        res = test_client.post("/api/analyze", json={"doc_id": doc_id})
        assert res.status_code == 503
        assert MSG_UNAVAILABLE in res.json()["detail"]

        # Crucial checks: Document data MUST be fully preserved!
        preserved_doc = DOCUMENTS[doc_id]
        assert preserved_doc["filename"] == "transformer_paper.pdf"
        assert preserved_doc["full_text"].startswith("Attention Is All You Need")
        assert preserved_doc["page_count"] == 8
        assert preserved_doc["stats"]["word_count"] == 3200
        assert preserved_doc["analysis"] is None  # No false success
        assert preserved_doc["is_analyzing"] is False  # In-flight lock cleared for retry

    # Verify subsequent retry succeeds when service recovers
    mock_analysis_result = PaperAnalysisResult(
        title="Attention Is All You Need",
        problem_statement="Recurrent models are sequential and slow.",
        research_objectives=["Eliminate recurrence using self-attention"],
        methodology="Transformer architecture with multi-head self-attention.",
        algorithms_models=["Transformer"],
        datasets="WMT 2014 En-De and En-Fr",
        key_findings=["State-of-the-art BLEU score of 28.4"],
        limitations=["Quadratic memory complexity with sequence length"],
        future_scope=["Extend attention to other modalities"],
        keywords=["Attention", "Transformer", "Machine Translation"],
    )

    with patch("server.analyzer.analyze_paper", return_value=mock_analysis_result):
        retry_res = test_client.post("/api/analyze", json={"doc_id": doc_id})
        assert retry_res.status_code == 200
        data = retry_res.json()
        assert data["success"] is True
        assert data["analysis"]["title"] == "Attention Is All You Need"
        assert DOCUMENTS[doc_id]["analysis"] is not None

    DOCUMENTS.pop(doc_id, None)
