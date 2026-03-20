"""OpenAI integration layer for BA Compass."""

from __future__ import annotations

import logging
import time
from typing import Any, Generator

import streamlit as st

LOGGER = logging.getLogger(__name__)

_MODEL = "gpt-4o"
_MAX_RETRIES = 3
_RETRY_BASE_SECONDS = 2


def _get_client():
    """Return an OpenAI client using the API key from Streamlit secrets."""
    try:
        from openai import OpenAI
        return OpenAI(api_key=st.secrets["openai_api_key"])
    except KeyError:
        raise RuntimeError(
            "OpenAI API key not found. Add 'openai_api_key' to your Streamlit secrets."
        )
    except Exception as exc:
        raise RuntimeError("Failed to initialise the OpenAI client.") from exc


def call_openai(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    json_mode: bool = False,
) -> str:
    """Send a chat completion request and return the response text.

    Retries up to _MAX_RETRIES times with exponential backoff on transient errors.
    Raises RuntimeError with a user-friendly message on failure.
    """
    client = _get_client()
    kwargs: dict[str, Any] = {
        "model": _MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as exc:
            last_exc = exc
            LOGGER.warning("OpenAI call failed (attempt %d/%d): %s", attempt + 1, _MAX_RETRIES, exc)
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_BASE_SECONDS * (2 ** attempt))

    LOGGER.error("OpenAI call failed after %d attempts: %s", _MAX_RETRIES, last_exc)
    raise RuntimeError(
        "The AI service is not responding right now. Your work is saved — please try again in a moment."
    )


def stream_openai(
    messages: list[dict[str, str]],
    temperature: float = 0.4,
) -> Generator[str, None, None]:
    """Stream a chat completion, yielding text chunks as they arrive.

    Falls back to a single call if streaming fails.
    """
    client = _get_client()
    try:
        with client.chat.completions.create(
            model=_MODEL,
            messages=messages,
            temperature=temperature,
            stream=True,
        ) as stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
    except Exception as exc:
        LOGGER.warning("Streaming failed, falling back to single call: %s", exc)
        yield call_openai(messages, temperature=temperature)


def truncate_conversation(
    messages: list[dict[str, str]],
    system_prompt: str,
    max_turns: int = 10,
) -> list[dict[str, str]]:
    """Keep the system prompt plus the most recent max_turns user/assistant pairs."""
    non_system = [m for m in messages if m["role"] != "system"]
    if len(non_system) > max_turns * 2:
        non_system = non_system[-(max_turns * 2):]
    return [{"role": "system", "content": system_prompt}] + non_system
