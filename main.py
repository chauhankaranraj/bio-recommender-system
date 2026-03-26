"""
Gene–Disease Recommender  –  CLI entry point.

Usage
-----
# 1. Download data, clean it, save to data/gene_disease.csv
python main.py --pipeline

# 2. Start the FastAPI server (default port 8000)
python main.py --serve

# 3. Run evaluation suite
python main.py --evaluate

# 4. Quick demo in the terminal
python main.py --demo --gene BRCA1
python main.py --demo --disease "Breast Cancer"
"""

import argparse
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)


# ── CLI handlers ─────────────────────────────────────────────────────────────

def run_pipeline(csv_path: str = "data/gene_disease.csv") -> None:
    """Download → clean → save gene–disease CSV."""
    from src.data import load_raw_data, clean_data, save_data

    logger.info("Step 1/3  Downloading raw data …")
    raw = load_raw_data()

    logger.info("Step 2/3  Cleaning data …")
    df  = clean_data(raw)

    logger.info("Step 3/3  Saving to %s …", csv_path)
    save_data(df, csv_path)

    from src.data.processor import dataset_stats
    stats = dataset_stats(df)
    logger.info("Dataset ready: %s", stats)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the FastAPI/Uvicorn server."""
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )


def run_evaluation(csv_path: str = "data/gene_disease.csv") -> None:
    """Fit all models and print evaluation metrics."""
    import pandas as pd
    from src.models import HybridRecommender
    from src.utils.metrics import evaluate_recommender

    df    = pd.read_csv(csv_path, dtype=str)
    model = HybridRecommender()
    model.fit(df)

    metrics = evaluate_recommender(model, df, k=10, n_queries=200)
    import json
    print(json.dumps(metrics, indent=2))


def run_demo(gene: str | None, disease: str | None, csv_path: str = "data/gene_disease.csv") -> None:
    """Quick terminal demo of the hybrid recommender."""
    import pandas as pd
    from src.models import HybridRecommender

    if not os.path.exists(csv_path):
        logger.error("CSV not found – run `python main.py --pipeline` first.")
        sys.exit(1)

    df    = pd.read_csv(csv_path, dtype=str)
    model = HybridRecommender()
    model.fit(df)

    if gene:
        resp = model.recommend_for_gene(gene.upper(), top_k=10)
        print(f"\nTop-10 disease recommendations for gene {gene.upper()}:")
        for i, r in enumerate(resp.results, 1):
            print(f"  {i:2}. {r.name:<50} score={r.score:.4f}")

    if disease:
        resp = model.recommend_for_disease(disease.title(), top_k=10)
        print(f"\nTop-10 gene recommendations for disease '{disease.title()}':")
        for i, r in enumerate(resp.results, 1):
            print(f"  {i:2}. {r.name:<20} score={r.score:.4f}")


# ── Argument parsing ─────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gene–Disease Recommender System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--pipeline",  action="store_true", help="Run data pipeline")
    parser.add_argument("--serve",     action="store_true", help="Start FastAPI server")
    parser.add_argument("--evaluate",  action="store_true", help="Run evaluation metrics")
    parser.add_argument("--demo",      action="store_true", help="Run terminal demo")
    parser.add_argument("--gene",      type=str, default=None)
    parser.add_argument("--disease",   type=str, default=None)
    parser.add_argument("--host",      type=str, default="0.0.0.0")
    parser.add_argument("--port",      type=int, default=8000)
    parser.add_argument("--csv",       type=str, default="data/gene_disease.csv")

    args = parser.parse_args()

    if args.pipeline:
        run_pipeline(args.csv)
    elif args.serve:
        run_server(args.host, args.port)
    elif args.evaluate:
        run_evaluation(args.csv)
    elif args.demo:
        run_demo(args.gene, args.disease, args.csv)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
