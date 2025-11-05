from __future__ import annotations

from typing import Any, Dict, List, Optional

from .client import MiniMaxClient


def generate_text(
    client: MiniMaxClient,
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    system: Optional[str] = None,
    tools: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Call MiniMax chat completions endpoint using configured base URL.

    messages: list of {role: "system"|"user"|"assistant", content: str}
    If `system` is provided, it is prepended as a system message.
    """
    payload_messages = list(messages)
    if system:
        payload_messages = [{"role": "system", "content": system}] + payload_messages

    kwargs: Dict[str, Any] = {"temperature": temperature}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if tools:
        kwargs["tools"] = tools

    return client.chat_completions(payload_messages, model=model, **kwargs)

