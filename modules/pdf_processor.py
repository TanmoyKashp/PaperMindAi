"""PDF Processor Module for PaperMind AI.

Extracts text, metadata, and per-page structures from academic PDF files using PyMuPDF (fitz).
Provides graceful error handling for corrupted, empty, or scanned documents.
"""

from dataclasses import dataclass, field
import io
import re
from typing import List, Optional, Union
try:
    import pymupdf as fitz
except ImportError:
    import fitz  # Fallback for older PyMuPDF versions


@dataclass
class PageContent:
    """Represents the extracted text and metadata of a single PDF page."""
    page_number: int
    text: str
    char_count: int
    word_count: int


@dataclass
class PDFProcessingResult:
    """Encapsulates the complete result of PDF text extraction."""
    success: bool
    filename: str
    page_count: int = 0
    pages: List[PageContent] = field(default_factory=list)
    full_text: str = ""
    total_characters: int = 0
    total_words: int = 0
    is_scanned_or_empty: bool = False
    error_message: Optional[str] = None


class PDFProcessor:
    """Extracts and validates text content from PDF documents."""

    def __init__(self, min_text_chars: int = 100, max_size_mb: int = 20):
        self.min_text_chars = min_text_chars
        self.max_size_mb = max_size_mb

    def validate_file(self, filename: str, file_size_bytes: int) -> Optional[str]:
        """
        Validate file extension and file size.
        Returns an error string if invalid, or None if valid.
        """
        if not filename.lower().endswith(".pdf"):
            return "Invalid file format. Please upload a PDF file (.pdf)."

        max_bytes = self.max_size_mb * 1024 * 1024
        if file_size_bytes > max_bytes:
            return f"File size exceeds maximum limit of {self.max_size_mb} MB."

        if file_size_bytes == 0:
            return "The uploaded file is empty (0 bytes)."

        return None

    def clean_page_text(self, text: str) -> str:
        """
        Clean common PDF extraction artifacts:
        - Normalize multiple blank lines into two
        - Fix broken hyphenated words at line ends (e.g. 'trans- \nformer' -> 'transformer')
        - Replace non-standard whitespace characters
        """
        if not text:
            return ""

        # Remove null bytes or non-printable control characters
        text = text.replace("\x00", "")

        # Reconnect words split across line breaks by hyphens (common in 2-column papers)
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

        # Replace excessive consecutive spaces or tabs with a single space
        text = re.sub(r"[ \t]+", " ", text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Reduce 3 or more consecutive newlines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def extract_from_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> PDFProcessingResult:
        """
        Extract text and structure from raw PDF bytes (e.g., from Streamlit's file_uploader).
        """
        # Validate size
        val_error = self.validate_file(filename, len(pdf_bytes))
        if val_error:
            return PDFProcessingResult(
                success=False,
                filename=filename,
                error_message=val_error,
            )

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            return PDFProcessingResult(
                success=False,
                filename=filename,
                error_message=f"Failed to open PDF document. File may be corrupted or encrypted: {str(e)}",
            )

        return self._extract_from_doc(doc, filename)

    def extract_from_path(self, file_path: str) -> PDFProcessingResult:
        """
        Extract text and structure from a PDF file path on disk.
        """
        try:
            doc = fitz.open(file_path)
            filename = file_path.split("/")[-1]
        except Exception as e:
            return PDFProcessingResult(
                success=False,
                filename=file_path,
                error_message=f"Could not read PDF file at '{file_path}': {str(e)}",
            )

        return self._extract_from_doc(doc, filename)

    def _extract_from_doc(self, doc: fitz.Document, filename: str) -> PDFProcessingResult:
        """Internal helper to process a fitz.Document instance."""
        try:
            page_count = len(doc)
            if page_count == 0:
                doc.close()
                return PDFProcessingResult(
                    success=False,
                    filename=filename,
                    page_count=0,
                    error_message="The PDF contains 0 pages.",
                )

            pages_list: List[PageContent] = []
            full_text_parts: List[str] = []

            for page_index in range(page_count):
                page = doc.load_page(page_index)
                raw_text = page.get_text("text")
                cleaned_text = self.clean_page_text(raw_text)

                char_count = len(cleaned_text)
                word_count = len(cleaned_text.split()) if cleaned_text else 0

                page_content = PageContent(
                    page_number=page_index + 1,
                    text=cleaned_text,
                    char_count=char_count,
                    word_count=word_count,
                )
                pages_list.append(page_content)
                if cleaned_text:
                    full_text_parts.append(f"--- Page {page_index + 1} ---\n{cleaned_text}")

            doc.close()

            full_text = "\n\n".join(full_text_parts).strip()
            total_chars = len(full_text)
            total_words = len(full_text.split()) if full_text else 0

            # Detect empty or scanned image-only PDF
            is_scanned = total_chars < self.min_text_chars

            if is_scanned:
                return PDFProcessingResult(
                    success=False,
                    filename=filename,
                    page_count=page_count,
                    pages=pages_list,
                    full_text=full_text,
                    total_characters=total_chars,
                    total_words=total_words,
                    is_scanned_or_empty=True,
                    error_message=(
                        f"Insufficient selectable text detected ({total_chars} characters across {page_count} pages). "
                        "This document appears to be a scanned image or empty PDF. "
                        "PaperMind AI requires digital, selectable text to analyze academic content."
                    ),
                )

            return PDFProcessingResult(
                success=True,
                filename=filename,
                page_count=page_count,
                pages=pages_list,
                full_text=full_text,
                total_characters=total_chars,
                total_words=total_words,
                is_scanned_or_empty=False,
                error_message=None,
            )

        except Exception as e:
            try:
                doc.close()
            except Exception:
                pass
            return PDFProcessingResult(
                success=False,
                filename=filename,
                error_message=f"An error occurred during PDF text extraction: {str(e)}",
            )

    @staticmethod
    def chunk_text(text: str, chunk_size_words: int = 1500, overlap_words: int = 150) -> List[str]:
        """
        Split a long document into overlapping word chunks.
        Beginner-friendly and robust chunking for long research documents.
        """
        words = text.split()
        if not words:
            return []

        if len(words) <= chunk_size_words:
            return [text]

        chunks = []
        start = 0
        step = chunk_size_words - overlap_words
        if step <= 0:
            step = chunk_size_words

        while start < len(words):
            end = min(start + chunk_size_words, len(words))
            chunk_slice = words[start:end]
            chunks.append(" ".join(chunk_slice))
            if end >= len(words):
                break
            start += step

        return chunks
