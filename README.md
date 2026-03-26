# GeneDiseaseAI — Gene–Disease Recommender System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A computational biology recommender system for predicting gene–disease
> associations using TF-IDF content-based filtering, NMF matrix factorisation, and
> bipartite Random Walk with Restart (RWR), fused via Reciprocal Rank Fusion (RRF).

---

## Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Download & clean the gene–disease dataset (NCBI ClinVar, ~5 min)
python main.py --pipeline

# 3. Start the FastAPI backend (port 8000)
python main.py --serve

# 4. In a new terminal – install & start the React frontend
cd frontend
npm install
npm run dev          # opens http://localhost:5173
```

---

## Data Source

| Source | URL | License |
|--------|-----|---------|
| NCBI ClinVar `gene_condition_source_id` | https://ftp.ncbi.nlm.nih.gov/pub/clinvar/gene_condition_source_id | Public domain |
| HPO `genes_to_disease.txt` (fallback) | https://purl.obolibrary.org/obo/hp/hpoa/genes_to_disease.txt | CC BY 4.0 |

Both sources are **freely available** and **require no registration**.

---

## Algorithms

### 1. Content-Based (TF-IDF + Cosine Similarity)
Each gene is represented as a TF-IDF document over its associated disease vocabulary.
Cosine similarity in the L2-normalised embedding space ranks candidates by functional overlap.

### 2. Matrix Factorisation (NMF)
The binary gene × disease interaction matrix **M** ≈ **W·H** is factorised via
Non-negative Matrix Factorisation. Latent factors capture biological pathway themes.

### 3. Graph Random Walk with Restart (RWR)
Personalised PageRank over the bipartite gene–disease knowledge graph:

```
p(t+1) = (1−α)·A_norm·p(t) + α·e_s
```

### 4. Hybrid — Reciprocal Rank Fusion (RRF)
```
RRF_score(d) = Σ_m  1 / (k + rank_m(d)),   k = 60
```

---

## Project Structure

```
biology-recommender/
├── data/
│   ├── raw/              # downloaded raw files (gitignored)
│   └── gene_disease.csv  # cleaned dataset
├── src/
│   ├── data/             # download → parse → clean pipeline
│   ├── models/           # CB, MF, Graph, Hybrid recommenders
│   ├── api/              # FastAPI application
│   └── utils/            # IR evaluation metrics
├── frontend/             # React 18 + Vite + Tailwind + D3.js
├── tests/                # pytest unit tests
├── scripts/              # standalone pipeline runner
├── main.py               # CLI entry point
└── requirements.txt
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/genes` | Paginated gene list |
| GET | `/api/v1/genes/{gene}/recommend` | Disease recommendations for a gene |
| GET | `/api/v1/genes/{gene}/similar` | Genes similar to the query gene |
| GET | `/api/v1/genes/{gene}/network` | Network sub-graph (D3-compatible) |
| GET | `/api/v1/diseases` | Paginated disease list |
| GET | `/api/v1/diseases/{disease}/recommend` | Gene recommendations for a disease |
| GET | `/api/v1/diseases/{disease}/similar` | Similar diseases |
| POST | `/api/v1/recommend` | Batch recommendations |
| GET | `/api/v1/network/{entity}` | Unified network graph |
| POST | `/api/v1/evaluate` | Run IR evaluation suite |
| GET | `/api/v1/stats` | Dataset statistics |

Interactive docs available at **http://localhost:8000/docs**.

---

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| Precision@K | Fraction of top-K results that are relevant |
| Recall@K | Fraction of relevant items found in top-K |
| NDCG@K | Normalised Discounted Cumulative Gain |
| MRR | Mean Reciprocal Rank |
| MAP@K | Mean Average Precision |
| Hit Rate@K | % queries with ≥1 correct result |

Run with:
```bash
python main.py --evaluate
```

---

## Running Tests

```bash
pytest tests/ -v --cov=src
```

---

## References

1. Salton & McGill (1983) *Introduction to Modern Information Retrieval*.
2. Lee & Seung (1999) *Learning the parts of objects by NMF*. Nature 401.
3. Köhler et al. (2008) *Walking the interactome for disease gene prioritization*. AJHG 82.
4. Cormack, Clarke & Buettcher (2009) *Reciprocal rank fusion outperforms Condorcet*. SIGIR.
5. Cheng et al. (2014) *Gene–disease association via gene ontology*. BMC Genomics.

---

## Author

**Shivani Pimparkar** — [@ShivaniPimparkar111](https://github.com/ShivaniPimparkar111)
