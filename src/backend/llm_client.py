"""
LLM Client Module.
Handles interaction with Google Generative AI (Gemini).
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import google.api_core.exceptions
import logging

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_EMBED_MODEL = "models/text-embedding-004"

logger = logging.getLogger(__name__)

# Retry ONLY on transient errors.
RETRYABLE_EXCEPTIONS = (
    google.api_core.exceptions.ResourceExhausted,    # 429 / quota / rate limit
    google.api_core.exceptions.ServiceUnavailable,   # 503
    google.api_core.exceptions.DeadlineExceeded,     # timeouts
    google.api_core.exceptions.InternalServerError,  # 500
)


class LLMClient:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    @retry(
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        wait=wait_exponential(multiplier=2, min=2, max=30),  # prevent huge waits
        stop=stop_after_attempt(3),  # Fail faster on rate limits
        reraise=True,  # IMPORTANT: raise the last exception after retries
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def generate_content(self, prompt: str) -> str:
        """
        Generates content from the LLM based on the prompt.
        Retries automatically on transient Gemini errors (429/503/timeouts/500).
        """
        response = self.model.generate_content(prompt)
        text = getattr(response, "text", None)

        # Track Tokens
        from src.backend.token_tracker import TokenTracker
        tracker = TokenTracker()
        # Input tokens
        tracker.add_input_tokens(self.count_tokens(prompt))
        # Output tokens
        tracker.add_output_tokens(self.count_tokens(text) if text else 0)

        # Guard: sometimes SDK returns empty/None.
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response.")
        return text

    def get_embedding(self, text: str, task_type: str = "retrieval_query") -> list[float]:
        """
        Generates an embedding for the given text.

        task_type:
          - "retrieval_document" for indexing your pattern library
          - "retrieval_query" for embedding user queries
        """
        result = genai.embed_content(
            model=GEMINI_EMBED_MODEL,
            content=text,
            task_type='retrieval_document',
            title="Embedding",
        )
        emb = result.get("embedding")
        if not emb:
            raise RuntimeError("Embedding API returned empty embedding.")
        return emb
    def count_tokens(self, text: str) -> int:
        """
        Counts tokens in the provided text using the model's tokenizer.
        """
        if not text:
            return 0
        try:
             # Gemini API has count_tokens
             res = self.model.count_tokens(text)
             return res.total_tokens
        except Exception as e:
            logger.warning(f"Token counting failed: {e}")
            # Fallback estimation (approx 4 chars per token)
            return len(text) // 4
