"""PaperMind AI — Academic Research Paper Intelligence Assistant.

Streamlit frontend application orchestrating:
1. PDF document upload, validation, and PyMuPDF text extraction.
2. Quantitative NLP preprocessing and readability statistics.
3. Gemini LLM-powered structured academic analysis.
4. Extracted research component exploration and keyword badges.
5. Interactive, document-grounded Q&A engine with session memory.
6. Publication-grade downloadable Markdown research report.
"""

import os
from typing import Optional
import streamlit as st

from modules.pdf_processor import PDFProcessor, PDFProcessingResult
from modules.text_preprocessor import TextPreprocessor, TextStatistics
from modules.gemini_client import (
    GeminiClient,
    GeminiAPIError,
    GeminiAPIKeyError,
    GeminiQuotaError,
)
from modules.paper_analyzer import PaperAnalyzer, PaperAnalysisResult
from modules.qa_engine import QAEngine
from modules.report_generator import ReportGenerator
from utils.helpers import format_file_size, get_api_key, load_config

# Page configuration
st.set_page_config(
    page_title="PaperMind AI — Research Intelligence Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Academic Theme CSS
st.markdown(
    """
    <style>
    /* Global Typography & Palette */
    :root {
        --pm-primary: #1e3a8a;
        --pm-accent: #2563eb;
        --pm-bg: #f8fafc;
        --pm-card-bg: #ffffff;
        --pm-text-dark: #0f172a;
        --pm-text-muted: #475569;
        --pm-border: #e2e8f0;
    }
    
    .stApp {
        background-color: var(--pm-bg);
        color: var(--pm-text-dark);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Container */
    .pm-header-container {
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid var(--pm-border);
        margin-bottom: 1.5rem;
    }
    .pm-header-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: var(--pm-primary);
        letter-spacing: -0.02em;
        margin: 0;
    }
    .pm-header-subtitle {
        font-size: 1.05rem;
        color: var(--pm-text-muted);
        margin-top: 0.35rem;
    }
    
    /* Academic Cards */
    .pm-card {
        background-color: var(--pm-card-bg);
        border: 1px solid var(--pm-border);
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .pm-card-header {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--pm-primary);
        border-bottom: 1px solid var(--pm-border);
        padding-bottom: 0.5rem;
        margin-bottom: 0.85rem;
    }
    .pm-card-body {
        font-size: 0.96rem;
        line-height: 1.6;
        color: var(--pm-text-dark);
    }
    
    /* Metric pill */
    .pm-metric-badge {
        display: inline-block;
        background-color: #eff6ff;
        color: var(--pm-accent);
        border: 1px solid #bfdbfe;
        border-radius: 4px;
        padding: 0.25rem 0.65rem;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    /* Keyword Tags */
    .pm-keyword-tag {
        display: inline-block;
        background-color: #f1f5f9;
        color: #1e293b;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        padding: 0.35rem 0.85rem;
        font-size: 0.88rem;
        font-weight: 500;
        margin: 0.25rem;
    }

    /* Sidebar Branding */
    .pm-sidebar-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--pm-primary);
        margin-bottom: 0.2rem;
    }
    .pm-sidebar-badge {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        background-color: #dbeafe;
        color: #1e40af;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize persistent Streamlit state variables."""
    if "current_file_id" not in st.session_state:
        st.session_state.current_file_id = None
    if "pdf_result" not in st.session_state:
        st.session_state.pdf_result = None
    if "text_stats" not in st.session_state:
        st.session_state.text_stats = None
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "custom_api_key" not in st.session_state:
        st.session_state.custom_api_key = ""


def reset_uploaded_document():
    """Clear all document state, cached analysis, and conversation history."""
    st.session_state.current_file_id = None
    st.session_state.pdf_result = None
    st.session_state.text_stats = None
    st.session_state.analysis_result = None
    st.session_state.chat_history = []


init_session_state()

# Load central configuration
config = load_config()
app_cfg = config.get("app", {})
model_cfg = config.get("model", {})
max_file_mb = app_cfg.get("max_file_size_mb", 20)

# Instantiate core modules
preprocessor = TextPreprocessor()
pdf_processor = PDFProcessor(
    min_text_chars=config.get("nlp", {}).get("min_extracted_text_chars", 100),
    max_size_mb=max_file_mb,
)

# Resolve active API key
active_key = st.session_state.custom_api_key.strip() or get_api_key()
gemini_client = GeminiClient(api_key=active_key, model_name=model_cfg.get("name", "gemini-2.5-flash"))
qa_engine = QAEngine(gemini_client=gemini_client, text_preprocessor=preprocessor)
analyzer = PaperAnalyzer(gemini_client=gemini_client)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <div class="pm-sidebar-title">📄 PaperMind AI</div>
            <span class="pm-sidebar-badge">NLP Research Assistant</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # API Connection Status Check
    st.subheader("🔑 Gemini API Setup")
    if gemini_client.is_configured():
        st.success(f"API Key configured ({gemini_client.model_name})")
    else:
        st.warning("Gemini API key is not detected in `.env`.")

    with st.expander("API Key Settings", expanded=not gemini_client.is_configured()):
        entered_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.custom_api_key,
            help="Enter a Google Gemini API key or save GEMINI_API_KEY in your .env file.",
            placeholder="AIzaSy...",
        )
        if entered_key != st.session_state.custom_api_key:
            st.session_state.custom_api_key = entered_key
            gemini_client.update_api_key(entered_key)
            st.rerun()

        if st.button("Test API Connection", use_container_width=True):
            with st.spinner("Connecting to Google Gemini..."):
                ok, msg = gemini_client.test_connection()
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    st.markdown("---")

    # Document Upload Section
    st.subheader("📤 Document Upload")
    uploaded_file = st.file_uploader(
        "Upload Academic PDF",
        type=["pdf"],
        help=f"Accepts research papers in PDF format up to {max_file_mb} MB.",
    )

    # Detect new file or reset
    if uploaded_file is not None:
        file_identifier = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.current_file_id != file_identifier:
            # New document uploaded: reset previous states
            reset_uploaded_document()
            st.session_state.current_file_id = file_identifier

            # Process PDF
            with st.spinner("Extracting text via PyMuPDF..."):
                pdf_bytes = uploaded_file.getvalue()
                res: PDFProcessingResult = pdf_processor.extract_from_bytes(pdf_bytes, filename=uploaded_file.name)
                st.session_state.pdf_result = res

                if res.success:
                    # Compute NLP Statistics
                    st.session_state.text_stats = preprocessor.compute_statistics(res.full_text)
                st.rerun()

    if st.session_state.pdf_result:
        res = st.session_state.pdf_result
        if res.success:
            st.success(f"Loaded: **{res.filename}**")
            st.caption(f"Pages: **{res.page_count}** | Words: **{res.total_words:,}**")
        else:
            st.error("Document extraction failed.")

        if st.button("Reset Document", use_container_width=True, type="secondary"):
            reset_uploaded_document()
            st.rerun()

    st.markdown("---")
    st.caption("PaperMind AI v1.0.0 | B.Tech Academic Submission")


# ==========================================
# MAIN INTERFACE
# ==========================================

# Header Banner
st.markdown(
    """
    <div class="pm-header-container">
        <h1 class="pm-header-title">PaperMind AI — Research Paper Intelligence</h1>
        <p class="pm-header-subtitle">
            Automated NLP component extraction, deep academic synthesis, and grounded question answering powered by Google Gemini.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Check if document is loaded
pdf_res: Optional[PDFProcessingResult] = st.session_state.pdf_result
stats: Optional[TextStatistics] = st.session_state.text_stats

if not pdf_res:
    # Empty State Guidance
    st.info("👈 **Get Started:** Upload an academic research paper (PDF format) in the sidebar to begin analysis.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="pm-card">
                <div class="pm-card-header">📊 Text Extraction</div>
                <div class="pm-card-body">
                    Uses PyMuPDF (fitz) to cleanly extract multi-page academic layouts, handling 2-column formatting and hyphenations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="pm-card">
                <div class="pm-card-header">🧠 Component Analysis</div>
                <div class="pm-card-body">
                    Identifies problem statements, objectives, architectures, datasets, experimental findings, and critical limitations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="pm-card">
                <div class="pm-card-header">💬 Grounded Q&A</div>
                <div class="pm-card-body">
                    Interact directly with your uploaded paper. Answers are strictly grounded in document context without hallucinations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

elif not pdf_res.success:
    # Error state for PDF processing (corrupted or scanned)
    st.error(f"⚠️ **Document Processing Error:** {pdf_res.error_message}")
    if pdf_res.is_scanned_or_empty:
        st.warning(
            "PaperMind AI requires selectable text. If this is a scanned photocopy or image-only PDF, "
            "please use an OCR tool (e.g. Adobe Acrobat OCR, tesseract) or supply a digitally authored PDF."
        )

else:
    # Valid document loaded!
    # Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Total Pages", pdf_res.page_count)
    with m2:
        st.metric("Word Count", f"{stats.word_count:,}" if stats else f"{pdf_res.total_words:,}")
    with m3:
        st.metric("Sentences", f"{stats.sentence_count:,}" if stats else "N/A")
    with m4:
        st.metric("Unique Vocab", f"{stats.vocabulary_size:,}" if stats else "N/A")
    with m5:
        st.metric("Est. Read Time", f"~{stats.estimated_reading_time_minutes} min" if stats else "N/A")

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # Automatic / Manual Analysis Trigger
    if st.session_state.analysis_result is None:
        if not gemini_client.is_configured():
            st.warning("⚠️ Please provide a Gemini API Key in the sidebar to perform AI research analysis.")
        else:
            col_btn, _ = st.columns([1, 3])
            with col_btn:
                if st.button("🚀 Analyze Research Paper", type="primary", use_container_width=True):
                    with st.spinner("Extracting research components & synthesizing insights with Gemini..."):
                        try:
                            analysis_data = analyzer.analyze_paper(pdf_res.full_text)
                            st.session_state.analysis_result = analysis_data
                            st.rerun()
                        except GeminiAPIKeyError as e:
                            st.error(f"🔑 API Key Error: {str(e)}")
                        except GeminiQuotaError as e:
                            st.error(f"⏳ Rate Limit Exceeded: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")

    # Display Analysis Tabs if analysis is available
    analysis: Optional[PaperAnalysisResult] = st.session_state.analysis_result

    tab_overview, tab_components, tab_keywords, tab_qa, tab_report = st.tabs([
        "📋 Overview",
        "🔬 Research Analysis",
        "🏷️ Keywords",
        "💬 Ask Your Paper",
        "📥 Download Report",
    ])

    # ---------------- TAB 1: OVERVIEW ----------------
    with tab_overview:
        if not analysis:
            st.info("Click **'🚀 Analyze Research Paper'** above to generate the comprehensive research summary.")
        else:
            st.markdown(f"### {analysis.title}")
            
            st.markdown(
                f"""
                <div class="pm-card">
                    <div class="pm-card-header">📌 Research Overview</div>
                    <div class="pm-card-body">{analysis.summary.overview}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_prob, col_concl = st.columns(2)
            with col_prob:
                st.markdown(
                    f"""
                    <div class="pm-card">
                        <div class="pm-card-header">🎯 Problem Statement</div>
                        <div class="pm-card-body">{analysis.problem_statement}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_concl:
                st.markdown(
                    f"""
                    <div class="pm-card">
                        <div class="pm-card-header">🏁 Final Conclusion</div>
                        <div class="pm-card-body">{analysis.summary.conclusion}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("#### 💡 Core Contributions")
            for c in analysis.summary.contributions:
                st.markdown(f"- {c}")

    # ---------------- TAB 2: RESEARCH ANALYSIS ----------------
    with tab_components:
        if not analysis:
            st.info("Click **'🚀 Analyze Research Paper'** above to view detailed research components.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🎯 Research Objectives")
                for obj in analysis.research_objectives:
                    st.markdown(f"- {obj}")

                st.markdown("#### 🛠️ Methodology & Framework")
                st.markdown(analysis.methodology)

                st.markdown("#### 🧮 Algorithms & Models Used")
                for algo in analysis.algorithms_models:
                    st.markdown(f"- {algo}")

            with c2:
                st.markdown("#### 📊 Datasets & Benchmarks")
                if isinstance(analysis.datasets, list):
                    for ds in analysis.datasets:
                        st.markdown(f"- {ds}")
                else:
                    st.markdown(analysis.datasets)

                st.markdown("#### 📈 Key Findings & Experimental Results")
                for finding in analysis.key_findings:
                    st.markdown(f"- {finding}")

                st.markdown("#### ⚠️ Acknowledged Limitations")
                for lim in analysis.limitations:
                    st.markdown(f"- {lim}")

                st.markdown("#### 🔮 Future Scope & Directions")
                for fut in analysis.future_scope:
                    st.markdown(f"- {fut}")

    # ---------------- TAB 3: KEYWORDS ----------------
    with tab_keywords:
        if not analysis:
            st.info("Click **'🚀 Analyze Research Paper'** above to extract domain keywords.")
        else:
            st.markdown("### 🏷️ Domain Research Keywords")
            st.caption("Extracted up to 10 context-specific technical terms, filtering generic research stop-words.")

            tag_html = "".join([f'<span class="pm-keyword-tag">{kw}</span>' for kw in analysis.keywords])
            st.markdown(f"<div style='margin-top: 1rem;'>{tag_html}</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### Keyword Analysis")
            st.markdown(
                "These keywords reflect the prominent conceptual topics and technical terminology "
                "surfaced within the paper's abstract, methodology, and experimental sections."
            )

    # ---------------- TAB 4: ASK YOUR PAPER (Q&A) ----------------
    with tab_qa:
        st.markdown("### 💬 Document-Grounded Q&A")
        st.caption("Ask specific questions about the methodology, baseline results, datasets, or theoretical claims.")

        if not gemini_client.is_configured():
            st.warning("⚠️ Please provide a Gemini API Key in the sidebar to ask questions.")
        else:
            # Display past chat turns
            for turn in st.session_state.chat_history:
                with st.chat_message(turn["role"]):
                    st.markdown(turn["content"])

            # Prompt suggestions
            col_q1, col_q2, col_q3 = st.columns(3)
            with col_q1:
                if st.button("What problem does this paper solve?", use_container_width=True):
                    st.session_state.pending_question = "What problem does this paper solve?"
            with col_q2:
                if st.button("Explain the methodology simply", use_container_width=True):
                    st.session_state.pending_question = "Explain the methodology in simple language."
            with col_q3:
                if st.button("What are the limitations?", use_container_width=True):
                    st.session_state.pending_question = "What are the limitations of this work?"

            # Chat input or button trigger
            user_query = st.chat_input("Ask a question about this paper...")

            # Handle pending button clicks
            if "pending_question" in st.session_state and st.session_state.pending_question:
                user_query = st.session_state.pending_question
                st.session_state.pending_question = None

            if user_query:
                # Add user message to state & display
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.markdown(user_query)

                # Generate grounded response
                with st.chat_message("assistant"):
                    with st.spinner("Searching document context & synthesizing answer..."):
                        try:
                            answer = qa_engine.answer_question(
                                question=user_query,
                                full_document_text=pdf_res.full_text,
                                chat_history=st.session_state.chat_history[:-1],
                            )
                            st.markdown(answer)
                            st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        except GeminiAPIKeyError as e:
                            st.error(f"🔑 {str(e)}")
                        except GeminiQuotaError as e:
                            st.error(f"⏳ {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Failed to answer question: {str(e)}")

            if st.session_state.chat_history:
                if st.button("Clear Conversation History", type="secondary"):
                    st.session_state.chat_history = []
                    st.rerun()

    # ---------------- TAB 5: DOWNLOAD REPORT ----------------
    with tab_report:
        st.markdown("### 📥 Download Academic Analysis Report")
        if not analysis:
            st.info("Please run **'🚀 Analyze Research Paper'** to generate the exportable research report.")
        else:
            st.markdown(
                "Generate a publication-grade academic Markdown document containing the complete "
                "synthesized research findings, linguistic statistics, problem definition, and citations."
            )

            report_md = ReportGenerator.generate_markdown_report(
                analysis=analysis,
                filename=pdf_res.filename,
                stats=stats,
                page_count=pdf_res.page_count,
            )

            # Download button
            base_name = os.path.splitext(pdf_res.filename)[0]
            download_filename = f"{base_name}_papermind_report.md"

            st.download_button(
                label="⬇️ Download Markdown Report (.md)",
                data=report_md,
                file_name=download_filename,
                mime="text/markdown",
                type="primary",
            )

            st.markdown("---")
            st.subheader("Report Preview")
            with st.expander("Preview Generated Report", expanded=False):
                st.markdown(report_md)
