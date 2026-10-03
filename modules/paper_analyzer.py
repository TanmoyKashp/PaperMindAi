"""Paper Analyzer Module for PaperMind AI.

Coordinates LLM-based research paper analysis:
- Extracts research problem, objectives, methodology, models, dataset, findings, limitations, future directions
- Generates structured overview, contributions, and conclusion
- Extracts top academic keywords (filtering generic terms)
- Supports multi-chunk synthesis for long research papers
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from modules.gemini_client import GeminiClient
from modules.pdf_processor import PDFProcessor
from utils.helpers import clean_json_markdown, load_config, load_prompt

logger = logging.getLogger(__name__)


class SummaryDetails(BaseModel):
    """Detailed summary sections of the paper."""
    overview: str = Field(
        default="Not explicitly stated in the paper.",
        description="High-level overview of the entire paper.",
    )
    contributions: List[str] = Field(
        default_factory=lambda: ["Not explicitly stated in the paper."],
        description="Key scientific or technical contributions.",
    )
    conclusion: str = Field(
        default="Not explicitly stated in the paper.",
        description="Final concluding takeaway from the authors.",
    )


class PaperAnalysisResult(BaseModel):
    """Structured research components extracted from an academic paper."""
    title: str = Field(default="Untitled Research Paper")
    problem_statement: str = Field(default="Not explicitly stated in the paper.")
    research_objectives: List[str] = Field(default_factory=list)
    methodology: str = Field(default="Not explicitly stated in the paper.")
    algorithms_models: List[str] = Field(default_factory=list)
    datasets: Union[str, List[str]] = Field(default="Not explicitly stated in the paper.")
    key_findings: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    future_scope: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    summary: SummaryDetails = Field(default_factory=SummaryDetails)

    def sanitize_empty_fields(self):
        """Ensure all empty fields or lists contain standard academic fallback string."""
        fallback = "Not explicitly stated in the paper."
        if not self.problem_statement or not self.problem_statement.strip():
            self.problem_statement = fallback
        if not self.research_objectives:
            self.research_objectives = [fallback]
        if not self.methodology or not self.methodology.strip():
            self.methodology = fallback
        if not self.algorithms_models:
            self.algorithms_models = [fallback]
        if not self.datasets:
            self.datasets = fallback
        elif isinstance(self.datasets, str) and not self.datasets.strip():
            self.datasets = fallback
        elif isinstance(self.datasets, list) and len(self.datasets) == 0:
            self.datasets = fallback
        if not self.key_findings:
            self.key_findings = [fallback]
        if not self.limitations:
            self.limitations = [fallback]
        if not self.future_scope:
            self.future_scope = [fallback]
        if not self.keywords:
            self.keywords = ["academic research"]

        # Filter out generic keywords if any slipped through
        generic_filter = {"paper", "research", "study", "results", "method", "author", "authors"}
        self.keywords = [kw for kw in self.keywords if kw.lower().strip() not in generic_filter][:10]
        if not self.keywords:
            self.keywords = ["academic research"]


class PaperAnalyzer:
    """Orchestrates comprehensive NLP and LLM analysis of research papers."""

    def __init__(self, gemini_client: GeminiClient, config_path: Optional[str] = None):
        self.client = gemini_client
        self.config = load_config(config_path)
        self.system_prompt = load_prompt("system_prompt.txt")
        self.analysis_prompt_template = load_prompt("analysis_prompt.txt")

    def analyze_paper(self, document_text: str) -> PaperAnalysisResult:
        """
        Analyze the full text of an academic paper and return structured components.
        For long papers, employs multi-stage chunk summarization before final synthesis.
        """
        if not document_text or not document_text.strip():
            raise ValueError("Document text is empty. Cannot perform analysis.")

        words = document_text.split()
        max_chunk_words = 6000

        # Handle long papers via chunk summarization
        if len(words) > max_chunk_words:
            effective_text = self._summarize_long_document(document_text, max_chunk_words)
        else:
            effective_text = document_text

        # Format prompt
        prompt = self.analysis_prompt_template.replace("{document_text}", effective_text)

        # Call Gemini API with JSON mode enabled
        raw_response = self.client.generate_content(
            prompt=prompt,
            system_instruction=self.system_prompt,
            temperature=0.2,
            json_mode=True,
        )

        return self._parse_analysis_json(raw_response)

    def _summarize_long_document(self, text: str, chunk_size_words: int) -> str:
        """
        Summarizes long research documents in chunks before final component extraction.
        Beginner-friendly map-reduce approach for academic papers.
        """
        chunks = PDFProcessor.chunk_text(text, chunk_size_words=3000, overlap_words=200)
        logger.info(f"Long document detected ({len(text.split())} words). Split into {len(chunks)} chunks.")

        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            chunk_prompt = (
                f"Extract the key research points, methodology, results, and components "
                f"from Section {i + 1} of {len(chunks)} of this academic paper:\n\n{chunk}"
            )
            summary = self.client.generate_content(
                prompt=chunk_prompt,
                system_instruction=self.system_prompt,
                temperature=0.2,
                json_mode=False,
            )
            chunk_summaries.append(f"--- Section {i + 1} Findings ---\n{summary}")

        return "\n\n".join(chunk_summaries)

    def _parse_analysis_json(self, raw_json_str: str) -> PaperAnalysisResult:
        """
        Safely parse and validate the JSON response into a PaperAnalysisResult model.
        Handles markdown backticks and minor formatting quirks.
        """
        cleaned_json = clean_json_markdown(raw_json_str)

        try:
            parsed_dict = json.loads(cleaned_json)
        except json.JSONDecodeError as err:
            logger.error(f"Failed to parse JSON response: {err}. Raw content: {cleaned_json[:200]}")
            raise ValueError(
                f"The AI model returned an invalid structured response: {str(err)}. "
                "Please retry the analysis."
            )

        try:
            result = PaperAnalysisResult.model_validate(parsed_dict)
            result.sanitize_empty_fields()
            return result
        except Exception as pydantic_err:
            logger.warning(f"Pydantic validation warning: {pydantic_err}. Attempting manual field recovery.")
            # Graceful manual recovery of known fields
            recovered = PaperAnalysisResult(
                title=str(parsed_dict.get("title", "Untitled Research Paper")),
                problem_statement=str(parsed_dict.get("problem_statement", "Not explicitly stated in the paper.")),
                research_objectives=list(parsed_dict.get("research_objectives", [])),
                methodology=str(parsed_dict.get("methodology", "Not explicitly stated in the paper.")),
                algorithms_models=list(parsed_dict.get("algorithms_models", [])),
                datasets=str(parsed_dict.get("datasets", "Not explicitly stated in the paper.")),
                key_findings=list(parsed_dict.get("key_findings", [])),
                limitations=list(parsed_dict.get("limitations", [])),
                future_scope=list(parsed_dict.get("future_scope", [])),
                keywords=list(parsed_dict.get("keywords", [])),
            )
            summary_raw = parsed_dict.get("summary", {})
            if isinstance(summary_raw, dict):
                recovered.summary = SummaryDetails(
                    overview=str(summary_raw.get("overview", "Not explicitly stated in the paper.")),
                    contributions=list(summary_raw.get("contributions", [])),
                    conclusion=str(summary_raw.get("conclusion", "Not explicitly stated in the paper.")),
                )
            recovered.sanitize_empty_fields()
            return recovered
