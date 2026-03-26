"""
Abstract base class for all gene–disease recommender models.

Every concrete model must implement:
    fit(df)          – ingest the cleaned dataframe and build internal structures
    recommend_for_gene(gene, top_k)     – return top-k diseases for a gene
    recommend_for_disease(disease, top_k) – return top-k genes for a disease
    similar_genes(gene, top_k)          – return genes most similar to *gene*
    similar_diseases(disease, top_k)    – return diseases most similar to *disease*
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

import pandas as pd


@dataclass
class RecommendationResult:
    """A single ranked recommendation with a confidence score."""
    name:   str
    score:  float
    reason: str = ""


@dataclass
class RecommendationResponse:
    """Container returned by every recommender method."""
    query:        str
    query_type:   str                          # "gene" | "disease"
    results:      List[RecommendationResult] = field(default_factory=list)
    model:        str = ""
    n_results:    int = 0

    def __post_init__(self) -> None:
        self.n_results = len(self.results)


class BaseRecommender(ABC):
    """Abstract base recommender."""

    name: str = "base"

    def __init__(self) -> None:
        self._fitted: bool = False
        self._genes:    list[str] = []
        self._diseases: list[str] = []

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def fit(self, df: pd.DataFrame) -> "BaseRecommender":
        """Ingest the cleaned gene–disease DataFrame and build all data structures."""

    @abstractmethod
    def recommend_for_gene(
        self, gene: str, top_k: int = 10
    ) -> RecommendationResponse:
        """Return top-*k* disease recommendations for *gene*."""

    @abstractmethod
    def recommend_for_disease(
        self, disease: str, top_k: int = 10
    ) -> RecommendationResponse:
        """Return top-*k* gene recommendations for *disease*."""

    @abstractmethod
    def similar_genes(
        self, gene: str, top_k: int = 10
    ) -> RecommendationResponse:
        """Return genes most similar to *gene* based on shared disease profile."""

    @abstractmethod
    def similar_diseases(
        self, disease: str, top_k: int = 10
    ) -> RecommendationResponse:
        """Return diseases most similar to *disease* based on shared gene profile."""

    # ── Shared utilities ─────────────────────────────────────────────────────

    def _assert_fitted(self) -> None:
        if not self._fitted:
            raise RuntimeError(
                f"Model '{self.name}' has not been fitted yet. Call .fit(df) first."
            )

    def _normalise_gene(self, gene: str) -> str:
        return gene.strip().upper()

    def _normalise_disease(self, disease: str) -> str:
        return disease.strip().title()

    @property
    def genes(self) -> list[str]:
        self._assert_fitted()
        return self._genes

    @property
    def diseases(self) -> list[str]:
        self._assert_fitted()
        return self._diseases
