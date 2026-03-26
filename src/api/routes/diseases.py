"""
Disease endpoints.

GET /api/v1/diseases                         – paginated disease list
GET /api/v1/diseases/{disease}               – disease detail + associated genes
GET /api/v1/diseases/{disease}/similar       – similar diseases
GET /api/v1/diseases/{disease}/recommend     – recommended genes for a disease
GET /api/v1/diseases/{disease}/network       – network sub-graph
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(tags=["diseases"])


@router.get("/diseases")
async def list_diseases(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    search: str = Query("", description="Filter diseases by substring"),
):
    """Return a paginated list of all diseases in the dataset."""
    model    = request.app.state.model
    diseases = model.diseases

    if search:
        diseases = [d for d in diseases if search.lower() in d.lower()]

    total  = len(diseases)
    start  = (page - 1) * page_size
    end    = start + page_size
    subset = diseases[start:end]

    return {
        "total":     total,
        "page":      page,
        "page_size": page_size,
        "results":   subset,
    }


@router.get("/diseases/{disease:path}")
async def get_disease(request: Request, disease: str):
    """Return disease detail including all associated genes."""
    df      = request.app.state.df
    disease = disease.strip().title()

    sub = df[df["disease"] == disease]
    if sub.empty:
        raise HTTPException(status_code=404, detail=f"Disease '{disease}' not found.")

    genes = sorted(sub["gene"].unique().tolist())
    return {
        "disease":   disease,
        "gene_count": len(genes),
        "genes":     genes,
    }


@router.get("/diseases/{disease:path}/similar")
async def similar_diseases(
    request: Request,
    disease: str,
    top_k: int = Query(10, ge=1, le=50),
    model_name: str = Query("hybrid_rrf"),
):
    """Return diseases most similar to *disease* based on shared gene profiles."""
    m       = _resolve_model(request, model_name)
    disease = disease.strip().title()
    resp    = m.similar_diseases(disease, top_k=top_k)

    if not resp.results:
        raise HTTPException(
            status_code=404,
            detail=f"Disease '{disease}' not found or no similar diseases.",
        )

    return {
        "query":   resp.query,
        "model":   resp.model,
        "results": [r.__dict__ for r in resp.results],
    }


@router.get("/diseases/{disease:path}/recommend")
async def recommend_genes(
    request: Request,
    disease: str,
    top_k: int = Query(10, ge=1, le=50),
    model_name: str = Query("hybrid_rrf"),
):
    """Return top-k gene recommendations for *disease*."""
    m       = _resolve_model(request, model_name)
    disease = disease.strip().title()
    resp    = m.recommend_for_disease(disease, top_k=top_k)

    if not resp.results:
        raise HTTPException(
            status_code=404,
            detail=f"Disease '{disease}' not found or no recommendations.",
        )

    return {
        "query":   resp.query,
        "model":   resp.model,
        "results": [r.__dict__ for r in resp.results],
    }


@router.get("/diseases/{disease:path}/network")
async def disease_network(
    request: Request,
    disease: str,
    depth:     int = Query(2, ge=1, le=3),
    max_nodes: int = Query(80, ge=10, le=200),
):
    """Return D3-compatible node-link graph centred on *disease*."""
    model   = request.app.state.model
    disease = disease.strip().title()
    data    = model.get_network_data(disease, depth=depth, max_nodes=max_nodes)

    if not data["nodes"]:
        raise HTTPException(
            status_code=404, detail=f"Disease '{disease}' not found in network."
        )

    return data


# ── helpers ──────────────────────────────────────────────────────────────────

def _resolve_model(request: Request, model_name: str):
    hybrid = request.app.state.model
    if model_name == "content_based":
        return hybrid._cb
    if model_name == "matrix_factorization":
        return hybrid._mf
    if model_name == "graph_rwr":
        return hybrid._rwr
    return hybrid
