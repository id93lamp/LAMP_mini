"""
Claude API Backend
==================
Wraps Anthropic's Claude API for use as the LAMP LLM backend.

Model  : claude-sonnet-4-5  (configurable via MODEL constant)
Auth   : CLAUDE_API_KEY in .env
Retry  : Exponential back-off on 429 / 529 (rate-limit / overload).

The response format follows Anthropic's Messages API and is returned
as-is to the Planner and Builder (they parse content[] blocks).
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-5"
_MAX_RETRIES = 5
_RETRY_BASE_DELAY = 10  # seconds; doubled each retry


def generate_with_tools(messages: list, system_prompt: str = "", tools: list = None) -> dict:
    """
    Call the Claude API with optional tool schemas.

    Parameters
    ----------
    messages      : List of Anthropic-format conversation turns.
    system_prompt : System instruction for this agent.
    tools         : Optional list of Anthropic tool schema dicts.

    Returns
    -------
    dict with 'content' list of text / tool_use blocks.
    """
    api_key = os.getenv("CLAUDE_API_KEY", "")
    if not api_key or api_key == "your_claude_api_key_here":
        print("[Warning] Valid CLAUDE_API_KEY not found. Simulating LLM response.")
        return {"content": [{"type": "text", "text": "```lean4\nsorry\n```"}]}

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    data: dict = {"model": MODEL, "max_tokens": 2048, "messages": messages}
    if system_prompt:
        data["system"] = system_prompt
    if tools:
        data["tools"] = tools

    for attempt in range(_MAX_RETRIES):
        response = None
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=120,
            )
            if response.status_code in (429, 529):
                delay = _RETRY_BASE_DELAY * (2 ** attempt)
                print(f"[Claude] {response.status_code} — retrying in {delay}s "
                      f"(attempt {attempt + 1}/{_MAX_RETRIES})")
                time.sleep(delay)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            delay = _RETRY_BASE_DELAY * (2 ** attempt)
            print(f"[Claude] Timeout — retrying in {delay}s (attempt {attempt + 1}/{_MAX_RETRIES})")
            time.sleep(delay)
        except Exception as e:
            detail = response.text if response and hasattr(response, "text") else ""
            print(f"[Claude] Error: {e}" + (f"\n{detail}" if detail else ""))
            if response is not None and response.status_code not in (429, 529):
                break

    print(f"[Claude] All {_MAX_RETRIES} retries exhausted. Returning fallback.")
    return {"content": [{"type": "text", "text": "```lean4\nsorry\n```"}]}
