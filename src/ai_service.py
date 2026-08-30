"""Groq integration. Pandas performs analysis; Groq only explains results."""

from __future__ import annotations

import json
import os

import streamlit as st


def secret_or_env(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(name)


def groq_explanation(payload: dict) -> str:
    api_key = secret_or_env("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add it in Streamlit Cloud → App settings → Secrets."
        )

    from groq import Groq

    client = Groq(api_key=api_key)
    prompt = f"""
You are a senior food-delivery operations analyst.
Use ONLY the calculated Python/Pandas results below.
Do not invent statistics.

Write:
1) a 2-sentence executive summary,
2) the three most important operational findings,
3) three prioritized actions,
4) one monitoring recommendation.

Keep the language concise, practical, and suitable for a business presentation.

Calculated results:
{json.dumps(payload, indent=2, default=str)}
"""
    response = client.chat.completions.create(
        model=secret_or_env("GROQ_MODEL") or "openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You explain calculated analytics clearly for business decision-makers.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=900,
    )
    return response.choices[0].message.content

