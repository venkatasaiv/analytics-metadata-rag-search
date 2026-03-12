# Analytics Metadata RAG Search

**Conversational search over structured analytics metadata using RAG — LangChain + BigQuery Vector Search + Vertex AI embeddings + Gemini + FastAPI, deployed on GCP.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)
![GCP](https://img.shields.io/badge/GCP-4285F4?style=flat&logo=google-cloud&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-4285F4?style=flat&logo=google-bigquery&logoColor=white)

---

## What This Is

Data analysts spend significant time searching for the right report, metric, or dimension across sprawling BI documentation. This project solves that with a **semantic search system over analytics metadata** — enabling natural language queries like *"what are the key sales performance metrics?"* instead of keyword guessing across Confluence or dashboards.

Rather than querying raw data warehouses, this system indexes **structured analytics metadata** (report descriptions, metric definitions, dimension documentation) as vector embeddings in BigQuery, then retrieves the most relevant entries and synthesizes a natural language answer using Gemini.

---

## Architecture

```
User Query
    ↓
FastAPI  (/ask endpoint)
    ↓
Vertex AI  (text-embedding-004 — embed the query)
    ↓
BigQuery Vector Search  (similarity_search, top-k with optional domain filter)
    ↓
Retrieved Metadata Documents
    ↓
Context Builder  (formats type, title, domain, owner, BI tool, tags)
    ↓
Gemini 1.5 Pro  (RAG prompt → natural language answer)
    ↓
JSON Response  (answer + matched documents + count)
```

---

## Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI 0.109 + Uvicorn |
| RAG Orchestration | LangChain 0.1.5 |
| Vector Store | BigQuery Vector Search (`langchain-google-community`) |
| Embeddings | Vertex AI `text-embedding-004` |
| LLM | Vertex AI Gemini 1.5 Pro |
| GCP SDK | `google-cloud-bigquery`, `google-cloud-aiplatform` |
| Config | `python-dotenv` |
| Language | Python 3.11+ |

---

## Project Structure

```
analytics-metadata-rag-search/
├── app/
│   ├── config.py        # GCP project, model, and search config via .env
│   ├── rag_chain.py     # Core RAG logic — retrieval, context building, LLM call
│   └── main.py          # FastAPI app — /ask and /health endpoints
├── requirements.txt
├── .env.example         # (create this — see Setup below)
├── .gitignore
└── README.md
```

---

## Core Logic — How the RAG Pipeline Works

**`rag_chain.py`** implements three functions that chain together:

**1. `retrieve_metadata(query, domain, top_k)`**
Embeds the user query using Vertex AI and runs `similarity_search` against the BigQuery vector store. Supports optional domain filtering (e.g. `"sales"`, `"finance"`) to scope results.

**2. `build_context(docs)`**
Formats retrieved documents into a structured context block showing `type`, `title`, `domain`, `owner`, `bi_tool`, and `tags` for each match — giving the LLM rich, structured grounding.

**3. `answer_question(query, domain)`**
Chains retrieval and context building, then calls Gemini with a constrained system prompt that instructs it to answer only from the provided metadata. Returns the answer, the matched documents, and the match count.

---

## Setup

### Prerequisites

- Python 3.11+
- GCP project with BigQuery API and Vertex AI API enabled
- Service account with `BigQuery Data Editor` and `Vertex AI User` roles
- `gcloud` CLI configured

### Install

```bash
git clone https://github.com/venkatasaiv/analytics-metadata-rag-search.git
cd analytics-metadata-rag-search
pip install -r requirements.txt
```

### Configure environment

Create a `.env` file in the project root:

```
GCP_PROJECT_ID=your-gcp-project-id
BQ_DATASET=analytics_metadata
BQ_TABLE=metadata_embeddings
BQ_LOCATION=US
EMBED_MODEL=text-embedding-004
LLM_MODEL=gemini-1.5-pro
TOP_K_RESULTS=5
TEMPERATURE=0.1
```

### Authenticate with GCP

```bash
gcloud auth application-default login
```

### Set up BigQuery vector store

Create the dataset and load your analytics metadata with embeddings into BigQuery. The table must have a vector column compatible with BigQuery Vector Search. Refer to the [BigQuery Vector Search documentation](https://cloud.google.com/bigquery/docs/vector-search-intro) for schema requirements.

### Run the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## API

### `POST /ask`

Ask a natural language question over your analytics metadata.

**Request:**
```json
{
  "query": "What are the key metrics for sales performance?",
  "domain": "sales"
}
```

**Response:**
```json
{
  "answer": "The key sales performance metrics include...",
  "matches": [
    {
      "page_content": "Sales Performance Dashboard — tracks revenue, pipeline, and conversion rates...",
      "metadata": {
        "type": "report",
        "title": "Sales Performance Dashboard",
        "domain": "sales",
        "owner": "Analytics Team",
        "bi_tool": "Tableau",
        "tags": "revenue, pipeline, conversion"
      }
    }
  ],
  "num_matches": 5
}
```

**`domain` is optional** — omit it to search across all metadata, or pass a value to filter results to a specific business domain.

### `GET /health`

```json
{ "status": "ok" }
```

---

## Design Decisions

**Why metadata-only, not text-to-SQL?**
Text-to-SQL systems require direct data warehouse access and carry security and governance risks. Searching over metadata is safer, faster, and more appropriate for documentation discovery — the core use case here.

**Why BigQuery Vector Search instead of a dedicated vector DB?**
For teams already on GCP, BigQuery Vector Search eliminates the need to manage a separate Pinecone or Weaviate instance. It scales natively, integrates with existing IAM and data governance, and uses pay-per-query pricing.

**Why RAG instead of fine-tuning?**
The metadata corpus is dynamic — reports and metrics are added and updated constantly. RAG allows the knowledge base to stay current without retraining. Retrieved documents are also fully traceable, which matters for analytics governance.

---

## Future Enhancements

- [ ] Add `scripts/` for generating sample metadata and building embeddings (for local testing without a live GCP project)
- [ ] Hybrid search — combine vector similarity with BM25 keyword scoring
- [ ] Streamlit or React frontend for non-technical users
- [ ] Metadata filtering by BI tool, owner, or tags via query parameters
- [ ] Docker container + Cloud Run deployment configuration
- [ ] Feedback loop for relevance tuning

---

## Author

**Venkatasai Vudatha** — Data Analyst & ML Engineer
📧 Vudatha.sai@gmail.com
🔗 [linkedin.com/in/venkatasaivudatha04](https://www.linkedin.com/in/venkatasaivudatha04/)
📍 Dallas, TX

---

## License

MIT License — see [LICENSE](LICENSE) for details.
