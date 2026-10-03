"""Document-Grounded Question Answering Engine for PaperMind AI.

Enables interactive, context-grounded Q&A over the uploaded research paper without external vector databases.
Extracts relevant paper context, tracks conversation history, and invokes Gemini with academic grounding prompts.
"""

from typing import Dict, List, Optional
from modules.gemini_client import GeminiClient
from modules.text_preprocessor import TextPreprocessor
from utils.helpers import load_config, load_prompt


class QAEngine:
    """Answers user queries grounded strictly within the research paper context."""

    def __init__(
        self,
        gemini_client: GeminiClient,
        text_preprocessor: Optional[TextPreprocessor] = None,
        config_path: Optional[str] = None,
    ):
        self.client = gemini_client
        self.preprocessor = text_preprocessor or TextPreprocessor()
        self.config = load_config(config_path)

        self.system_prompt = load_prompt("system_prompt.txt")
        self.qa_prompt_template = load_prompt("qa_prompt.txt")

        qa_cfg = self.config.get("qa", {})
        self.max_history_turns = qa_cfg.get("max_history_turns", 10)
        self.context_window_chars = qa_cfg.get("context_window_chars", 12000)

    def format_history(self, chat_history: List[Dict[str, str]]) -> str:
        """
        Format recent conversation history into a clean dialogue log.
        Limits to the last `max_history_turns` turns to avoid token overflow.
        """
        if not chat_history:
            return "No previous conversation."

        recent_history = chat_history[-self.max_history_turns :]
        formatted_turns = []
        for message in recent_history:
            role = "User" if message.get("role") == "user" else "Assistant"
            content = message.get("content", "").strip()
            formatted_turns.append(f"{role}: {content}")

        return "\n".join(formatted_turns)

    def answer_question(
        self,
        question: str,
        full_document_text: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Answer a user question strictly based on the extracted paper text.
        
        Args:
            question: The user's query about the paper.
            full_document_text: Complete text extracted from the uploaded PDF.
            chat_history: Prior conversation turns [{'role': 'user'|'assistant', 'content': '...'}].
            
        Returns:
            The model's grounded answer.
        """
        if not question or not question.strip():
            return "Please provide a valid question."

        if not full_document_text or not full_document_text.strip():
            return "No document content is loaded. Please upload a research paper first."

        # Extract relevant context from the document using keyword & heuristic matching
        context = self.preprocessor.extract_relevant_context(
            full_text=full_document_text,
            query=question,
            max_context_chars=self.context_window_chars,
        )

        formatted_history = self.format_history(chat_history or [])

        # Fill prompt template
        prompt = (
            self.qa_prompt_template
            .replace("{context}", context)
            .replace("{chat_history}", formatted_history)
            .replace("{question}", question.strip())
        )

        # Generate answer from Gemini
        response = self.client.generate_content(
            prompt=prompt,
            system_instruction=self.system_prompt,
            temperature=0.2,
            json_mode=False,
        )

        return response.strip()
