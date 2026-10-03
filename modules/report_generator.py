"""Report Generator Module for PaperMind AI.

Generates a comprehensive, downloadable academic Markdown report 
synthesizing the genuine analysis and text statistics of the analyzed research paper.
"""

from datetime import datetime
from typing import Optional
from modules.paper_analyzer import PaperAnalysisResult
from modules.text_preprocessor import TextStatistics


class ReportGenerator:
    """Formats research paper analysis results into publication-grade Markdown reports."""

    @staticmethod
    def generate_markdown_report(
        analysis: PaperAnalysisResult,
        filename: str,
        stats: Optional[TextStatistics] = None,
        page_count: Optional[int] = None,
    ) -> str:
        """
        Generate a comprehensive, structured Markdown report from the analysis result.
        
        Args:
            analysis: Validated PaperAnalysisResult instance.
            filename: Original PDF filename.
            stats: Quantitative text statistics (optional).
            page_count: Number of PDF pages (optional).
            
        Returns:
            Formatted Markdown report string.
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format list helpers
        def format_bullet_list(items):
            if not items:
                return "- Not explicitly stated in the paper."
            return "\n".join(f"- {item}" for item in items)

        def format_datasets(datasets_val):
            if isinstance(datasets_val, list):
                return format_bullet_list(datasets_val)
            return str(datasets_val)

        def format_keywords(keywords):
            if not keywords:
                return "`academic research`"
            return ", ".join(f"`{kw}`" for kw in keywords)

        report_lines = [
            f"# PaperMind AI — Academic Research Analysis Report",
            f"",
            f"> **Generated On:** {now_str}  ",
            f"> **Source File:** `{filename}`  ",
            f"> **System:** PaperMind AI (Powered by Google Gemini & PyMuPDF)  ",
            f"",
            f"---",
            f"",
            f"## 1. Document Identity & Overview",
            f"",
            f"**Paper Title:** {analysis.title}",
            f"",
        ]

        # Statistics table if available
        if stats or page_count:
            report_lines.extend([
                f"### Document Statistics",
                f"| Metric | Value |",
                f"| :--- | :--- |",
            ])
            if page_count:
                report_lines.append(f"| **Total Pages** | {page_count} |")
            if stats:
                report_lines.extend([
                    f"| **Total Word Count** | {stats.word_count:,} words |",
                    f"| **Total Character Count** | {stats.character_count:,} characters |",
                    f"| **Unique Vocabulary** | {stats.vocabulary_size:,} distinct terms |",
                    f"| **Sentence Count** | {stats.sentence_count:,} sentences |",
                    f"| **Avg Sentence Length** | {stats.avg_sentence_length_words} words |",
                    f"| **Estimated Reading Time** | ~{stats.estimated_reading_time_minutes} minutes |",
                ])
            report_lines.extend(["", "---", ""])

        # Summary section
        report_lines.extend([
            f"## 2. Research Summary",
            f"",
            f"### High-Level Overview",
            f"{analysis.summary.overview}",
            f"",
            f"### Core Contributions",
            f"{format_bullet_list(analysis.summary.contributions)}",
            f"",
            f"### Conclusion",
            f"{analysis.summary.conclusion}",
            f"",
            f"---",
            f"",
            f"## 3. Problem Statement & Research Objectives",
            f"",
            f"### Problem Statement",
            f"{analysis.problem_statement}",
            f"",
            f"### Research Objectives",
            f"{format_bullet_list(analysis.research_objectives)}",
            f"",
            f"---",
            f"",
            f"## 4. Methodology & Technical Architecture",
            f"",
            f"### Proposed Framework / Methodology",
            f"{analysis.methodology}",
            f"",
            f"### Algorithms & Models Employed",
            f"{format_bullet_list(analysis.algorithms_models)}",
            f"",
            f"### Datasets & Benchmarks",
            f"{format_datasets(analysis.datasets)}",
            f"",
            f"---",
            f"",
            f"## 5. Experimental Results & Findings",
            f"",
            f"{format_bullet_list(analysis.key_findings)}",
            f"",
            f"---",
            f"",
            f"## 6. Critical Evaluation: Limitations & Future Scope",
            f"",
            f"### Acknowledged Limitations",
            f"{format_bullet_list(analysis.limitations)}",
            f"",
            f"### Proposed Future Directions",
            f"{format_bullet_list(analysis.future_scope)}",
            f"",
            f"---",
            f"",
            f"## 7. Extracted Research Keywords",
            f"",
            f"{format_keywords(analysis.keywords)}",
            f"",
            f"---",
            f"",
            f"*(Report generated automatically by PaperMind AI — NLP-Based Research Intelligence Assistant)*",
        ])

        return "\n".join(report_lines)
