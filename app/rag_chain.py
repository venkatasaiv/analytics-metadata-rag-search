"""RAG chain for analytics metadata search using BigQuery Vector Store."""

from typing import List, Dict, Any
from langchain_google_community import BigQueryVectorStore
from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI
from app import config

# Initialize embedding model and LLM
embedding = VertexAIEmbeddings(
    model_name=config.EMBED_MODEL,
    project=config.PROJECT_ID
)

llm = ChatVertexAI(
    model_name=config.LLM_MODEL,
    project=config.PROJECT_ID,
    temperature=config.TEMPERATURE
)

# Initialize BigQuery Vector Store
vector_store = BigQueryVectorStore(
    project_id=config.PROJECT_ID,
    dataset_name=config.BQ_DATASET,
    table_name=config.BQ_TABLE,
    location=config.BQ_LOCATION,
    embedding=embedding,
)

SYSTEM_PROMPT = (
    "You are an enterprise analytics assistant. "
    "Answer only using the provided analytics metadata about reports, metrics, and dimensions. "
    "If the answer is unclear or not found in the context, say you don't know. "
    "Be concise and specific in your responses."
)

def retrieve_metadata(
    query: str, 
    domain: str | None = None,
    top_k: int = config.TOP_K_RESULTS
) -> List[Dict[str, Any]]:
    """Retrieve relevant metadata from BigQuery Vector Store.
    
    Args:
        query: User's search query
        domain: Optional business domain filter
        top_k: Number of results to retrieve
        
    Returns:
        List of relevant document metadata
    """
    filter_dict = {}
    if domain:
        filter_dict["domain"] = domain
    
    docs = vector_store.similarity_search(
        query=query,
        k=top_k,
        filter=filter_dict or None,
    )
    
    return [
        {
            "page_content": d.page_content,
            "metadata": d.metadata
        } for d in docs
    ]

def build_context(docs: List[Dict[str, Any]]) -> str:
    """Build formatted context string from retrieved documents.
    
    Args:
        docs: List of retrieved documents with metadata
        
    Returns:
        Formatted context string
    """
    if not docs:
        return "No relevant analytics metadata found."
    
    blocks = []
    for i, d in enumerate(docs, 1):
        m = d["metadata"]
        blocks.append(
            f"{i}. Type: {m.get('type', 'N/A')} | Title: {m.get('title', 'N/A')}\n"
            f"   Domain: {m.get('domain', 'N/A')} | Owner: {m.get('owner', 'N/A')}\n"
            f"   Tool: {m.get('bi_tool', 'N/A')} | Tags: {m.get('tags', 'N/A')}\n"
            f"   Summary: {d['page_content']}"
        )
    return "\n\n".join(blocks)

def answer_question(
    query: str, 
    domain: str | None = None
) -> Dict[str, Any]:
    """Answer a question using RAG over analytics metadata.
    
    Args:
        query: User's question
        domain: Optional business domain filter
        
    Returns:
        Dictionary with answer and matching documents
    """
    # Retrieve relevant metadata
    docs = retrieve_metadata(query, domain=domain)
    
    # Build context
    context = build_context(docs)
    
    # Build prompt
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context (Analytics Metadata):\n{context}\n\n"
        f"User question: {query}"
    )
    
    # Get LLM response
    resp = llm.invoke(prompt)
    
    return {
        "answer": resp.content,
        "matches": docs,
        "num_matches": len(docs)
    }
