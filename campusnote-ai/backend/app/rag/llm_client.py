"""
LLM Client
==========
Thin wrapper around the Anthropic Claude API. The API key and model name
are read from environment variables (never hardcoded), per Section 27.
"""
import logging
from anthropic import Anthropic, APIError
from app.config import settings

logger = logging.getLogger("campusnote.llm")

_client = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        if not settings.LLM_API_KEY:
            raise RuntimeError(
                "LLM_API_KEY is not set. Add it to backend/.env (see .env.example)."
            )
        _client = Anthropic(api_key=settings.LLM_API_KEY)
    return _client


def generate_answer(system_prompt: str, user_prompt: str) -> str:
    """Calls the LLM and returns the generated answer text.
    Raises RuntimeError on failure so the route layer can return a clean
    error response instead of a raw stack trace (Section 24)."""
    try:
        client = get_client()
        response = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=settings.LLM_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
        return "\n".join(parts).strip()
    except APIError as e:
        logger.error(f"LLM API error: {e}")
        raise RuntimeError("The AI service is temporarily unavailable. Please try again shortly.")
    except Exception as e:
        logger.error(f"Unexpected LLM error: {e}")
        raise RuntimeError("Something went wrong while generating the answer.")
