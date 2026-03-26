"""
Post-cleaning processing utilities.

Responsibilities
----------------
* Persist the cleaned CSV to disk.
* Build the binary gene × disease interaction matrix used by all models.
* Provide summary statistics about the curated dataset.
"""

import logging
import os
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

logger = logging.getLogger(__name__)


# ── I/O helpers ─────────────────────────────────────────────────────────────

def save_data(df: pd.DataFrame, path: str = "data/gene_disease.csv") -> None:
    """
    Save cleaned DataFrame to *path* (creates parent directories as needed).

    Parameters
    ----------
    df   : Cleaned DataFrame with columns [gene, disease].
    path : Destination CSV path.
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Saved %d rows → %s", len(df), path)


def load_cleaned(path: str = "data/gene_disease.csv") -> pd.DataFrame:
    """Load the pre-cleaned CSV from disk."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Cleaned dataset not found at '{path}'. "
            "Run the pipeline first: python main.py --pipeline"
        )
    return pd.read_csv(path, dtype=str)


# ── Feature engineering ──────────────────────────────────────────────────────

def build_interaction_matrix(
    df: pd.DataFrame,
) -> Tuple[csr_matrix, list[str], list[str]]:
    """
    Build a binary gene × disease interaction (co-occurrence) matrix.

    Returns
    -------
    matrix   : scipy CSR matrix of shape (n_genes, n_diseases)
    genes    : sorted list of gene symbols (row index)
    diseases : sorted list of disease names (col index)
    """
    genes    = sorted(df["gene"].unique())
    diseases = sorted(df["disease"].unique())

    gene_idx    = {g: i for i, g in enumerate(genes)}
    disease_idx = {d: i for i, d in enumerate(diseases)}

    rows = df["gene"].map(gene_idx).values
    cols = df["disease"].map(disease_idx).values
    data = np.ones(len(df), dtype=np.float32)

    matrix = csr_matrix(
        (data, (rows, cols)),
        shape=(len(genes), len(diseases)),
    )
    logger.info(
        "Interaction matrix: %d genes × %d diseases  (density=%.4f%%)",
        len(genes), len(diseases),
        100 * matrix.nnz / (len(genes) * len(diseases)),
    )
    return matrix, genes, diseases


def dataset_stats(df: pd.DataFrame) -> dict:
    """Return a summary dictionary of the curated dataset."""
    return {
        "total_associations": int(len(df)),
        "unique_genes":       int(df["gene"].nunique()),
        "unique_diseases":    int(df["disease"].nunique()),
        "avg_diseases_per_gene": float(
            df.groupby("gene")["disease"].nunique().mean()
        ),
        "avg_genes_per_disease": float(
            df.groupby("disease")["gene"].nunique().mean()
        ),
        "top_genes": (
            df.groupby("gene")["disease"]
            .nunique()
            .nlargest(10)
            .to_dict()
        ),
        "top_diseases": (
            df.groupby("disease")["gene"]
            .nunique()
            .nlargest(10)
            .to_dict()
        ),
    }
