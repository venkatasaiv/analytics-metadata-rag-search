"""FastAPI application for analytics metadata RAG search."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.rag_chain import answer_question

app = FastAPI(
    title="Analytics Metadata RAG Search",
    description="RAG-inspired conversational search over analytics metadata",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    """Request model for /ask endpoint."""
    query: str
    domain: Optional[str] = None

class Match(BaseModel):
    """Model for a single metadata match."""
    page_content: str
    metadata: Dict[str, Any]

class QueryResponse(BaseModel):
    """Response model for /ask endpoint."""
    answer: str
    matches: List[Match]
    num_matches: int

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Analytics Metadata RAG Search API",
        "endpoints": {
            "/ask": "POST - Ask a question about analytics metadata",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    """Ask a question about analytics metadata.
    
    Args:
        request: Query request containing question and optional domain filter
        
    Returns:
        QueryResponse with answer and relevant matches
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        result = answer_question(
            query=request.query,
            domain=request.domain
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
