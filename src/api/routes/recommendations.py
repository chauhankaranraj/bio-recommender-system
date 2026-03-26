"""
Unified recommendation & evaluation endpoints.

POST /api/v1/recommend           – batch recommendations
GET  /api/v1/network/{entity}    – network graph for any entity
POST /api/v1/evaluate            – run IR evaluation suite
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

router = APIRouter(tags=["recommendations"])


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class BatchRecommendRequest(BaseModel):
    entities:   List[str] = Field(..., description="List of gene symbols or disease names")
    entity_type: str      = Field("gene", description="'gene' or 'disease'")
    top_k:      int       = Field(10, ge=1, le=50)
    model_name: str       = Field("hybrid_rrf")


class BatchRecommendResponse(BaseModel):
    entity:  str
    results: list


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/recommend", response_model=List[BatchRecommendResponse])
async def batch_recommend(request: Request, body: BatchRecommendRequest):
    """Batch recommendations for multiple genes or diseases."""
    model = _resolve_model(request, body.model_name)

    outputs = []
    for entity in body.entities:
        if body.entity_type == "gene":
            resp = model.recommend_for_gene(entity.strip().upper(), top_k=body.top_k)
        else:
            resp = model.recommend_for_disease(entity.strip().title(), top_k=body.top_k)

        outputs.append({
            "entity":  entity,
            "results": [r.__dict__ for r in resp.results],
        })

    return outputs


@router.get("/network/{entity:path}")
async def get_network(
    request: Request,
    entity:    str,
    depth:     int = Query(2, ge=1, le=3),
    max_nodes: int = Query(80, ge=10, le=200),
):
    """Return D3-compatible bipartite network sub-graph centred on *entity*."""
    model = request.app.state.model
    data  = model.get_network_data(entity.strip(), depth=depth, max_nodes=max_nodes)

    if not data["nodes"]:
        raise HTTPException(status_code=404, detail=f"Entity '{entity}' not found in network.")

    return data


@router.post("/evaluate")
async def evaluate(
    request:    Request,
    k:          int = Query(10, ge=1, le=50),
    n_queries:  int = Query(100, ge=10, le=1000),
    model_name: str = Query("hybrid_rrf"),
):
    """
    Run leave-one-out evaluation and return IR metrics.

    This is compute-intensive – keep n_queries ≤ 200 for interactive use.
    """
    from ...utils.metrics import evaluate_recommender

    model = _resolve_model(request, model_name)
    df    = request.app.state.df

    result = evaluate_recommender(model, df, k=k, n_queries=n_queries)
    return result


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
