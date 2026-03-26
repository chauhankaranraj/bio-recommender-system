#!/usr/bin/env python
"""
Standalone data-pipeline runner.

Run from project root:
    python scripts/run_pipeline.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)-8s | %(message)s")

from src.data import load_raw_data, clean_data, save_data
from src.data.processor import dataset_stats

def main():
    raw   = load_raw_data(raw_dir="data/raw")
    df    = clean_data(raw)
    save_data(df, "data/gene_disease.csv")
    stats = dataset_stats(df)

    print("\n" + "="*60)
    print("  Gene–Disease Dataset Summary")
    print("="*60)
    print(f"  Total associations : {stats['total_associations']:,}")
    print(f"  Unique genes       : {stats['unique_genes']:,}")
    print(f"  Unique diseases    : {stats['unique_diseases']:,}")
    print(f"  Avg diseases/gene  : {stats['avg_diseases_per_gene']:.2f}")
    print(f"  Avg genes/disease  : {stats['avg_genes_per_disease']:.2f}")
    print("\n  Top 5 genes by disease count:")
    for g, c in list(stats["top_genes"].items())[:5]:
        print(f"    {g:<15} {c} diseases")
    print("\n  Top 5 diseases by gene count:")
    for d, c in list(stats["top_diseases"].items())[:5]:
        print(f"    {d[:45]:<45} {c} genes")
    print("="*60)

if __name__ == "__main__":
    main()
