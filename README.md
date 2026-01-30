# Analytics Metadata RAG Search

**RAG-inspired conversational analytics search** using LangChain, BigQuery Vector Search, and Vertex AI embeddings over structured analytics metadata on GCP.

## Overview

This project implements a semantic search system for analytics documentation and metadata, enabling data analysts and stakeholders to discover insights through natural language queries. Instead of querying raw data, it searches over **structured analytics metadata** (reports, metrics, dimensions) using retrieval-augmented generation (RAG).

### Key Features

- **Semantic Search**: Vector embeddings enable finding relevant analytics assets by meaning, not just keywords
- **BigQuery Vector Store**: Native integration with BigQuery for scalable vector search
- **LangChain Integration**: Modular RAG pipeline using LangChain for Google Cloud
- **FastAPI REST API**: Clean API for integration with dashboards or chat interfaces
- **Metadata-Only**: No direct data warehouse querying—safe for documentation discovery

## Architecture

```
User Query
    ↓
FastAPI Endpoint
    ↓
Vector Embedding (Vertex AI)
    ↓
BigQuery Vector Search
    ↓
Retrieved Metadata (top-k)
    ↓
Context Injection → LLM (Gemini)
    ↓
Natural Language Answer + Source Links
```

## Tech Stack

- **LangChain**: Orchestration framework
- **Google BigQuery**: Vector store for embeddings and metadata
- **Vertex AI**: Text embeddings (`text-embedding-004`) and LLM (`gemini-1.5-pro`)
- **FastAPI**: REST API framework
- **Python 3.11+**

## Project Structure

```
analytics-metadata-rag-search/
├── app/
│   ├── config.py         # Configuration and environment variables
│   ├── rag_chain.py      # Core RAG logic (retrieval + LLM)
│   └── main.py           # FastAPI application
├── scripts/
│   ├── generate_metadata.py    # Create synthetic metadata
│   └── build_embeddings.py     # Generate embeddings and load to BigQuery
├── data/
│   ├── reports.csv       # Sample report metadata
│   └── metrics.csv       # Sample metric definitions
├── requirements.txt
├── Dockerfile
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- GCP Project with:
  - BigQuery API enabled
  - Vertex AI API enabled
  - Service account with appropriate permissions
- `gcloud` CLI configured

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/venkatasaiv/analytics-metadata-rag-search.git
   cd analytics-metadata-rag-search
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   GCP_PROJECT_ID=your-gcp-project-id
   BQ_DATASET=analytics_metadata
   BQ_TABLE=metadata_embeddings
   BQ_LOCATION=US
   EMBED_MODEL=text-embedding-004
   LLM_MODEL=gemini-1.5-pro
   ```

4. **Authenticate with GCP**:
   ```bash
   gcloud auth application-default login
   ```

### Build Vector Store

1. **Create BigQuery dataset**:
   ```bash
   bq mk --dataset --location=US your-project-id:analytics_metadata
   ```

2. **Generate and load embeddings** (example script):
   ```bash
   python scripts/build_embeddings.py
   ```

## Usage

### Run the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

### API Endpoints

#### `POST /ask`

Ask a question about analytics metadata.

**Request**:
```json
{
  "query": "What are the key metrics for sales performance?",
  "domain": "sales"
}
```

**Response**:
```json
{
  "answer": "The key metrics for sales performance include...",
  "matches": [
    {
      "page_content": "Report: Sales Performance Dashboard...",
      "metadata": {
        "type": "report",
        "title": "Sales Performance Dashboard",
        "domain": "sales",
        "owner": "Analytics Team"
      }
    }
  ],
  "num_matches": 5
}
```

#### `GET /health`

Health check endpoint.

## Deployment

### Cloud Run

Build and deploy to Cloud Run:

```bash
# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/analytics-rag-search

# Deploy to Cloud Run
gcloud run deploy analytics-rag-search \
  --image gcr.io/YOUR_PROJECT_ID/analytics-rag-search \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID,BQ_DATASET=analytics_metadata
```

## Design Decisions

### Why Metadata-Only?

- **Security**: No direct access to raw analytics data
- **Performance**: Lighter queries, faster responses
- **Scope**: Focused on discovery, not ad-hoc querying

### Why BigQuery Vector Search?

- **Native Integration**: No separate vector database to manage
- **Scalability**: Handles millions of vectors
- **Cost-Effective**: Pay-per-query pricing
- **Ecosystem**: Integrates with existing GCP data infrastructure

### RAG vs. Fine-Tuning

- **RAG**: Dynamic, updatable knowledge base without retraining
- **Lower Cost**: No model training/hosting overhead
- **Transparency**: Retrieved documents are traceable

## Limitations

- **No SQL Generation**: This is intentionally not a text-to-SQL system
- **Metadata Quality**: Search quality depends on well-documented metadata
- **Cold Start**: First query after deployment may be slow (LLM initialization)

## Future Enhancements

- [ ] Add metadata filtering by BI tool, owner, tags
- [ ] Implement hybrid search (vector + keyword)
- [ ] Add feedback loop for relevance tuning
- [ ] Build Streamlit UI for non-technical users
- [ ] Add metadata versioning and lineage tracking

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgements

- [LangChain](https://langchain.com/) for RAG orchestration
- [Google Cloud BigQuery](https://cloud.google.com/bigquery) for vector search
- [Vertex AI](https://cloud.google.com/vertex-ai) for embeddings and LLM
