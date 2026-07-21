from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IngestPathRequest(BaseModel):
    path: str = Field(
        ..., description="Directory containing source documents to ingest."
    )


class FAQQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language FAQ query.")
    top_k: int = Field(
        5, ge=1, le=20, description="Maximum number of snippets to return."
    )


class FAQDocumentResponse(BaseModel):
    page_content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None


class FAQVectorQueryRequest(BaseModel):
    knowledge_base_id: str = Field(
        ..., description="Identifier of the knowledge base to query."
    )
    query: str = Field(..., min_length=1, description="Natural language FAQ query.")


class AzureDocumentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query.")
    top_k: int = Field(5, ge=1, le=20)


class KBQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query.")
    top_k: int = Field(5, ge=1, le=50)


class KBIngestResponse(BaseModel):
    knowledge_base_id: str
    chunks: int
    message: str


class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class RAGQueryResponse(BaseModel):
    results: List[dict]
    query: str
    total_results: int
    metadata: Optional[dict] = None
