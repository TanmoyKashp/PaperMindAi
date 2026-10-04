"""Google Gemini API Client for PaperMind AI.

Uses the official Google Gen AI Python SDK (`google-genai`).
Handles client initialization, configuration loading, error classification,
and robust generation with low temperature for research accuracy.
"""

from typing import Any, Dict, Optional, Tuple
import os

from utils.helpers import get_api_key, load_config


class GeminiAPIError(Exception):
    """Base exception for Gemini API related errors."""
    pass


class GeminiAPIKeyError(GeminiAPIError):
    """Exception raised when API key is missing or invalid."""
    pass


class GeminiQuotaError(GeminiAPIError):
    """Exception raised when rate limits or quotas are exceeded."""
    pass


class GeminiClient:
    """Wrapper around the official Google Gen AI SDK (google-genai)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        config_path: Optional[str] = None,
    ):
        self.config = load_config(config_path)
        if api_key is not None:
            self.api_key = api_key.strip() if api_key else None
        else:
            self.api_key = get_api_key()
        
        # Priority: explicit argument -> config.yaml -> fallback
        configured_model = self.config.get("model", {}).get("name", "gemini-2.5-flash")
        self.model_name = model_name or configured_model

        model_cfg = self.config.get("model", {})
        self.temperature = model_cfg.get("temperature", 0.2)
        self.max_output_tokens = model_cfg.get("max_output_tokens", 4096)
        self.top_p = model_cfg.get("top_p", 0.95)

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
        """Update the active API key and reinitialize the client."""
        if new_key and new_key.strip():
            self.api_key = new_key.strip()
            self._init_client()
        else:
            self.api_key = None
            self._client = None

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
                    max_output_tokens=10,
                    temperature=0.0,
                ),
            )

            if response and (response.text is not None):
                return True, f"Connected successfully to Google Gemini ({self.model_name})."
            else:
                return False, "Gemini returned an empty test response."

        except Exception as e:
            err_msg = str(e)
            if "API_KEY_INVALID" in err_msg or "400" in err_msg or "403" in err_msg or "invalid api key" in err_msg.lower():
                return False, "Invalid Gemini API Key. Please verify your key in Google AI Studio."
            elif "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                return False, "Gemini API rate limit or quota exceeded. Please try again shortly."
            else:
                return False, f"API Connection failed: {err_msg}"

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Generate text or JSON response from Gemini.
        
        Args:
            prompt: User/task prompt.
            system_instruction: Optional system instruction.
            temperature: Sampling temperature (defaults to config low temp: 0.2).
            json_mode: If True, requests JSON response mime-type.
            
        Returns:
            The raw string response from the model.
        """
        if not self.is_configured():
            raise GeminiAPIKeyError(
                "Gemini API key is missing. Please set the GEMINI_API_KEY environment variable "
                "in your .env file or input it directly in the application sidebar."
            )

        if self._client is None:
            self._init_client()

        temp = temperature if temperature is not None else self.temperature

        try:
            from google.genai import types

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
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            if response is None:
                raise GeminiAPIError("Received null response from Gemini API.")

            # Check response text
            text = response.text
            if not text:
                # Check candidate finish reason
                if hasattr(response, "candidates") and response.candidates:
                    finish_reason = getattr(response.candidates[0], "finish_reason", "UNKNOWN")
                    raise GeminiAPIError(
                        f"Gemini returned an empty response. Candidate finish reason: {finish_reason}"
                    )
                raise GeminiAPIError("Gemini returned an empty response with no text content.")

            return text.strip()

        except GeminiAPIError:
            raise
        except Exception as e:
            err_msg = str(e)
            if "API_KEY_INVALID" in err_msg or "400" in err_msg or "403" in err_msg or "invalid api key" in err_msg.lower():
                raise GeminiAPIKeyError("Invalid Gemini API key provided. Please verify your credentials.")
            elif "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                raise GeminiQuotaError("Gemini API rate limit or quota exceeded. Please wait a moment and retry.")
            else:
                raise GeminiAPIError(f"Gemini API generation error: {err_msg}")
