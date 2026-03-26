"""
Gene endpoints.

GET /api/v1/genes                     – paginated gene list
GET /api/v1/genes/{gene}              – gene detail + known diseases
GET /api/v1/genes/{gene}/similar      – similar genes
GET /api/v1/genes/{gene}/recommend    – recommended diseases for a gene
GET /api/v1/genes/{gene}/network      – network sub-graph for visualisation
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(tags=["genes"])


@router.get("/genes")
async def list_genes(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    search: str = Query("", description="Filter genes by prefix"),
):
    """Return a paginated list of all genes in the dataset."""
    model = request.app.state.model
    genes = model.genes

    if search:
        genes = [g for g in genes if g.upper().startswith(search.upper())]

    total  = len(genes)
    start  = (page - 1) * page_size
    end    = start + page_size
    subset = genes[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": subset,
    }


@router.get("/genes/{gene}")
async def get_gene(request: Request, gene: str):
    """Return gene detail including all associated diseases."""
    df  = request.app.state.df
    gene = gene.strip().upper()

    sub = df[df["gene"] == gene]
    if sub.empty:
        raise HTTPException(status_code=404, detail=f"Gene '{gene}' not found.")

    diseases = sorted(sub["disease"].unique().tolist())
    return {
        "gene":             gene,
        "disease_count":    len(diseases),
        "diseases":         diseases,
    }


@router.get("/genes/{gene}/similar")
async def similar_genes(
    request: Request,
    gene: str,
    top_k: int = Query(10, ge=1, le=50),
    model_name: str = Query("hybrid_rrf", description="hybrid_rrf | content_based | graph_rwr"),
):
    """Return genes most similar to *gene* based on shared disease profiles."""
    m    = _resolve_model(request, model_name)
    gene = gene.strip().upper()
    resp = m.similar_genes(gene, top_k=top_k)

    if not resp.results:
        raise HTTPException(status_code=404, detail=f"Gene '{gene}' not found or no similar genes.")

    return {
        "query":   resp.query,
        "model":   resp.model,
        "results": [r.__dict__ for r in resp.results],
    }


@router.get("/genes/{gene}/recommend")
async def recommend_diseases(
    request: Request,
    gene: str,
    top_k: int = Query(10, ge=1, le=50),
    model_name: str = Query("hybrid_rrf"),
):
    """Return top-k disease recommendations for *gene*."""
    m    = _resolve_model(request, model_name)
    gene = gene.strip().upper()
    resp = m.recommend_for_gene(gene, top_k=top_k)

    if not resp.results:
        raise HTTPException(status_code=404, detail=f"Gene '{gene}' not found or no recommendations.")

    return {
        "query":   resp.query,
        "model":   resp.model,
        "results": [r.__dict__ for r in resp.results],
    }


@router.get("/genes/{gene}/network")
async def gene_network(
    request: Request,
    gene: str,
    depth: int = Query(2, ge=1, le=3),
    max_nodes: int = Query(80, ge=10, le=200),
):
    """Return D3-compatible node-link graph centred on *gene*."""
    model = request.app.state.model
    data  = model.get_network_data(gene.strip().upper(), depth=depth, max_nodes=max_nodes)

    if not data["nodes"]:
        raise HTTPException(status_code=404, detail=f"Gene '{gene}' not found in network.")

    return data


# ── helpers ──────────────────────────────────────────────────────────────────

def _resolve_model(request: Request, model_name: str):
    """Return the appropriate sub-model or the hybrid."""
    hybrid = request.app.state.model
    if model_name == "content_based":
        return hybrid._cb
    if model_name == "matrix_factorization":
        return hybrid._mf
    if model_name == "graph_rwr":
        return hybrid._rwr
    return hybrid
