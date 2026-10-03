"""Unit tests for PDF Processor module."""

import io
import pytest
try:
    import pymupdf as fitz
except ImportError:
    import fitz
from modules.pdf_processor import PDFProcessor, PDFProcessingResult


@pytest.fixture
def sample_valid_pdf_bytes() -> bytes:
    """Generate a clean, valid 2-page PDF in memory for testing."""
    doc = fitz.open()
    
    # Page 1
    page1 = doc.new_page(width=595, height=842)
    page1.insert_textbox(
        fitz.Rect(50, 72, 545, 750),
        "Attention Is All You Need\n\n"
        "Ashish Vaswani, Noam Shazeer, Niki Parmar\n"
        "Abstract\n"
        "The dominant sequence transduction models are based on complex recurrent or "
        "convolutional neural networks that include an encoder and a decoder. "
        "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.",
        fontsize=11,
    )
    
    # Page 2
    page2 = doc.new_page(width=595, height=842)
    page2.insert_textbox(
        fitz.Rect(50, 72, 545, 750),
        "Methodology and Architecture\n\n"
        "The Transformer follows this overall architecture using stacked self-attention and point-wise, "
        "fully connected layers for both the encoder and decoder. Multi-head attention allows the model "
        "to jointly attend to information from different representation subspaces.",
        fontsize=11,
    )
    
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def sample_empty_pdf_bytes() -> bytes:
    """Generate a PDF with blank pages (no selectable text)."""
    doc = fitz.open()
    doc.new_page(width=595, height=842)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_valid_pdf_extraction(sample_valid_pdf_bytes):
    processor = PDFProcessor(min_text_chars=50)
    result = processor.extract_from_bytes(sample_valid_pdf_bytes, filename="transformer_sample.pdf")

    assert result.success is True
    assert result.filename == "transformer_sample.pdf"
    assert result.page_count == 2
    assert len(result.pages) == 2
    assert "Transformer" in result.full_text
    assert "Multi-head attention" in result.full_text
    assert result.total_characters > 100
    assert result.total_words > 20
    assert result.error_message is None
    assert result.is_scanned_or_empty is False


def test_invalid_corrupted_pdf_handling():
    processor = PDFProcessor()
    corrupted_bytes = b"NOT_A_VALID_PDF_HEADER_12345_CORRUPTED"
    result = processor.extract_from_bytes(corrupted_bytes, filename="broken.pdf")

    assert result.success is False
    assert result.error_message is not None
    assert "Failed to open PDF document" in result.error_message


def test_invalid_file_extension():
    processor = PDFProcessor()
    result = processor.extract_from_bytes(b"some content", filename="report.docx")

    assert result.success is False
    assert "Invalid file format" in result.error_message


def test_empty_file_handling():
    processor = PDFProcessor()
    result = processor.extract_from_bytes(b"", filename="empty.pdf")

    assert result.success is False
    assert "empty" in result.error_message.lower()


def test_scanned_or_insufficient_text(sample_empty_pdf_bytes):
    processor = PDFProcessor(min_text_chars=100)
    result = processor.extract_from_bytes(sample_empty_pdf_bytes, filename="scanned.pdf")

    assert result.success is False
    assert result.is_scanned_or_empty is True
    assert "Insufficient selectable text" in result.error_message


def test_text_cleaning_hyphenation():
    processor = PDFProcessor()
    dirty_text = "The trans-\nformer architecture im-\nproves attention."
    cleaned = processor.clean_page_text(dirty_text)

    assert "transformer" in cleaned
    assert "improves" in cleaned


def test_chunking_strategy():
    long_text = "word " * 1000  # 1000 words
    chunks = PDFProcessor.chunk_text(long_text, chunk_size_words=300, overlap_words=50)

    assert len(chunks) == 4
    for chunk in chunks:
        words = chunk.split()
        assert len(words) <= 300
