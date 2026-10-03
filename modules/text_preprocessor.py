"""NLP Text Preprocessing Module for PaperMind AI.

Performs explainable NLP operations:
- Text normalization and cleaning
- Sentence segmentation via NLTK (with safe fallback)
- Document statistics (words, sentences, vocabulary, reading time)
- Section extraction and keyword-relevance matching for grounded Q&A
"""

from dataclasses import dataclass
import math
import re
from typing import Dict, List, Optional
import nltk


@dataclass
class TextStatistics:
    """Quantitative NLP metrics of the extracted document text."""
    character_count: int
    character_count_no_spaces: int
    word_count: int
    sentence_count: int
    paragraph_count: int
    vocabulary_size: int
    avg_word_length: float
    avg_sentence_length_words: float
    estimated_reading_time_minutes: float


class TextPreprocessor:
    """Handles text cleaning, tokenization, and linguistic metric calculation."""

    def __init__(self):
        self._ensure_nltk_resources()

    def _ensure_nltk_resources(self):
        """Check if NLTK punkt tokenizer is available locally without blocking on network."""
        try:
            self._has_punkt = bool(nltk.data.find("tokenizers/punkt"))
        except Exception:
            self._has_punkt = False

    def normalize_text(self, text: str) -> str:
        """
        Normalize text:
        - Normalize unicode quotes, dashes, ligatures (e.g. fi, fl)
        - Clean irregular spacing
        - Preserve standard sentence casing and structure for LLM understanding
        """
        if not text:
            return ""

        # Normalize unicode quotes and dashes
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("‘", "'").replace("’", "'")
        text = text.replace("—", " - ").replace("–", " - ")

        # Common ligature replacements
        text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")
        text = text.replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")

        # Normalize multiple spaces
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def segment_sentences(self, text: str) -> List[str]:
        """
        Segment text into individual sentences using NLTK (if available),
        falling back to a robust regex-based splitter.
        """
        if not text or not text.strip():
            return []

        if getattr(self, "_has_punkt", False):
            try:
                sentences = nltk.sent_tokenize(text)
                if sentences:
                    return [s.strip() for s in sentences if s.strip()]
            except Exception:
                pass

        # Robust regex fallback for academic sentence boundaries
        # Protect common abbreviations so they don't trigger sentence splits
        protected = text
        abbreviations = [
            "e.g.", "i.e.", "et al.", "Fig.", "Ref.", "Vol.", "No.", "vs.", "Dr.", "Prof."
        ]
        for i, abbr in enumerate(abbreviations):
            protected = protected.replace(abbr, f"__ABBR_{i}__")

        raw_splits = re.split(r"(?<=[.?!])\s+(?=[A-Z0-9])", protected)
        sentences = []
        for s in raw_splits:
            restored = s
            for i, abbr in enumerate(abbreviations):
                restored = restored.replace(f"__ABBR_{i}__", abbr)
            cleaned_s = restored.strip()
            if cleaned_s:
                sentences.append(cleaned_s)

        return sentences if sentences else [text.strip()]

    def extract_paragraphs(self, text: str) -> List[str]:
        """Split text into distinct non-empty paragraphs based on double newlines."""
        if not text:
            return []
        raw_paras = re.split(r"\n\s*\n", text)
        return [p.strip() for p in raw_paras if len(p.strip()) > 30]

    def compute_statistics(self, text: str) -> TextStatistics:
        """Calculate comprehensive linguistic and readability metrics."""
        cleaned = self.normalize_text(text)
        if not cleaned:
            return TextStatistics(0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0)

        # Words
        words = re.findall(r"\b[A-Za-z0-9_-]+\b", cleaned)
        word_count = len(words)

        # Vocabulary size (unique lowercased words)
        unique_words = set(w.lower() for w in words)
        vocabulary_size = len(unique_words)

        # Characters
        char_count = len(cleaned)
        char_count_no_spaces = len(cleaned.replace(" ", "").replace("\n", "").replace("\t", ""))

        # Sentences
        sentences = self.segment_sentences(cleaned)
        sentence_count = max(len(sentences), 1 if word_count > 0 else 0)

        # Paragraphs
        paragraphs = self.extract_paragraphs(cleaned)
        paragraph_count = max(len(paragraphs), 1 if word_count > 0 else 0)

        # Averages
        avg_word_length = (
            round(sum(len(w) for w in words) / word_count, 2) if word_count > 0 else 0.0
        )
        avg_sentence_len = (
            round(word_count / sentence_count, 1) if sentence_count > 0 else 0.0
        )

        # Estimated reading time based on standard 220 words per minute for scientific reading
        reading_time = round(word_count / 220.0, 1)

        return TextStatistics(
            character_count=char_count,
            character_count_no_spaces=char_count_no_spaces,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            vocabulary_size=vocabulary_size,
            avg_word_length=avg_word_length,
            avg_sentence_length_words=avg_sentence_len,
            estimated_reading_time_minutes=reading_time,
        )

    def extract_relevant_context(
        self,
        full_text: str,
        query: str,
        max_context_chars: int = 12000,
        top_k: int = 5,
    ) -> str:
        """
        Lightweight, explainable, and vector-db-free context retrieval for Q&A.
        
        Splits paper into paragraphs/sections and scores each paragraph based on:
        1. Query term frequency and keyword overlap
        2. Exact phrase match bonus
        3. Position / academic section heuristic
        
        Returns the concatenated top-k most relevant passages.
        """
        if len(full_text) <= max_context_chars:
            # If the entire document fits comfortably within context, return it directly
            return full_text

        paragraphs = self.extract_paragraphs(full_text)
        if not paragraphs:
            return full_text[:max_context_chars]

        # Extract meaningful query keywords (alphanumeric, length >= 3)
        stopwords = {
            "the", "a", "an", "and", "or", "in", "on", "at", "to", "for",
            "with", "by", "of", "from", "is", "are", "was", "were", "what",
            "which", "who", "whom", "how", "why", "can", "could", "does",
            "this", "that", "these", "those", "have", "has", "had", "paper",
        }
        raw_terms = re.findall(r"\b[A-Za-z0-9_-]+\b", query.lower())
        keywords = [t for t in raw_terms if t not in stopwords and len(t) >= 3]

        if not keywords:
            # If no specific keywords found, use first few paragraphs (Abstract & Intro)
            context = "\n\n".join(paragraphs[:top_k])
            return context[:max_context_chars]

        scored_paras = []
        clean_query = query.lower().strip()

        for idx, para in enumerate(paragraphs):
            para_lower = para.lower()
            score = 0.0

            # Exact phrase bonus
            if clean_query in para_lower:
                score += 15.0

            # Keyword matching
            for kw in keywords:
                count = para_lower.count(kw)
                if count > 0:
                    score += 2.0 * math.log(1 + count)

            # Abstract / Introduction priority boost for general inquiries
            if idx < 3:
                score += 1.5

            if score > 0:
                scored_paras.append((score, idx, para))

        # Sort primarily by score descending
        scored_paras.sort(key=lambda x: x[0], reverse=True)

        selected = scored_paras[:top_k]
        # Re-sort chronologically by their original document order to preserve narrative flow
        selected.sort(key=lambda x: x[1])

        if not selected:
            # Fallback to beginning of document
            return full_text[:max_context_chars]

        context_parts = []
        current_len = 0
        for _, _, para in selected:
            if current_len + len(para) > max_context_chars:
                break
            context_parts.append(para)
            current_len += len(para) + 2

        return "\n\n".join(context_parts)
