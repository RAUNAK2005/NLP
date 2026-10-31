from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import comparisons, datasets, demo, reports
from app.core.config import get_settings
from app.db.database import Base, engine

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Research-oriented platform for comparing original and synthetic NLP classification datasets.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "environment": settings.environment}


app.include_router(datasets.router, prefix="/api")
app.include_router(comparisons.router, prefix="/api")
app.include_router(demo.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
