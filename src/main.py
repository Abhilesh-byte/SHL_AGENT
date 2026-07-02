from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

try:  # Supports both `uvicorn src.main:app` and `cd src && uvicorn main:app`.
    from .llm_client import call_llm
    from .prompts import REFUSAL_REPLY, build_prompt
    from .retriever import retriever
    from .router import route_phase
    from .validators import validate_and_clean
    from .web_app import APP_HTML
except ImportError:  # pragma: no cover - convenience for direct local execution.
    from llm_client import call_llm
    from prompts import REFUSAL_REPLY, build_prompt
    from retriever import retriever
    from router import route_phase
    from validators import validate_and_clean
    from web_app import APP_HTML


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    messages: list[Message] = Field(..., min_length=1)


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1)


class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str


class ChatResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation]
    end_of_conversation: bool


app = FastAPI(
    title="SHL Assessment Recommender API",
    description="Conversational API for recommending SHL assessments from a local catalog.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _message_dicts(messages: list[Message]) -> list[dict[str, str]]:
    return [message.model_dump() for message in messages]


def _conversation_query(messages: list[dict[str, str]]) -> str:
    return "\n".join(message["content"] for message in messages if message["role"] == "user")


async def _run_agent(messages: list[dict[str, str]]) -> dict:
    phase = route_phase(messages)

    if phase == "REFUSE":
        return validate_and_clean(
            {
                "reply": REFUSAL_REPLY,
                "recommendations": [],
                "end_of_conversation": False,
            },
            retriever.valid_urls,
            phase,
        )

    candidates = retriever.search(_conversation_query(messages), top_k=15)
    prompt = build_prompt(phase, messages, candidates)

    try:
        llm_json = await call_llm(prompt)
    except Exception as exc:  # Provider/network/key failures should be explicit to API callers.
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider call failed: {exc}",
        ) from exc

    return validate_and_clean(llm_json, retriever.valid_urls, phase)


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    return APP_HTML


@app.get("/app", response_class=HTMLResponse)
async def web_app() -> str:
    return APP_HTML


@app.get("/api")
async def api_info() -> dict[str, str]:
    return {
        "name": "SHL Assessment Recommender API",
        "health": "/health",
        "catalog": "/catalog",
        "chat": "/chat",
        "recommend": "/recommend",
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/catalog")
async def catalog() -> list[dict]:
    return retriever.catalog


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> dict:
    return await _run_agent(_message_dicts(request.messages))


@app.post("/recommend", response_model=ChatResponse)
async def recommend(request: RecommendRequest) -> dict:
    return await _run_agent([{"role": "user", "content": request.query}])
