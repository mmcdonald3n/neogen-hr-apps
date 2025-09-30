# utils/llm.py
import os
import streamlit as st
from openai import OpenAI

def chat_complete(prompt: str, *, max_tokens: int = 1800, system: str | None = None, temperature: float | None = None) -> str:
    """
    Unified wrapper for Chat Completions:
      - prompt: plain string
      - system: optional system string
      - returns assistant text
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    # try a few likely places for model/temp set in your app
    model = (st.session_state.get("openai_model")
             or st.session_state.get("model")
             or "gpt-4o-mini")
    temp = temperature if temperature is not None else float(st.session_state.get("temperature", 0.2))

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp,
        max_tokens=max_tokens
    )
    return resp.choices[0].message.content.strip()
