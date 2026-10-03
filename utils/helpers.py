"""Helper utilities for configuration loading, prompt retrieval, and formatting."""
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv

# Automatically load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def get_base_dir() -> Path:
    """Return the root directory of the application."""
    return BASE_DIR


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely load configuration from a YAML file.
    Falls back to robust default values if file is missing or invalid.
    """
    default_config: Dict[str, Any] = {
        "app": {
            "name": "PaperMind AI",
            "version": "1.0.0",
            "description": "NLP-Based Research Paper Intelligence Assistant",
            "max_file_size_mb": 20,
        },
        "model": {
            "name": "gemini-2.5-flash",
            "temperature": 0.2,
            "max_output_tokens": 4096,
            "top_p": 0.95,
        },
        "nlp": {
            "max_keywords": 10,
            "min_extracted_text_chars": 100,
            "chunk_size_tokens": 3000,
            "chunk_overlap_tokens": 200,
        },
        "qa": {
            "max_history_turns": 10,
            "context_window_chars": 12000,
        },
    }

    if config_path is None:
        target_path = BASE_DIR / "config" / "config.yaml"
    else:
        target_path = Path(config_path)

    if not target_path.exists():
        return default_config

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f)
            if isinstance(user_config, dict):
                # Deep merge top-level keys
                for key, val in user_config.items():
                    if key in default_config and isinstance(val, dict):
                        default_config[key].update(val)
                    else:
                        default_config[key] = val
        return default_config
    except Exception:
        return default_config


def load_prompt(prompt_name: str) -> str:
    """
    Load an external prompt template from the prompts/ directory.
    
    Args:
        prompt_name: Name of the file, e.g. 'system_prompt.txt', 'analysis_prompt.txt'.
    
    Returns:
        The content of the prompt as a string.
    """
    prompt_file = BASE_DIR / "prompts" / prompt_name
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found at: {prompt_file}")
    
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_api_key() -> Optional[str]:
    """Retrieve GEMINI_API_KEY from environment variables."""
    # Ensure fresh dotenv load if user modified .env
    load_dotenv(override=False)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip():
        return api_key.strip()
    return None


def format_file_size(size_in_bytes: int) -> str:
    """Format bytes into readable string (KB, MB)."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"


def clean_json_markdown(text: str) -> str:
    """
    Remove markdown code fences (e.g. ```json ... ``` or ``` ...) 
    from LLM responses to ensure valid JSON parsing.
    """
    text = text.strip()
    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text
