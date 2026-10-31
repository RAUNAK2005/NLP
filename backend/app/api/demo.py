from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.comparison_service import create_comparison
from app.services.dataset_service import load_sample_dataset

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/run", status_code=201)
def run_demo(db: Session = Depends(get_db)):
    root = Path(__file__).resolve().parents[3]
    sample_root = root / "sample_data"
    if not sample_root.exists():
        sample_root = Path.cwd() / "sample_data"
    original = load_sample_dataset(db, sample_root / "original_sentiment.csv", "original")
    synthetic = load_sample_dataset(db, sample_root / "synthetic_sentiment.csv", "synthetic")
    return create_comparison(db, original.id, synthetic.id)

