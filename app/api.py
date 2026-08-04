"""FastAPI entry point."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.rag import RAGService

app = FastAPI(title="Fictional School Policy RAG")


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask")
def ask(request: AskRequest) -> dict[str, object]:
    return RAGService().answer(request.question)
