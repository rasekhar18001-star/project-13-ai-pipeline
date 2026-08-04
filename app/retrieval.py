"""Deterministic lexical retrieval over the fixed policy corpus."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Document:
    id: str
    text: str
    path: Path


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.casefold())


def load_corpus(directory: Path | None = None) -> list[Document]:
    corpus = directory or ROOT / "data/policies"
    documents = []
    for path in sorted(corpus.glob("*.md")):
        documents.append(Document(path.stem, path.read_text(encoding="utf-8"), path))
    if not documents:
        raise ValueError(f"no policy documents found in {corpus}")
    return documents


class LexicalRetriever:
    def __init__(self, documents: list[Document] | None = None) -> None:
        self.documents = documents or load_corpus()

    def retrieve(self, question: str, top_k: int = 3) -> list[Document]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        query = tokenize(question)
        if not query:
            return []
        qset = set(query)
        scored = []
        for doc in self.documents:
            tokens = tokenize(doc.text)
            score = sum(tokens.count(term) for term in qset) + 2 * len(qset & set(tokenize(doc.id.replace("_", " "))))
            if score:
                scored.append((score, doc.id, doc))
        scored.sort(key=lambda item: (-item[0], item[1]))
        return [item[2] for item in scored[:top_k]]
