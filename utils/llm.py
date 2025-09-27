import os
from typing import List, Dict, Any, Optional

def _get_api_key() -> Optional[str]:
    # Prefer Streamlit secrets if available
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY", None)
        if key:
            return str(key)
    except Exception:
        pass
    # Fallback to env var
    return os.getenv("OPENAI_API_KEY")

def chat_complete(model: str, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1500) -> str:
    """
    Adapter that tries the new OpenAI SDK first (client.chat.completions.create),
    then falls back to legacy openai.ChatCompletion.create if needed.
    """
    api_key = _get_api_key()
    if not api_key:
        return "[ERROR] No OpenAI API key found. Add it to .streamlit/secrets.toml (OPENAI_API_KEY) or as env var."

    # New SDK path
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content
    except Exception:
        pass

    # Legacy SDK path
    try:
        import openai
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[ERROR] OpenAI call failed: {e}"
