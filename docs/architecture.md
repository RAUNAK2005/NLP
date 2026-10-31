# Architecture

```text
                 USER
                  |
                  v
            React Frontend
                  |
                  v
             FastAPI API
                  |
        +---------+---------+
        v         v         v
     Dataset    NLP       Reports
     Service   Engine      Service
                  |
        +---------+--------------+
        v         v              v
    Statistics Similarity      ML Utility
        |         |              |
        +---------+--------------+
                  v
             Comparison
                  |
                  v
              SQL Database
```

The current local-development default uses SQLite for convenience. The SQLAlchemy models are compatible with PostgreSQL through `DATABASE_URL`, so a later deployment can switch databases without changing application code.

## Backend Modules

- `app/api`: FastAPI route modules for datasets, comparisons, demo execution, and exports.
- `app/db`: SQLAlchemy database configuration and persistence models.
- `app/nlp`: reusable preprocessing, statistics, similarity, and utility-model logic.
- `app/services`: application services that coordinate validation, persistence, comparison, and reporting.

## Frontend Modules

- `src/pages`: routed application screens.
- `src/components`: reusable UI, comparison, and chart components.
- `src/services`: typed API client functions.
- `src/types`: shared frontend response types.

