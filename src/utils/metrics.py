"""
Information-retrieval evaluation metrics for recommender systems.

Metrics implemented
-------------------
* Precision@K   – fraction of top-k results that are relevant.
* Recall@K      – fraction of relevant items found in top-k.
* NDCG@K        – Normalised Discounted Cumulative Gain at cutoff K.
* MRR           – Mean Reciprocal Rank.
* MAP@K         – Mean Average Precision at cutoff K.
* Hit Rate@K    – proportion of queries with ≥1 correct result in top-k.

All functions follow the ``sklearn`` convention: higher is better.
"""

from __future__ import annotations

import logging
import math
from typing import List, Set

import numpy as np
import pandas as pd

from ..models.base_recommender import BaseRecommender

logger = logging.getLogger(__name__)


# ── Per-query metric helpers ─────────────────────────────────────────────────

def precision_at_k(recommended: List[str], relevant: Set[str], k: int) -> float:
    """P@K = |relevant ∩ top-k| / k."""
    top_k = recommended[:k]
    hits  = sum(1 for r in top_k if r in relevant)
    return hits / k if k > 0 else 0.0


def recall_at_k(recommended: List[str], relevant: Set[str], k: int) -> float:
    """Recall@K = |relevant ∩ top-k| / |relevant|."""
    if not relevant:
        return 0.0
    top_k = recommended[:k]
    hits  = sum(1 for r in top_k if r in relevant)
    return hits / len(relevant)


def ndcg_at_k(recommended: List[str], relevant: Set[str], k: int) -> float:
    """
    NDCG@K – binary relevance variant.
    DCG@K = Σ_{i=1}^{k}  rel_i / log2(i+1)
    IDCG@K is computed using as many relevant items as possible up to K.
    """
    gains = [1.0 if r in relevant else 0.0 for r in recommended[:k]]
    dcg   = sum(g / math.log2(i + 2) for i, g in enumerate(gains))

    ideal_gains = sorted(gains, reverse=True)  # binary: already 0/1
    # Fill ideal with up to k relevant items
    n_ideal = min(len(relevant), k)
    idcg    = sum(1.0 / math.log2(i + 2) for i in range(n_ideal))

    return dcg / idcg if idcg > 0 else 0.0


def mean_reciprocal_rank(recommended: List[str], relevant: Set[str]) -> float:
    """MRR = 1 / rank_of_first_relevant_item (0 if not found)."""
    for rank, item in enumerate(recommended, start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0


def average_precision_at_k(
    recommended: List[str], relevant: Set[str], k: int
) -> float:
    """AP@K = mean of P@i for each i where the i-th item is relevant."""
    hits, total = 0, 0
    for i, item in enumerate(recommended[:k], start=1):
        if item in relevant:
            hits  += 1
            total += hits / i
    return total / min(len(relevant), k) if relevant else 0.0


# ── Full evaluation suite ────────────────────────────────────────────────────

def evaluate_recommender(
    model: BaseRecommender,
    df: pd.DataFrame,
    k: int = 10,
    n_queries: int = 200,
    seed: int = 42,
) -> dict:
    """
    Evaluate *model* using leave-one-out cross-validation.

    For each sampled query gene/disease, we hold out ONE known association,
    run the recommender, and measure whether the held-out item appears in
    the top-k results.

    Parameters
    ----------
    model      : A fitted BaseRecommender instance.
    df         : Full cleaned gene–disease DataFrame.
    k          : Cutoff for ranking metrics.
    n_queries  : Number of random queries to evaluate (for speed).
    seed       : Random state for reproducibility.

    Returns
    -------
    dict with keys: precision, recall, ndcg, mrr, map, hit_rate (all @k).
    """
    rng = np.random.default_rng(seed)

    # ── Gene → disease evaluation ────────────────────────────────────────────
    gene_metrics: list[dict] = []
    genes_with_multi = (
        df.groupby("gene")["disease"]
        .filter(lambda x: len(x) >= 2)
        .index
    )
    sampled_idx = rng.choice(
        genes_with_multi.values, size=min(n_queries, len(genes_with_multi)), replace=False
    )
    sampled_pairs = df.loc[sampled_idx]

    for gene, group in sampled_pairs.groupby("gene"):
        hold_out = rng.choice(group["disease"].values)
        relevant = set(df.loc[df["gene"] == gene, "disease"].values) - {hold_out}

        resp  = model.recommend_for_gene(gene, top_k=k)
        recs  = [r.name for r in resp.results]

        gene_metrics.append({
            "precision": precision_at_k(recs, relevant | {hold_out}, k),
            "recall":    recall_at_k(recs, relevant | {hold_out}, k),
            "ndcg":      ndcg_at_k(recs, relevant | {hold_out}, k),
            "mrr":       mean_reciprocal_rank(recs, {hold_out}),
            "map":       average_precision_at_k(recs, {hold_out}, k),
            "hit":       1.0 if hold_out in recs else 0.0,
        })

    def _mean(key: str, metrics: list[dict]) -> float:
        return float(np.mean([m[key] for m in metrics])) if metrics else 0.0

    result = {
        "k": k,
        "n_gene_queries":   len(gene_metrics),
        "gene": {
            "precision_at_k": _mean("precision", gene_metrics),
            "recall_at_k":    _mean("recall",    gene_metrics),
            "ndcg_at_k":      _mean("ndcg",      gene_metrics),
            "mrr":            _mean("mrr",        gene_metrics),
            "map_at_k":       _mean("map",        gene_metrics),
            "hit_rate_at_k":  _mean("hit",        gene_metrics),
        },
    }
    logger.info("[Metrics] Evaluation complete: %s", result["gene"])
    return result
