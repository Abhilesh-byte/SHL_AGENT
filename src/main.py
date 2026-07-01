"""
This file is the ONLY place all the other modules meet. Trace a single
request through it and you've understood the whole system:

  request  ->  router.route_phase        (decide what kind of turn this is)
           ->  retriever.search           (pull relevant catalog candidates)
           ->  prompts.build_prompt       (turn phase+history+candidates into text)
           ->  llm_client.call_llm        (get the model's JSON)
           ->  validators.validate_and_clean  (guardrail the output)
           ->  response

Run locally:
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

Then test with:
    python test_client.py
"""
from router import route_phase
from retriever import retriever
from prompts import build_prompt, REFUSAL_REPLY
from llm_client import call_llm
from validators import validate_and_clean
app = FastAPI(title="SHL Assessment Recommender")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(req: ChatRequest):
    messages = [m.model_dump() for m in req.messages]

    # 1. Route: deterministic pre-check decides the conversational phase
    phase = route_phase(messages)

    if phase == "REFUSE":
        return {"reply": REFUSAL_REPLY, "recommendations": [], "end_of_conversation": False}

    # 2. Retrieve: pull a relevant candidate slice, not the whole catalog
    query_text = " ".join(m["content"] for m in messages if m["role"] == "user")
    candidates = retriever.search(query_text, top_k=15)

    # 3. Prompt: build phase-specific instructions grounded in those candidates
    prompt = build_prompt(phase, messages, candidates)

    # 4. LLM call
    raw = await call_llm(prompt)

    # 5. Validate: strip hallucinated URLs, enforce schema hard rules
    result = validate_and_clean(raw, retriever.valid_urls, phase)

    return result