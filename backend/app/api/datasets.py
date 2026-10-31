from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session, selectinload

from app.db.database import get_db
from app.db.models import Dataset
from app.schemas.dataset import DatasetWithStatistics
from app.services.dataset_service import create_dataset_from_upload

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetWithStatistics, status_code=201)
async def upload_dataset(
    dataset_type: str = Form(...),
    task_type: str = Form("sentiment_classification"),
    text_column: str | None = Form(None),
    label_column: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await create_dataset_from_upload(db, file, dataset_type, task_type, text_column, label_column)


@router.get("", response_model=list[DatasetWithStatistics])
def list_datasets(db: Session = Depends(get_db)):
    return db.query(Dataset).options(selectinload(Dataset.statistics)).order_by(Dataset.created_at.desc()).all()


@router.get("/{dataset_id}", response_model=DatasetWithStatistics)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).options(selectinload(Dataset.statistics)).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found.")
    return dataset
