"""Unit tests for NLP Text Preprocessor and Report Generator modules."""

import pytest
from modules.text_preprocessor import TextPreprocessor, TextStatistics
from modules.report_generator import ReportGenerator
from modules.paper_analyzer import PaperAnalysisResult, SummaryDetails


@pytest.fixture
def preprocessor() -> TextPreprocessor:
    return TextPreprocessor()


def test_normalize_text(preprocessor):
    raw = "“Attention Is All You Need” — a paper with ﬁne ligatures   and   spaces."
    cleaned = preprocessor.normalize_text(raw)
    assert '"Attention Is All You Need"' in cleaned
    assert " - " in cleaned
    assert "fine" in cleaned
    assert "   " not in cleaned


def test_segment_sentences(preprocessor):
    text = (
        "Natural language processing is evolving rapidly. "
        "The Transformer model replaced recurrent networks. "
        "Can it achieve state-of-the-art performance? Yes, it can!"
    )
    sentences = preprocessor.segment_sentences(text)
    assert len(sentences) == 4
    assert "Natural language processing is evolving rapidly." in sentences
    assert "Yes, it can!" in sentences


def test_compute_statistics(preprocessor):
    text = (
        "Deep learning architectures have revolutionized artificial intelligence. "
        "Transformers utilize self-attention mechanisms to process sequence data efficiently."
    )
    stats = preprocessor.compute_statistics(text)

    assert stats.word_count > 15
    assert stats.sentence_count == 2
    assert stats.vocabulary_size > 10
    assert stats.avg_word_length > 0
    assert stats.avg_sentence_length_words > 5
    assert stats.estimated_reading_time_minutes > 0.0


def test_relevant_context_extraction(preprocessor):
    paper_text = (
        "Section 1: Introduction\n"
        "Machine learning models often require large labeled datasets for supervised training.\n\n"
        "Section 2: Optimization and Hyperparameters\n"
        "We used the AdamW optimizer with a learning rate of 1e-4 and a cosine decay schedule. "
        "Batch size was set to 64 across 8 NVIDIA A100 GPUs.\n\n"
        "Section 3: Evaluation Metrics\n"
        "Models were evaluated using BLEU score and ROUGE-L on benchmark datasets."
    )

    query = "What optimizer and learning rate were used?"
    context = preprocessor.extract_relevant_context(paper_text, query, max_context_chars=500, top_k=1)

    assert "AdamW" in context
    assert "learning rate" in context


def test_report_generator():
    analysis = PaperAnalysisResult(
        title="Attention Is All You Need",
        problem_statement="Sequential computation in RNNs prevents parallelization.",
        research_objectives=["Replace recurrent models with self-attention mechanism."],
        methodology="Transformer architecture using multi-head self-attention.",
        algorithms_models=["Transformer", "Multi-Head Attention", "Adam Optimizer"],
        datasets=["WMT 2014 English-to-German", "WMT 2014 English-to-French"],
        key_findings=["Achieved 28.4 BLEU on English-to-German, setting new SOTA."],
        limitations=["Quadratic complexity with respect to sequence length."],
        future_scope=["Apply attention mechanisms to vision and audio domains."],
        keywords=["Transformer", "Self-Attention", "Machine Translation", "Deep Learning"],
        summary=SummaryDetails(
            overview="Introduces the Transformer model.",
            contributions=["Solely attention-based sequence architecture."],
            conclusion="Transforms sequence transduction performance while speeding training."
        ),
    )

    stats = TextStatistics(
        character_count=5000,
        character_count_no_spaces=4200,
        word_count=850,
        sentence_count=45,
        paragraph_count=6,
        vocabulary_size=320,
        avg_word_length=5.2,
        avg_sentence_length_words=18.8,
        estimated_reading_time_minutes=3.8,
    )

    report = ReportGenerator.generate_markdown_report(
        analysis=analysis,
        filename="vaswani2017.pdf",
        stats=stats,
        page_count=11,
    )

    assert "# PaperMind AI — Academic Research Analysis Report" in report
    assert "Attention Is All You Need" in report
    assert "vaswani2017.pdf" in report
    assert "AdamW" not in report  # ensures no hardcoded content
    assert "Multi-Head Attention" in report
    assert "28.4 BLEU" in report
    assert "Total Pages" in report
    assert "Total Word Count" in report
