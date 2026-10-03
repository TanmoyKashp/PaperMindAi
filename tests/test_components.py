"""Unit tests for GeminiClient, PaperAnalyzer, and QAEngine using mocks."""

import json
from unittest.mock import MagicMock, patch
import pytest

from modules.gemini_client import GeminiClient, GeminiAPIKeyError, GeminiQuotaError
from modules.paper_analyzer import PaperAnalyzer, PaperAnalysisResult
from modules.qa_engine import QAEngine


@pytest.fixture
def mock_gemini_client():
    client = GeminiClient(api_key="mock_test_key_for_unit_tests")
    return client


def test_gemini_client_not_configured():
    client = GeminiClient(api_key="")
    assert client.is_configured() is False
    with pytest.raises(GeminiAPIKeyError):
        client.generate_content("Hello")


def test_gemini_client_configured(mock_gemini_client):
    assert mock_gemini_client.is_configured() is True
    assert mock_gemini_client.model_name == "gemini-2.5-flash"


def test_paper_analyzer_with_mock(mock_gemini_client):
    analyzer = PaperAnalyzer(gemini_client=mock_gemini_client)

    sample_llm_json = json.dumps({
        "title": "BERT: Pre-training of Deep Bidirectional Transformers",
        "problem_statement": "Language models were unidirectional, limiting contextual representations.",
        "research_objectives": ["Introduce bidirectional pre-training for language representations."],
        "methodology": "Masked language model and next sentence prediction objectives.",
        "algorithms_models": ["BERT-Base", "BERT-Large", "Transformer Encoder"],
        "datasets": "BooksCorpus and English Wikipedia.",
        "key_findings": ["Outperformed prior state-of-the-art on 11 NLP tasks."],
        "limitations": ["High pre-training computational cost."],
        "future_scope": ["Domain-specific pre-training (BioBERT, SciBERT)."],
        "keywords": ["BERT", "Bidirectional", "Transformer", "Pre-training", "NLP"],
        "summary": {
            "overview": "BERT introduces deep bidirectional language representations.",
            "contributions": ["Masked LM objective", "Fine-tuning paradigm across 11 benchmarks"],
            "conclusion": "Bidirectional pre-training is crucial for language representations."
        }
    })

    with patch.object(mock_gemini_client, "generate_content", return_value=sample_llm_json):
        result = analyzer.analyze_paper("Sample paper full text content...")

        assert isinstance(result, PaperAnalysisResult)
        assert result.title == "BERT: Pre-training of Deep Bidirectional Transformers"
        assert len(result.algorithms_models) == 3
        assert "BERT-Base" in result.algorithms_models
        assert "BooksCorpus and English Wikipedia." in result.datasets
        assert len(result.keywords) == 5
        assert "Transformer Encoder" in result.algorithms_models


def test_paper_analyzer_sanitization_fallback(mock_gemini_client):
    analyzer = PaperAnalyzer(gemini_client=mock_gemini_client)

    # Missing fields to test graceful fallback
    partial_json = json.dumps({
        "title": "Incomplete Paper",
        "summary": {
            "overview": "Overview only"
        }
    })

    with patch.object(mock_gemini_client, "generate_content", return_value=partial_json):
        result = analyzer.analyze_paper("Some paper text...")
        assert result.title == "Incomplete Paper"
        assert result.problem_statement == "Not explicitly stated in the paper."
        assert result.methodology == "Not explicitly stated in the paper."
        assert result.datasets == "Not explicitly stated in the paper."


def test_qa_engine_with_mock(mock_gemini_client):
    qa_engine = QAEngine(gemini_client=mock_gemini_client)

    mock_answer = "The authors evaluated their model on the GLUE benchmark dataset."
    with patch.object(mock_gemini_client, "generate_content", return_value=mock_answer):
        answer = qa_engine.answer_question(
            question="What benchmark dataset was evaluated?",
            full_document_text="The experiments evaluated on GLUE benchmark dataset with 8 tasks.",
            chat_history=[{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}],
        )

        assert "GLUE benchmark" in answer


def test_qa_engine_empty_input(mock_gemini_client):
    qa_engine = QAEngine(gemini_client=mock_gemini_client)
    ans1 = qa_engine.answer_question("", "Some doc text")
    assert "valid question" in ans1.lower()

    ans2 = qa_engine.answer_question("What is this?", "")
    assert "upload a research paper" in ans2.lower()
