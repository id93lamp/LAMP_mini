"""
DeepSeek API Backend
====================
Wraps DeepSeek's API (OpenAI-compatible) for use as the LAMP backend.

Model  : deepseek-v4-pro
Auth   : DEEPSEEK_API_KEY in .env

Converts Anthropic-format messages/tool schemas to the OpenAI format
and converts the response back to Anthropic content[] format.
"""

import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "deepseek-v4-pro"
_MAX_RETRIES = 5
_RETRY_BASE_DELAY = 5


def _anthropic_to_openai(messages: list) -> list:
    """Convert Anthropic-format conversation turns to OpenAI format."""
    out = []
    for m in messages:
        role = m["role"]
        content = m["content"]
        if isinstance(content, str):
            out.append({"role": role, "content": content})
        elif isinstance(content, list):
            if role == "assistant":
                text = "".join(b.get("text", "") for b in content if b.get("type") == "text")
                tool_calls = [
                    {
                        "id": b["id"],
                        "type": "function",
                        "function": {"name": b["name"], "arguments": json.dumps(b.get("input", {}))},
                    }
                    for b in content if b.get("type") == "tool_use"
                ]
                msg: dict = {"role": "assistant", "content": text or None}
                if tool_calls:
                    msg["tool_calls"] = tool_calls
                out.append(msg)
            elif role == "user":
                for b in content:
                    if b.get("type") == "text":
                        out.append({"role": "user", "content": b["text"]})
                    elif b.get("type") == "tool_result":
                        out.append({
                            "role": "tool",
                            "tool_call_id": b["tool_use_id"],
                            "content": str(b.get("content", "")),
                        })
    return out


def generate_with_tools(messages: list, system_prompt: str = "", tools: list = None) -> dict:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        print("[Warning] Valid DEEPSEEK_API_KEY not found. Simulating response.")
        return {"content": [{"type": "text", "text": "```lean4\nsorry\n```"}]}

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    openai_messages = _anthropic_to_openai(messages)
    if system_prompt:
        openai_messages.insert(0, {"role": "system", "content": system_prompt})

    openai_tools = None
    if tools:
        openai_tools = [
            {"type": "function", "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["input_schema"],
            }}
            for t in tools
        ]

    for attempt in range(_MAX_RETRIES):
        try:
            kwargs: dict = {"model": MODEL, "messages": openai_messages, "temperature": 0.0}
            if openai_tools:
                kwargs["tools"] = openai_tools
            response = client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            content = []
            if message.content:
                content.append({"type": "text", "text": message.content})
            if message.tool_calls:
                for tc in message.tool_calls:
                    content.append({
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.function.name,
                        "input": json.loads(tc.function.arguments),
                    })
            return {"content": content}
        except Exception as e:
            delay = _RETRY_BASE_DELAY * (2 ** attempt)
            print(f"[DeepSeek] Attempt {attempt + 1}/{_MAX_RETRIES} failed: {e}. Retrying in {delay}s…")
            time.sleep(delay)

    print("[DeepSeek] All retries exhausted. Returning fallback.")
    return {"content": [{"type": "text", "text": "```lean4\nsorry\n```"}]}
