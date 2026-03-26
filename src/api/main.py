"""
FastAPI application entry point.

Run with:
    uvicorn src.api.main:app --reload --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..data import load_raw_data, clean_data, save_data, build_interaction_matrix
from ..models import HybridRecommender
from ..data.processor import dataset_stats, load_cleaned
from .routes import genes, diseases, recommendations

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)

# ── Shared application state ─────────────────────────────────────────────────
# FastAPI's lifespan stores fitted objects here so routes can access them
# without a global import.

_state: dict = {}

CSV_PATH = os.getenv("GENE_DISEASE_CSV", "data/gene_disease.csv")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Download data (if needed), fit the hybrid model, expose via app.state."""
    logger.info("=== Biology Recommender API starting up ===")

    # Load / download cleaned data
    if not os.path.exists(CSV_PATH):
        logger.info("Cleaned CSV not found – running data pipeline …")
        raw = load_raw_data()
        df  = clean_data(raw)
        save_data(df, CSV_PATH)
    else:
        df = load_cleaned(CSV_PATH)

    logger.info("Dataset: %d associations", len(df))

    # Fit hybrid recommender (all three sub-models)
    model = HybridRecommender(n_components=min(64, df["gene"].nunique() - 1))
    model.fit(df)

    # Expose objects to all routes via app.state
    app.state.df    = df
    app.state.model = model
    app.state.stats = dataset_stats(df)

    logger.info("=== API ready ===")
    yield

    # Shutdown – nothing to clean up for in-memory models
    logger.info("=== API shutting down ===")


# ── Create app ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Gene–Disease Recommender API",
    description=(
        "A biology recommender system combining TF-IDF content-based "
        "filtering, NMF matrix factorisation, and bipartite Random Walk with "
        "Restart over a curated NCBI ClinVar gene–disease knowledge graph."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS (allow local React dev server) ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register route groups ─────────────────────────────────────────────────────
app.include_router(genes.router,           prefix="/api/v1")
app.include_router(diseases.router,        prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")


# ── Root health check ─────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
async def root():
    return {
        "service": "Gene–Disease Recommender API",
        "version": "1.0.0",
        "status":  "healthy",
        "docs":    "/docs",
    }


@app.get("/api/v1/stats", tags=["stats"])
async def get_stats():
    """Return global dataset statistics (gene count, disease count, top entities)."""
    return app.state.stats


@app.get("/api/v1/search", tags=["search"])
async def search(
    q:         str  = "",
    page_size: int  = 10,
    genes_only: bool = False,
    diseases_only: bool = False,
):
    """
    Unified search across both genes and diseases.

    Returns two lists – `genes` and `diseases` – each filtered by the query
    string (case-insensitive substring match).  Handy for autocomplete.

    Examples
    --------
    /api/v1/search?q=brca          → genes starting with BRCA + diseases containing "Brca"
    /api/v1/search?q=cancer&diseases_only=true
    """
    model    = app.state.model
    q_lower  = q.strip().lower()
    q_upper  = q.strip().upper()

    matched_genes    = []
    matched_diseases = []

    if not diseases_only:
        matched_genes = [g for g in model.genes if q_upper in g or q_lower in g.lower()][:page_size]

    if not genes_only:
        matched_diseases = [d for d in model.diseases if q_lower in d.lower()][:page_size]

    return {
        "query":    q,
        "genes":    matched_genes,
        "diseases": matched_diseases,
    }
