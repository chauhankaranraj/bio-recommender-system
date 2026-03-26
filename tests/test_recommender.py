"""
Unit tests for all recommender models.
"""

import pandas as pd
import pytest

from src.models import (
    ContentBasedRecommender,
    GraphRecommender,
    HybridRecommender,
    MatrixFactorizationRecommender,
)


@pytest.fixture(scope="module")
def sample_df():
    """Synthetic gene–disease dataset (large enough for NMF k > 1)."""
    genes    = [f"GENE{i}" for i in range(30)]
    diseases = [f"DISEASE{i}" for i in range(20)]
    import random
    random.seed(42)
    rows = []
    for g in genes:
        for d in random.sample(diseases, k=random.randint(2, 6)):
            rows.append({"gene": g, "disease": d})
    return pd.DataFrame(rows).drop_duplicates()


@pytest.fixture(scope="module")
def cb_model(sample_df):
    return ContentBasedRecommender().fit(sample_df)


@pytest.fixture(scope="module")
def mf_model(sample_df):
    return MatrixFactorizationRecommender(n_components=8).fit(sample_df)


@pytest.fixture(scope="module")
def graph_model(sample_df):
    return GraphRecommender().fit(sample_df)


@pytest.fixture(scope="module")
def hybrid_model(sample_df):
    return HybridRecommender(n_components=8).fit(sample_df)


class TestContentBased:
    def test_recommend_for_gene(self, cb_model):
        resp = cb_model.recommend_for_gene("GENE0", top_k=5)
        assert resp.n_results > 0
        assert all(isinstance(r.score, float) for r in resp.results)

    def test_recommend_for_disease(self, cb_model):
        resp = cb_model.recommend_for_disease("DISEASE0", top_k=5)
        assert resp.n_results > 0

    def test_similar_genes(self, cb_model):
        resp = cb_model.similar_genes("GENE0", top_k=5)
        # Self should not appear
        assert "GENE0" not in [r.name for r in resp.results]

    def test_unknown_gene_returns_empty(self, cb_model):
        resp = cb_model.recommend_for_gene("NONEXISTENT_GENE_XYZ", top_k=5)
        assert resp.n_results == 0


class TestMatrixFactorization:
    def test_fit_produces_matrices(self, mf_model):
        assert mf_model._W is not None
        assert mf_model._H is not None

    def test_recommend_for_gene(self, mf_model):
        resp = mf_model.recommend_for_gene("GENE0", top_k=5)
        assert resp.n_results > 0

    def test_similar_genes(self, mf_model):
        resp = mf_model.similar_genes("GENE1", top_k=5)
        assert "GENE1" not in [r.name for r in resp.results]


class TestGraphRecommender:
    def test_graph_built(self, graph_model):
        assert graph_model._graph is not None
        assert graph_model._graph.number_of_nodes() > 0

    def test_recommend_for_gene(self, graph_model):
        resp = graph_model.recommend_for_gene("GENE0", top_k=5)
        assert resp.n_results > 0

    def test_network_data(self, graph_model):
        data = graph_model.get_network_data("GENE0", depth=1, max_nodes=30)
        assert "nodes" in data
        assert "links" in data
        assert len(data["nodes"]) > 0


class TestHybridRecommender:
    def test_recommend_for_gene(self, hybrid_model):
        resp = hybrid_model.recommend_for_gene("GENE0", top_k=10)
        assert resp.n_results > 0
        assert resp.model == "hybrid_rrf"

    def test_recommend_for_disease(self, hybrid_model):
        resp = hybrid_model.recommend_for_disease("DISEASE0", top_k=10)
        assert resp.n_results > 0

    def test_rrf_scores_descending(self, hybrid_model):
        resp = hybrid_model.recommend_for_gene("GENE5", top_k=10)
        scores = [r.score for r in resp.results]
        assert scores == sorted(scores, reverse=True)

    def test_network_data_delegated(self, hybrid_model):
        data = hybrid_model.get_network_data("GENE0")
        assert "nodes" in data
