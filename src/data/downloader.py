"""
Gene-disease dataset downloader.

Primary source
--------------
NCBI ClinVar ``gene_condition_source_id`` (tab-separated, no registration needed).
URL: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/gene_condition_source_id

Columns of interest
-------------------
  #GeneID | GeneSymbol | ConceptID | DiseaseName | SourceName | SourceID |
  DiseaseMIM | LastEvaluated

Fallback source (used automatically if primary fails)
------------------------------------------------------
Human Phenotype Ontology (HPO) ``genes_to_disease.txt``
URL: https://purl.obolibrary.org/obo/hp/hpoa/genes_to_disease.txt
Columns: ncbi_gene_id | gene_symbol | disease_id | disease_name
"""

import gzip
import logging
import os
import shutil
import urllib.request
from pathlib import Path
from typing import Optional

import pandas as pd
from tqdm import tqdm

logger = logging.getLogger(__name__)

# ── Public dataset URLs (no authentication required) ────────────────────────

NCBI_CLINVAR_URL = (
    "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/gene_condition_source_id"
)
HPO_GENES_URL = (
    "https://purl.obolibrary.org/obo/hp/hpoa/genes_to_disease.txt"
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; GeneDiseaseRecommender/1.0; "
        "+https://github.com/ShivaniPimparkar111/biology-recommender)"
    )
}


# ── Low-level helpers ────────────────────────────────────────────────────────

class _TqdmUpTo(tqdm):
    """Provides ``update_to`` hook for urlretrieve progress."""

    def update_to(self, b: int = 1, bsize: int = 1, tsize: Optional[int] = None) -> None:
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def _http_get(url: str, dest: str) -> str:
    """Download *url* to *dest*, showing a progress bar."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers=_HEADERS)

    logger.info("GET %s → %s", url, dest)
    with _TqdmUpTo(unit="B", unit_scale=True, miniters=1, desc=Path(dest).name) as t:
        urllib.request.urlretrieve(url, dest, reporthook=t.update_to)  # noqa: S310

    return dest


def _decompress_gz(gz_path: str) -> str:
    """Decompress a .gz file in-place; returns path without the .gz suffix."""
    out_path = gz_path[:-3]
    logger.info("Decompressing %s → %s", gz_path, out_path)
    with gzip.open(gz_path, "rb") as f_in, open(out_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    return out_path


# ── Main public function ─────────────────────────────────────────────────────

def load_raw_data(raw_dir: str = "data/raw") -> pd.DataFrame:
    """
    Download (if necessary) and parse the gene–disease raw dataset.

    Tries NCBI ClinVar first; falls back to HPO on any failure.

    Parameters
    ----------
    raw_dir : str
        Directory where downloaded files are cached.

    Returns
    -------
    pd.DataFrame
        Raw dataframe with at minimum the columns ``gene`` and ``disease``.
    """
    os.makedirs(raw_dir, exist_ok=True)

    # ── Try NCBI ClinVar ─────────────────────────────────────────────────────
    ncbi_path = os.path.join(raw_dir, "gene_condition_source_id.txt")
    try:
        if not os.path.exists(ncbi_path):
            _http_get(NCBI_CLINVAR_URL, ncbi_path)
        df = _parse_ncbi_clinvar(ncbi_path)
        logger.info("Loaded NCBI ClinVar: %d raw rows", len(df))
        return df
    except Exception as exc:  # noqa: BLE001
        logger.warning("NCBI ClinVar download/parse failed (%s). Falling back to HPO.", exc)

    # ── Fallback: HPO ────────────────────────────────────────────────────────
    hpo_path = os.path.join(raw_dir, "genes_to_disease.txt")
    if not os.path.exists(hpo_path):
        _http_get(HPO_GENES_URL, hpo_path)
    df = _parse_hpo(hpo_path)
    logger.info("Loaded HPO genes_to_disease: %d raw rows", len(df))
    return df


# ── Format-specific parsers ──────────────────────────────────────────────────

def _parse_ncbi_clinvar(path: str) -> pd.DataFrame:
    """
    Parse NCBI ClinVar ``gene_condition_source_id``.

    Expected columns (tab-separated, first line is a commented header):
        #GeneID  GeneSymbol  ConceptID  DiseaseName  SourceName
        SourceID  DiseaseMIM  LastEvaluated
    """
    df = pd.read_csv(
        path,
        sep="\t",
        comment="#",
        header=None,
        names=[
            "gene_id", "gene", "concept_id", "disease",
            "source_name", "source_id", "disease_mim", "last_evaluated",
        ],
        dtype=str,
        low_memory=False,
    )
    return df[["gene", "disease"]].copy()


def _parse_hpo(path: str) -> pd.DataFrame:
    """
    Parse HPO ``genes_to_disease.txt``.

    Expected columns (tab-separated):
        ncbi_gene_id  gene_symbol  disease_id  disease_name
    Lines beginning with '#' are comments.
    """
    df = pd.read_csv(
        path,
        sep="\t",
        comment="#",
        header=None,
        names=["gene_id", "gene", "disease_id", "disease"],
        dtype=str,
        low_memory=False,
    )
    return df[["gene", "disease"]].copy()
