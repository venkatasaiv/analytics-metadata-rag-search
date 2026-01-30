"""Configuration settings for the analytics metadata RAG search application."""

import os
from dotenv import load_dotenv

load_dotenv()

# GCP Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET = os.getenv("BQ_DATASET", "analytics_metadata")
BQ_TABLE = os.getenv("BQ_TABLE", "metadata_embeddings")
BQ_LOCATION = os.getenv("BQ_LOCATION", "US")

# Model Configuration
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-004")  # Vertex AI embedding model
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-pro")          # Vertex AI LLM

# Search Configuration
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
