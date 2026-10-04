"""Google Gemini API Client for PaperMind AI.

Uses the official Google Gen AI Python SDK (`google-genai`).
Handles client initialization, configuration loading, error classification,
bounded exponential backoff for transient failures (503, 429, timeouts),
and robust generation with low temperature for research accuracy.
"""

import logging
import re
import time
from typing import Any, Callable, Dict, Optional, Tuple

from utils.helpers import get_api_key, load_config

logger = logging.getLogger(__name__)

# Standard user-facing error messages
MSG_UNAVAILABLE = (
    "The AI model is temporarily experiencing high demand. "
    "Your document is still available. Please retry in a moment."
)
MSG_QUOTA_EXCEEDED = "Gemini API rate limit reached. Please wait before trying again."
MSG_AUTH_FAILED = (
    "Your Gemini API key could not be authenticated. Please verify your API configuration."
)
MSG_TIMEOUT = (
    "Connection to the AI service timed out. "
    "Your document is still available. Please retry in a moment."
)


class GeminiAPIError(Exception):
    """Base exception for Gemini API related errors."""
    pass


class GeminiAPIKeyError(GeminiAPIError):
    """Exception raised when API key is missing, unauthorized, or invalid."""
    pass


class GeminiQuotaError(GeminiAPIError):
    """Exception raised when rate limits or quotas are exceeded (HTTP 429)."""
    pass


class GeminiUnavailableError(GeminiAPIError):
    """Exception raised when the model is temporarily unavailable or overloaded (HTTP 503)."""
    pass


class GeminiTransientError(GeminiAPIError):
    """Exception raised when transient network connections or timeouts occur."""
    pass


class GeminiClient:
    """Wrapper around the official Google Gen AI SDK (google-genai) with resilience."""

    # Default bounded backoff delays in seconds (approximately 2s, 4s, 8s)
    DEFAULT_RETRY_DELAYS = (2.0, 4.0, 8.0)

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        config_path: Optional[str] = None,
        max_retries: int = 3,
        retry_delays: Optional[Tuple[float, ...]] = None,
        sleep_fn: Optional[Callable[[float], None]] = None,
    ):
        self.config = load_config(config_path)
        if api_key is not None:
            self.api_key = api_key.strip() if api_key else None
        else:
            self.api_key = get_api_key()

        # Priority: explicit argument -> config.yaml -> fallback default
        configured_model = self.config.get("model", {}).get("name", "gemini-2.5-flash")
        self.model_name = model_name or configured_model

        # Optional secondary fallback model if explicitly configured in config.yaml
        self.fallback_model = self.config.get("model", {}).get("fallback_model")

        model_cfg = self.config.get("model", {})
        self.temperature = model_cfg.get("temperature", 0.2)
        self.max_output_tokens = model_cfg.get("max_output_tokens", 4096)
        self.top_p = model_cfg.get("top_p", 0.95)

        # Retry configuration
        self.max_retries = max(0, max_retries)
        self.retry_delays = retry_delays if retry_delays is not None else self.DEFAULT_RETRY_DELAYS
        self.sleep_fn = sleep_fn if sleep_fn is not None else time.sleep

        self._client = None
        if self.api_key:
            self._init_client()

    def _init_client(self):
        """Initialize the official Google Gen AI client."""
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        except Exception as e:
            self._client = None
            raise GeminiAPIError(f"Failed to initialize Google Gen AI SDK: {str(e)}")

    def is_configured(self) -> bool:
        """Check if an API key is available."""
        return bool(self.api_key and self.api_key.strip())

    def update_api_key(self, new_key: str):
        """Update active API key and reinitialize client."""
        if new_key and new_key.strip():
            self.api_key = new_key.strip()
            self._init_client()
        else:
            self.api_key = None
            self._client = None

    @staticmethod
    def _extract_retry_after(exc: Exception) -> Optional[float]:
        """Extract Retry-After delay in seconds if provided by headers or error message."""
        # Check response headers if attached to exception
        response = getattr(exc, "response", None)
        headers = getattr(exc, "headers", None) or (getattr(response, "headers", None) if response else None)
        if headers and hasattr(headers, "get"):
            val = headers.get("retry-after") or headers.get("Retry-After")
            if val is not None:
                try:
                    sec = float(val)
                    if 0 < sec <= 60:
                        return sec
                except (ValueError, TypeError):
                    pass

        # Check direct attributes
        for attr in ("retry_delay", "retry_after", "delay"):
            val = getattr(exc, attr, None)
            if val is not None:
                try:
                    sec = float(val)
                    if 0 < sec <= 60:
                        return sec
                except (ValueError, TypeError):
                    pass

        # Check regex match in exception string (e.g., "retry after 5s" or "Retry-After: 5")
        msg = str(exc)
        match = re.search(r"retry(?:-|\s+)after[:\s]+(\d+(?:\.\d+)?)", msg, re.IGNORECASE)
        if match:
            try:
                sec = float(match.group(1))
                if 0 < sec <= 60:
                    return sec
            except (ValueError, TypeError):
                pass

        return None

    @classmethod
    def classify_error(cls, exc: Exception) -> Tuple[bool, str, Optional[float]]:
        """
        Classify error into (is_transient, category, retry_after).
        
        Categories:
        - 'auth': 401/403/invalid key (DO NOT RETRY)
        - 'client_error': 400/malformed request/invalid argument (DO NOT RETRY)
        - 'unavailable': 503/model high demand (RETRY)
        - 'quota': 429/rate limit/resource exhausted (RETRY)
        - 'timeout': network timeout/connection reset (RETRY)
        - 'unknown': other errors (DO NOT RETRY unless 5xx)
        """
        code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
        status = getattr(exc, "status", None)
        msg = str(exc).lower()

        # 1. Non-retryable authentication & permission errors
        if isinstance(exc, GeminiAPIKeyError):
            return False, "auth", None
        if code in (401, 403) or (status and status in ("PERMISSION_DENIED", "UNAUTHENTICATED")):
            return False, "auth", None
        if any(term in msg for term in ("api_key_invalid", "invalid api key", "unauthenticated", "permission denied")):
            return False, "auth", None

        # 2. Non-retryable bad requests & client errors
        if code in (400, 404) or (status and status in ("INVALID_ARGUMENT", "NOT_FOUND", "FAILED_PRECONDITION")):
            return False, "client_error", None
        if "invalid argument" in msg or "malformed" in msg:
            return False, "client_error", None

        # 3. Retryable HTTP 503 / Service Unavailable / High demand
        retry_after = cls._extract_retry_after(exc)
        if code == 503 or (status and status == "UNAVAILABLE"):
            return True, "unavailable", retry_after
        if any(term in msg for term in ("503", "unavailable", "high demand", "temporarily overloaded", "service unavailable")):
            return True, "unavailable", retry_after

        # 4. Retryable HTTP 429 / Rate limit / Resource exhausted
        if code == 429 or (status and status == "RESOURCE_EXHAUSTED"):
            return True, "quota", retry_after
        if any(term in msg for term in ("429", "resource_exhausted", "rate limit", "quota")):
            return True, "quota", retry_after

        # 5. Retryable Network timeouts & connection failures
        exc_type = exc.__class__.__name__.lower()
        if isinstance(exc, (TimeoutError, ConnectionError)) or any(t in exc_type for t in ("timeout", "connect", "network")):
            return True, "timeout", retry_after
        if any(term in msg for term in ("timed out", "timeout", "connection reset", "connection refused", "broken pipe")):
            return True, "timeout", retry_after
        if code in (502, 504) or (status and status in ("BAD_GATEWAY", "GATEWAY_TIMEOUT")):
            return True, "timeout", retry_after

        # 6. Other 5xx server errors
        if isinstance(code, int) and 500 <= code < 600:
            return True, "unavailable", retry_after

        return False, "unknown", None

    def test_connection(self) -> Tuple[bool, str]:
        """
        Verify that the API key is active and capable of making calls.
        Returns (success: bool, message: str).
        """
        if not self.is_configured():
            return False, "GEMINI_API_KEY is not set. Add it to .env or enter it in the sidebar."

        try:
            if self._client is None:
                self._init_client()

            from google.genai import types

            response = self._client.models.generate_content(
                model=self.model_name,
                contents="Ping",
                config=types.GenerateContentConfig(
                    max_output_tokens=100,
                    temperature=0.0,
                ),
            )

            if response and (response.text is not None or (hasattr(response, "candidates") and response.candidates)):
                return True, f"Connected successfully to Google Gemini ({self.model_name})."
            else:
                return False, "Gemini returned an empty test response."

        except Exception as e:
            _, category, _ = self.classify_error(e)
            if category == "auth":
                return False, MSG_AUTH_FAILED
            elif category == "quota":
                return False, MSG_QUOTA_EXCEEDED
            elif category == "unavailable":
                return False, MSG_UNAVAILABLE
            else:
                return False, f"API Connection failed: {str(e)}"

    def _execute_api_call(
        self,
        prompt: str,
        model_name: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> str:
        """Execute single raw generation call without retry loop."""
        from google.genai import types

        temp = temperature if temperature is not None else self.temperature
        config_kwargs: Dict[str, Any] = {
            "temperature": temp,
            "max_output_tokens": self.max_output_tokens,
            "top_p": self.top_p,
        }

        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        if json_mode:
            config_kwargs["response_mime_type"] = "application/json"

        config = types.GenerateContentConfig(**config_kwargs)

        response = self._client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )

        if response is None:
            raise GeminiAPIError("Received null response from Gemini API.")

        text = response.text
        if not text:
            if hasattr(response, "candidates") and response.candidates:
                finish_reason = getattr(response.candidates[0], "finish_reason", "UNKNOWN")
                raise GeminiAPIError(
                    f"Gemini returned an empty response. Candidate finish reason: {finish_reason}"
                )
            raise GeminiAPIError("Gemini returned an empty response with no text content.")

        return text.strip()

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Generate text or JSON response with bounded exponential backoff for transient errors.
        
        Args:
            prompt: User or task prompt.
            system_instruction: Optional system instruction.
            temperature: Sampling temperature.
            json_mode: If True, request JSON response MIME type.
            
        Returns:
            The model's generated text response.
            
        Raises:
            GeminiAPIKeyError: On authentication/permission failure (not retried).
            GeminiUnavailableError: On 503/high demand exhaustion.
            GeminiQuotaError: On 429 rate limit exhaustion.
            GeminiTransientError: On network timeout/connection exhaustion.
            GeminiAPIError: On permanent or generic failures.
        """
        if not self.is_configured():
            raise GeminiAPIKeyError(MSG_AUTH_FAILED)

        if self._client is None:
            self._init_client()

        # Retry loop for primary model
        last_exception: Optional[Exception] = None
        last_category: str = "unknown"

        for attempt in range(self.max_retries + 1):
            try:
                return self._execute_api_call(
                    prompt=prompt,
                    model_name=self.model_name,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    json_mode=json_mode,
                )
            except Exception as exc:
                last_exception = exc
                is_transient, category, retry_after = self.classify_error(exc)
                last_category = category

                # Never retry non-transient errors (invalid key, malformed request, etc.)
                if not is_transient:
                    if category == "auth":
                        logger.error("Non-retryable authentication failure: %s", exc)
                        raise GeminiAPIKeyError(MSG_AUTH_FAILED) from exc
                    elif category == "client_error":
                        logger.error("Non-retryable client error: %s", exc)
                        raise GeminiAPIError(f"Invalid request to Gemini API: {str(exc)}") from exc
                    else:
                        logger.error("Non-retryable Gemini error: %s", exc)
                        raise GeminiAPIError(f"Gemini API error: {str(exc)}") from exc

                # Check if retries remain
                if attempt < self.max_retries:
                    # Determine delay: respect Retry-After or use exponential backoff
                    if retry_after is not None and retry_after > 0:
                        delay = min(retry_after, 60.0)
                        logger.info("Using server Retry-After delay: %.2fs", delay)
                    else:
                        delay_idx = min(attempt, len(self.retry_delays) - 1)
                        delay = self.retry_delays[delay_idx]

                    logger.warning(
                        "Gemini API transient %s error (attempt %d/%d). Retrying in %.2fs. Error: %s",
                        category,
                        attempt + 1,
                        self.max_retries,
                        delay,
                        str(exc),
                    )
                    self.sleep_fn(delay)
                else:
                    logger.error(
                        "Gemini API retries exhausted (%d attempts) for model %s.",
                        self.max_retries + 1,
                        self.model_name,
                    )

        # Retries exhausted on primary model: check for controlled fallback model (Section 5)
        if (
            self.fallback_model
            and self.fallback_model != self.model_name
            and last_category == "unavailable"
        ):
            logger.warning(
                "Attempting controlled fallback model '%s' after primary '%s' availability failure.",
                self.fallback_model,
                self.model_name,
            )
            try:
                return self._execute_api_call(
                    prompt=prompt,
                    model_name=self.fallback_model,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    json_mode=json_mode,
                )
            except Exception as fb_exc:
                logger.error("Configured fallback model '%s' also failed: %s", self.fallback_model, fb_exc)

        # Raise appropriate user-facing exception
        if last_category == "unavailable":
            raise GeminiUnavailableError(MSG_UNAVAILABLE) from last_exception
        elif last_category == "quota":
            raise GeminiQuotaError(MSG_QUOTA_EXCEEDED) from last_exception
        elif last_category == "timeout":
            raise GeminiTransientError(MSG_TIMEOUT) from last_exception
        else:
            raise GeminiAPIError(
                f"Gemini API request failed after {self.max_retries} retries: {str(last_exception)}"
            ) from last_exception
