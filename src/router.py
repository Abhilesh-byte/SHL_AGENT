"""
Deterministic phase routing. We do NOT let the LLM freely decide "what kind
of turn is this" from scratch every time — that's how you get the
conversational incoherence the assignment explicitly warns about. Instead,
cheap rule-based checks narrow it down, and only genuinely ambiguous judgment
(e.g. "is this query specific enough yet?") is left to the LLM inside the
chosen phase's prompt.
"""
import re

OFF_TOPIC_PATTERNS = [
    r"\bignore (all|previous|the) instructions\b",
    r"\bsystem prompt\b",
    r"\byou are now\b",
    r"\bdisregard\b.*\bguidelines\b",
    r"\blabor law\b",
    r"\bemployment law\b",
    r"\bshould i fire\b",
    r"\bhr strategy\b",
    r"\bwrite (a|my) resume\b",
]

COMPARISON_PATTERNS = [
    r"\bdifference between\b",
    r"\bcompare\b",
    r"\bvs\.?\b",
    r"\bversus\b",
    r"\bwhich (one|is better)\b",
]

REFINEMENT_PATTERNS = [
    r"\balso\b", r"\badd\b", r"\bactually\b", r"\binstead\b",
    r"\bremove\b", r"\bswap\b", r"\bwhat about\b", r"\bcan you also\b",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    text = text.lower()
    return any(re.search(p, text) for p in patterns)


RECOMMENDATION_MARKER = re.compile(r"Recommended:\s*(.+)$", re.IGNORECASE | re.MULTILINE)


def extract_previous_shortlist_names(messages: list[dict]) -> list[str]:
    """
    IMPORTANT: the API is stateless and conversation history only carries
    {role, content} plain strings — the structured `recommendations` array
    from a prior turn is NOT replayed back to us. So if we need to know what
    we recommended last time (to support REFINE), we have to recover it from
    the plain-text `reply` we ourselves wrote.

    Fix: whenever main.py sends a committed shortlist, it appends a
    machine-parseable trailer line "Recommended: Name A, Name B, ..." to the
    human-readable reply (see prompts.py / main.py). We parse that back out
    here. This keeps the reply natural for the simulated user while giving
    us continuity across stateless turns.
    """
    names: list[str] = []
    for m in messages:
        if m["role"] == "assistant":
            match = RECOMMENDATION_MARKER.search(m.get("content", ""))
            if match:
                names = [n.strip() for n in match.group(1).split(",") if n.strip()]
    return names


def has_committed_recommendations(messages: list[dict]) -> bool:
    return len(extract_previous_shortlist_names(messages)) > 0


def has_enough_context(messages: list[dict]) -> bool:
    """
    Heuristic: require at least a role/skill signal AND one qualifying detail
    (seniority, a named competency, or a pasted job description of decent
    length) across the conversation so far. This stops the agent from
    recommending on turn 1 for a bare "I need a test", while not looping
    forever if the user gives everything up front.
    """
    user_turns = [m["content"] for m in messages if m["role"] == "user"]
    combined = " ".join(user_turns).lower()

    role_signal = bool(re.search(
        r"\b(developer|engineer|analyst|manager|sales|support|admin|"
        r"accountant|designer|java|python|sql|customer service)\b", combined))

    qualifier_signal = bool(re.search(
        r"\b(senior|junior|mid|entry|graduate|years?|stakeholder|leadership|"
        r"team|communication|personality|cognitive|behavioral|remote)\b",
        combined
    )) or len(combined) > 200  # a pasted JD counts as sufficient context

    # Also: after 2+ user turns, be more willing to act even with partial info
    # — the evaluator's simulated user may refuse to give more detail.
    turns_exhausted = len(user_turns) >= 3

    return (role_signal and qualifier_signal) or turns_exhausted


def route_phase(messages: list[dict]) -> str:
    last_user_msg = messages[-1]["content"] if messages else ""

    if _matches_any(last_user_msg, OFF_TOPIC_PATTERNS):
        return "REFUSE"

    if _matches_any(last_user_msg, COMPARISON_PATTERNS):
        return "COMPARE"

    if has_committed_recommendations(messages) and _matches_any(last_user_msg, REFINEMENT_PATTERNS):
        return "REFINE"

    if has_enough_context(messages):
        return "RECOMMEND"

    return "CLARIFY"