"""
Thin abstraction over the LLM provider. main.py only ever calls call_llm() —
it never knows or cares whether that's Groq, Gemini, or a mock. This is the
"join" pattern: swap the provider by changing ONE file, not scattered API
calls throughout the codebase.

Set LLM_PROVIDER=mock while developing without API keys (see MockProvider
below) — it returns deterministic, schema-valid JSON so you can test the
whole pipeline (routing -> retrieval -> prompt -> validation) without
spending a single real API call.
"""
import os
import json
import re

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "mock")


def _strip_code_fences(text: str) -> str:
    """LLMs sometimes wrap JSON in ```json ... ``` even when told not to."""
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()


async def call_groq(prompt: str) -> dict:
    import httpx
    api_key = os.environ["GROQ_API_KEY"]
    async with httpx.AsyncClient(timeout=25) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
        )
        resp.raise_for_status()
        raw_text = resp.json()["choices"][0]["message"]["content"]
    return json.loads(_strip_code_fences(raw_text))


async def call_gemini(prompt: str) -> dict:
    import httpx
    api_key = os.environ["GEMINI_API_KEY"]
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={api_key}"
    )
    async with httpx.AsyncClient(timeout=25) as client:
        resp = await client.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        })
        resp.raise_for_status()
        raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(_strip_code_fences(raw_text))


class MockProvider:
    """
    Deterministic stand-in used for local wiring tests (no API key needed).
    It doesn't understand the prompt semantically — it just returns
    schema-valid JSON so you can verify the pipeline plumbing works before
    spending real API calls or when a key isn't configured yet.
    """
    async def call(self, prompt: str) -> dict:
        if "PHASE: CLARIFY" in prompt:
            return {
                "reply": "Could you tell me the seniority level and key skills for this role?",
                "recommendations": [],
                "end_of_conversation": False,
            }
        if "PHASE: COMPARE" in prompt:
            return {
                "reply": "Based on the catalog, these assessments differ in what they measure — "
                         "one focuses on personality traits, the other on cognitive ability.",
                "recommendations": [],
                "end_of_conversation": False,
            }
        # RECOMMEND / REFINE: pull the first two candidate lines out of the prompt
        candidate_lines = re.findall(r"- name: (.+?) \| url: (.+?) \| type: (.+?) \|", prompt)
        picks = candidate_lines[:2] if candidate_lines else []
        names = ", ".join(p[0] for p in picks)
        return {
            "reply": f"Here are assessments matching your needs.\nRecommended: {names}",
            "recommendations": [
                {"name": n, "url": u, "test_type": t} for n, u, t in picks
            ],
            "end_of_conversation": True,
        }


async def call_llm(prompt: str) -> dict:
    if LLM_PROVIDER == "groq":
        return await call_groq(prompt)
    if LLM_PROVIDER == "gemini":
        return await call_gemini(prompt)
    return await MockProvider().call(prompt)