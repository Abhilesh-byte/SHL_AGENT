"""
Post-hoc validation. Never trust the LLM's JSON blindly — this is the
"agent design" safety net that catches the hallucination behavior probes.
"""


def validate_and_clean(llm_json: dict, valid_urls: set[str], phase: str) -> dict:
    reply = llm_json.get("reply", "").strip() or "Sorry, could you rephrase that?"
    recs = llm_json.get("recommendations", []) or []
    end_flag = bool(llm_json.get("end_of_conversation", False))

    # Hard rule: strip any recommendation whose URL isn't in our real catalog.
    # This is the single most important line against hallucination.
    clean_recs = [r for r in recs if r.get("url") in valid_urls]

    # Hard rule: CLARIFY / COMPARE / REFUSE must never carry recommendations.
    if phase in ("CLARIFY", "COMPARE", "REFUSE"):
        clean_recs = []
        end_flag = False

    # Hard rule: cap at 10 items per spec.
    clean_recs = clean_recs[:10]

    # Hard rule: end_of_conversation only true when we actually committed a list.
    if phase in ("RECOMMEND", "REFINE") and not clean_recs:
        end_flag = False

    return {
        "reply": reply,
        "recommendations": clean_recs,
        "end_of_conversation": end_flag,
    }