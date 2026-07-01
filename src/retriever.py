"""
Retrieval layer. This is the ONLY file that reads catalog.json directly.
Everything downstream (router, prompts, main) asks THIS module for candidates
instead of touching the JSON file itself — that's the "join" contract.
"""
import json
import re
from pathlib import Path
from rank_bm25 import BM25Okapi

CATALOG_PATH = Path(__file__).parent / "catalog.json"


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class CatalogRetriever:
    def __init__(self, catalog_path: Path = CATALOG_PATH):
        with open(catalog_path) as f:
            self.catalog: list[dict] = json.load(f)

        corpus = [f"{c['name']} {c['description']}" for c in self.catalog]
        self.tokenized_corpus = [_tokenize(doc) for doc in corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        # Fast lookup used later by the URL-hallucination validator
        self.valid_urls = {c["url"] for c in self.catalog}
        self.by_url = {c["url"]: c for c in self.catalog}

    def search(self, query: str, top_k: int = 15, type_filter: list[str] | None = None) -> list[dict]:
        if not query.strip():
            results = self.catalog[:top_k]
        else:
            scores = self.bm25.get_scores(_tokenize(query))
            ranked = sorted(zip(self.catalog, scores), key=lambda pair: -pair[1])
            results = [c for c, score in ranked if score > 0][:top_k]
            if not results:  # BM25 found nothing — fall back to full catalog slice
                results = self.catalog[:top_k]

        if type_filter:
            filtered = [c for c in results if any(t in c["test_type"] for t in type_filter)]
            if filtered:
                results = filtered

        return results

    def get_by_name(self, name: str) -> dict | None:
        name_lower = name.lower()
        for c in self.catalog:
            if c["name"].lower() == name_lower:
                return c
        return None


# Singleton instance — loaded once at process start, reused across requests.
# This is what "stateless per-conversation, but not per-process" means:
# the catalog itself is shared, immutable, read-only state. That's fine.
# It's CONVERSATION state that must never be cached here.
retriever = CatalogRetriever()