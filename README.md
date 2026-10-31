# Synthetic Dataset Evaluation Framework for NLP

A full-stack research dashboard for evaluating whether a synthetic NLP text-classification dataset preserves the properties of an original dataset.

## Problem Statement

Synthetic text datasets are useful only if they preserve the original dataset's linguistic patterns, label distributions, diversity, and downstream machine-learning utility. This project compares an original dataset and a synthetic dataset using reproducible metrics instead of fabricated demo scores.

## Features

- CSV upload for original and synthetic datasets
- Automatic text and label column detection
- Dataset validation with warnings for missing values, duplicates, and long text
- NLP statistics: record counts, text length, vocabulary, TTR, word frequency, n-grams, class distribution
- Similarity metrics: vocabulary Jaccard, n-gram overlap, TF-IDF centroid cosine, semantic similarity fallback, Jensen-Shannon class similarity
- Utility experiment: Real->Real baseline and Synthetic->Real evaluation on the same original holdout test set
- Project-defined composite score across fidelity, diversity, and utility
- Interactive React dashboard with charts and metric explanations
- Experiment history
- JSON, CSV, and PDF exports
- Demo mode using `sample_data/original_sentiment.csv` and `sample_data/synthetic_sentiment.csv`

## Tech Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Recharts, Lucide icons
- Backend: FastAPI, Pydantic, SQLAlchemy, pandas, NumPy, SciPy, scikit-learn, ReportLab
- Database: SQLite by default for local development; PostgreSQL-compatible via `DATABASE_URL`

## Local Setup

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Environment Variables

Copy `.env.example` to `.env` and adjust values if needed. For local SQLite development, omit `DATABASE_URL` or set:

```text
DATABASE_URL=sqlite:///./nlp_eval.db
```

## API

FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

Core endpoints:

- `POST /api/datasets/upload`
- `GET /api/datasets`
- `POST /api/comparisons`
- `GET /api/comparisons/{id}/detail`
- `POST /api/demo/run`
- `GET /api/reports/comparisons/{id}.json`
- `GET /api/reports/comparisons/{id}.csv`
- `GET /api/reports/comparisons/{id}.pdf`

## Research Methodology

The main downstream utility experiment is:

```text
Original train -> classifier -> original test
Synthetic train -> classifier -> same original test
```

The original test split is not used for training the synthetic model. The random seed, model family, vectorizer configuration, sample size, embedding model, and scoring weights are stored in the comparison configuration.

## Limitations

The composite score is project-defined and transparent, not a universal scientific standard. High similarity can indicate fidelity, but excessive similarity may also indicate memorization or insufficient novelty. Interpret fidelity together with diversity and utility.

## Tests

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
```

## Future Scope

- Authenticated users and shared experiment workspaces
- PostgreSQL migrations with Alembic
- Background job queue for large datasets
- User-editable scoring weights in the UI
- Optional near-duplicate privacy analysis
- More NLP task types beyond text classification

