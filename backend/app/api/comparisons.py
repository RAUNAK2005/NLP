from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, selectinload

from app.db.database import get_db
from app.db.models import Comparison, Dataset
from app.schemas.comparison import ComparisonCreate, ComparisonRead
from app.schemas.dataset import DatasetWithStatistics
from app.services.comparison_service import create_comparison, get_comparison

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@router.post("", response_model=ComparisonRead, status_code=201)
def compare_datasets(payload: ComparisonCreate, db: Session = Depends(get_db)):
    return create_comparison(
        db,
        payload.original_dataset_id,
        payload.synthetic_dataset_id,
        payload.scoring_weights,
    )


@router.get("", response_model=list[ComparisonRead])
def list_comparisons(db: Session = Depends(get_db)):
    return db.query(Comparison).options(selectinload(Comparison.metrics)).order_by(Comparison.created_at.desc()).all()


@router.get("/{comparison_id}", response_model=ComparisonRead)
def read_comparison(comparison_id: int, db: Session = Depends(get_db)):
    return get_comparison(db, comparison_id)


@router.get("/{comparison_id}/detail")
def read_comparison_detail(comparison_id: int, db: Session = Depends(get_db)):
    comparison = get_comparison(db, comparison_id)
    original = (
        db.query(Dataset)
        .options(selectinload(Dataset.statistics))
        .filter(Dataset.id == comparison.original_dataset_id)
        .first()
    )
    synthetic = (
        db.query(Dataset)
        .options(selectinload(Dataset.statistics))
        .filter(Dataset.id == comparison.synthetic_dataset_id)
        .first()
    )
    return jsonable_encoder(
        {
            "comparison": ComparisonRead.model_validate(comparison),
            "original_dataset": DatasetWithStatistics.model_validate(original),
            "synthetic_dataset": DatasetWithStatistics.model_validate(synthetic),
        }
    )

