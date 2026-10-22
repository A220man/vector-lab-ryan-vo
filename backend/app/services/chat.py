from typing import Dict, Any, Optional
import os


async def chat_completion(
    message: str,
    context: str = "",
    model: Optional[str] = None,
) -> tuple[str, Dict[str, Any]]:
    """
    Chat completion with usage tracking.
    In production, this would call an LLM API.
    For now, returns a mock response with simulated usage.
    """
    # Check if we have an API key configured
    api_key = os.getenv("LLM_API_KEY")

    if not api_key:
        # Demo mode - return mock response
        response = (
            f"Based on the document context, here's my response to: '{message}'\n\n"
            f"Context summary: {context[:200]}..." if context else "No document context provided."
        )

        usage = {
            "model": model or "demo-model",
            "input_tokens": len((message + context).split()) * 1.3,
            "output_tokens": len(response.split()) * 1.3,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "complete": 1,  # 1=complete, 0=partial, -1=unknown
        }
        # Round to integers
        usage = {k: int(v) if isinstance(v, float) else v for k, v in usage.items()}
        return response, usage

    # TODO: Implement real LLM call with httpx
    # Would use OpenAI-compatible, Anthropic, or Gemini adapters
    # Track per-call usage with complete/partial/unknown states

    raise NotImplementedError("LLM integration not yet implemented")