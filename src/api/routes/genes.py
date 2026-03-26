"""
Gene endpoints  –  simple, forgiving, well-documented.

All gene lookups are case-insensitive (brca2 == BRCA2).
On 404, the response includes close-match suggestions.

GET /api/v1/genes                     – paginated / searchable gene list
GET /api/v1/genes/{gene}              – gene detail + known diseases
GET /api/v1/genes/{gene}/similar      – genes with similar disease profiles
GET /api/v1/genes/{gene}/recommend    – top disease recommendations
GET /api/v1/genes/{gene}/network      – D3-compatible bipartite sub-graph
"""

from __future__ import annotations

import difflib

from fastapi import APIRouter, HTTPException, Query, Request

router = APIRouter(tags=["genes"])


# ── List ─────────────────────────────────────────────────────────────────────

@router.get("/genes", summary="List all genes")
async def list_genes(
    request: Request,
    page:      int = Query(1,   ge=1,            description="Page number"),
    page_size: int = Query(50,  ge=1,  le=500,   description="Results per page"),
    search:    str = Query("",                   description="Filter by gene symbol prefix"),
):
    """Return a paginated list of gene symbols. Use `search` to filter by prefix."""
    genes = request.app.state.model.genes

    if search:
        s = search.upper()
        genes = [g for g in genes if g.startswith(s)]

    total  = len(genes)
    start  = (page - 1) * page_size
    return {
        "total":     total,
        "page":      page,
        "page_size": page_size,
        "results":   genes[start : start + page_size],
    }


# ── Action routes BEFORE the bare detail route ───────────────────────────────

@router.get("/genes/{gene}/recommend", summary="Disease recommendations for a gene")
async def recommend_diseases(
    request:    Request,
    gene:       str,
    top_k:      int = Query(10, ge=1, le=50,  description="Number of results"),
    model_name: str = Query("hybrid_rrf",     description="hybrid_rrf | content_based | matrix_factorization | graph_rwr"),
):
    """
    Return the top-K diseases most likely associated with **gene**.

    The hybrid model (default) fuses TF-IDF, NMF, and Graph-RWR rankings
    via Reciprocal Rank Fusion for the most robust results.
    """
    model = _resolve_model(request, model_name)
    gene  = _resolve_gene(request, gene)

    resp = model.recommend_for_gene(gene, top_k=top_k)
    if not resp.results:
        raise HTTPException(404, f"No recommendations found for gene '{gene}'.")
    return {"query": resp.query, "model": resp.model,
            "results": [r.__dict__ for r in resp.results]}


@router.get("/genes/{gene}/similar", summary="Genes similar to the query gene")
async def similar_genes(
    request:    Request,
    gene:       str,
    top_k:      int = Query(10, ge=1, le=50),
    model_name: str = Query("hybrid_rrf"),
):
    """Return genes whose disease profile is most similar to **gene**."""
    model = _resolve_model(request, model_name)
    gene  = _resolve_gene(request, gene)

    resp = model.similar_genes(gene, top_k=top_k)
    if not resp.results:
        raise HTTPException(404, f"No similar genes found for '{gene}'.")
    return {"query": resp.query, "model": resp.model,
            "results": [r.__dict__ for r in resp.results]}


@router.get("/genes/{gene}/network", summary="Network sub-graph for a gene")
async def gene_network(
    request:   Request,
    gene:      str,
    depth:     int = Query(2, ge=1, le=3, description="Hop depth from seed node"),
    max_nodes: int = Query(80, ge=10, le=200, description="Cap on returned nodes"),
):
    """
    Return a D3-compatible node-link graph centred on **gene**.
    Nodes have `id`, `type` (gene|disease), `label`, and `degree`.
    """
    gene = _resolve_gene(request, gene)
    data = request.app.state.model.get_network_data(gene, depth=depth, max_nodes=max_nodes)
    if not data["nodes"]:
        raise HTTPException(404, f"Gene '{gene}' not found in network.")
    return data


@router.get("/genes/{gene}", summary="Gene detail")
async def get_gene(request: Request, gene: str):
    """Return a gene's metadata and all known disease associations."""
    gene = _resolve_gene(request, gene)
    df   = request.app.state.df
    sub  = df[df["gene"] == gene]
    return {
        "gene":          gene,
        "disease_count": int(len(sub)),
        "diseases":      sorted(sub["disease"].unique().tolist()),
    }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _resolve_gene(request: Request, raw: str) -> str:
    """
    Normalise to uppercase and validate against the known gene list.
    On mismatch, return a 404 with up to 5 close-match suggestions.
    """
    normalised = raw.strip().upper()
    genes = request.app.state.model.genes
    if normalised in genes:
        return normalised
    suggestions = difflib.get_close_matches(normalised, genes, n=5, cutoff=0.6)
    detail = f"Gene '{normalised}' not found."
    if suggestions:
        detail += f" Did you mean: {', '.join(suggestions)}?"
    raise HTTPException(status_code=404, detail=detail)


def _resolve_model(request: Request, model_name: str):
    hybrid = request.app.state.model
    mapping = {
        "content_based":        hybrid._cb,
        "matrix_factorization": hybrid._mf,
        "graph_rwr":            hybrid._rwr,
    }
    return mapping.get(model_name, hybrid)
