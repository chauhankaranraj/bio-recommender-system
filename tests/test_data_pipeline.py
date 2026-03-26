"""
Unit tests for the data acquisition and cleaning pipeline.
Run with: pytest tests/ -v
"""

import pandas as pd
import pytest

from src.data.cleaner import clean_data
from src.data.processor import build_interaction_matrix, dataset_stats, save_data


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def raw_df():
    """Minimal raw dataframe with intentional noise."""
    return pd.DataFrame({
        "gene": [
            "BRCA1", "BRCA2", "TP53", " tp53 ", "BRCA1",
            "UNKNOWN", "not provided", "ATM", "PTEN", "BRCA1",
        ],
        "disease": [
            "Breast Cancer", "Ovarian Cancer", "Li-Fraumeni Syndrome",
            "Li-Fraumeni Syndrome", "Breast Cancer",  # dup
            "some disease", "other", "Ataxia-Telangiectasia",
            "Cowden Syndrome", "Ovarian Cancer",
        ],
    })


@pytest.fixture
def clean_df(raw_df):
    return clean_data(raw_df)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestCleanData:
    def test_columns_renamed(self, clean_df):
        assert set(clean_df.columns) == {"gene", "disease"}

    def test_no_nulls(self, clean_df):
        assert clean_df.isnull().sum().sum() == 0

    def test_no_duplicates(self, clean_df):
        assert not clean_df.duplicated().any()

    def test_gene_uppercased(self, clean_df):
        assert all(g == g.upper() for g in clean_df["gene"])

    def test_junk_removed(self, clean_df):
        junk = {"NOT PROVIDED", "OTHER", "NOT SPECIFIED", "UNKNOWN"}
        assert not any(g in junk for g in clean_df["gene"])

    def test_whitespace_stripped(self, clean_df):
        assert not any(g.startswith(" ") or g.endswith(" ") for g in clean_df["gene"])


class TestInteractionMatrix:
    def test_shape(self, clean_df):
        mat, genes, diseases = build_interaction_matrix(clean_df)
        assert mat.shape == (len(genes), len(diseases))

    def test_binary(self, clean_df):
        mat, _, _ = build_interaction_matrix(clean_df)
        import numpy as np
        assert set(mat.data.tolist()).issubset({0.0, 1.0})

    def test_nonzero_count(self, clean_df):
        mat, _, _ = build_interaction_matrix(clean_df)
        assert mat.nnz == len(clean_df)


class TestDatasetStats:
    def test_keys_present(self, clean_df):
        stats = dataset_stats(clean_df)
        for key in ("total_associations", "unique_genes", "unique_diseases",
                    "avg_diseases_per_gene", "avg_genes_per_disease",
                    "top_genes", "top_diseases"):
            assert key in stats

    def test_counts_positive(self, clean_df):
        stats = dataset_stats(clean_df)
        assert stats["unique_genes"] > 0
        assert stats["unique_diseases"] > 0


class TestSaveData:
    def test_roundtrip(self, clean_df, tmp_path):
        path = str(tmp_path / "test.csv")
        save_data(clean_df, path)
        loaded = pd.read_csv(path, dtype=str)
        assert list(loaded.columns) == ["gene", "disease"]
        assert len(loaded) == len(clean_df)
