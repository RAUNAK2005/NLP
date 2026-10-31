import re
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Dataset, DatasetStatistics
from app.nlp.statistics import calculate_dataset_statistics

TEXT_HINTS = ("text", "review", "sentence", "content", "message", "comment", "tweet", "body")
LABEL_HINTS = ("label", "sentiment", "class", "category", "target", "polarity", "rating")
SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def sanitize_filename(filename: str) -> str:
    cleaned = SAFE_FILENAME_RE.sub("_", Path(filename).name)
    return cleaned[:180] or "dataset.csv"


def detect_columns(df: pd.DataFrame) -> tuple[str | None, str | None]:
    lower_map = {str(column).lower(): str(column) for column in df.columns}
    text_column = next((lower_map[name] for name in lower_map if any(hint in name for hint in TEXT_HINTS)), None)
    label_column = next((lower_map[name] for name in lower_map if any(hint in name for hint in LABEL_HINTS)), None)
    if text_column is None:
        object_columns = [column for column in df.columns if df[column].dtype == object]
        if object_columns:
            text_column = max(object_columns, key=lambda column: df[column].astype(str).str.len().mean())
    if label_column is None:
        candidates = [
            column
            for column in df.columns
            if column != text_column and df[column].nunique(dropna=True) <= max(20, int(len(df) * 0.2))
        ]
        if candidates:
            label_column = str(candidates[0])
    return text_column, label_column


def validation_report(df: pd.DataFrame, text_column: str | None, label_column: str | None) -> dict[str, Any]:
    warnings: list[str] = []
    checks = [
        {"label": "CSV format valid", "status": "passed"},
        {"label": f"{len(df):,} records found", "status": "passed" if len(df) else "failed"},
        {"label": "Text column detected", "status": "passed" if text_column else "warning"},
        {"label": "Label column detected", "status": "passed" if label_column else "warning"},
    ]
    if text_column:
        missing_text = int(df[text_column].isna().sum() + (df[text_column].astype(str).str.strip() == "").sum())
        duplicate_text = int(df[text_column].astype(str).duplicated().sum())
        long_text = int((df[text_column].astype(str).str.len() > 5000).sum())
        if missing_text:
            warnings.append(f"{missing_text} missing or empty text values")
        if duplicate_text:
            warnings.append(f"{duplicate_text} duplicate text records")
        if long_text:
            warnings.append(f"{long_text} very long text records")
    if label_column:
        missing_label = int(df[label_column].isna().sum() + (df[label_column].astype(str).str.strip() == "").sum())
        if missing_label:
            warnings.append(f"{missing_label} missing labels")
    return {"checks": checks, "warnings": warnings, "blocking_errors": []}


def read_csv_bytes(content: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(BytesIO(content), encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only UTF-8 CSV files are supported.") from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is not a valid CSV.") from exc


def persist_dataframe(
    db: Session,
    df: pd.DataFrame,
    *,
    name: str,
    dataset_type: str,
    file_name: str,
    file_size: int,
    task_type: str,
    text_column: str | None = None,
    label_column: str | None = None,
) -> Dataset:
    settings = get_settings()
    if len(df) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dataset is empty.")
    if len(df) > settings.max_rows:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"Dataset exceeds {settings.max_rows:,} rows.")

    inferred_text_column, inferred_label_column = detect_columns(df)
    text_column = text_column or inferred_text_column
    label_column = label_column or inferred_label_column
    if not text_column or text_column not in df.columns:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A text column could not be identified.")
    if not label_column or label_column not in df.columns:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A label column could not be identified.")

    df = df.where(pd.notnull(df), None)
    report = validation_report(df, text_column, label_column)
    stats_payload = calculate_dataset_statistics(df, text_column, label_column)
    records = df.to_dict(orient="records")
    dataset = Dataset(
        name=name,
        dataset_type=dataset_type,
        file_name=file_name,
        file_size=file_size,
        row_count=len(df),
        column_count=len(df.columns),
        columns=[str(column) for column in df.columns],
        text_column=text_column,
        label_column=label_column,
        task_type=task_type,
        sample_rows=records[:10],
        validation_report=report,
        raw_records=records,
    )
    db.add(dataset)
    db.flush()
    stats = DatasetStatistics(
        dataset_id=dataset.id,
        missing_count=stats_payload["missing_text_count"] + stats_payload["missing_label_count"],
        duplicate_count=stats_payload["duplicate_count"],
        unique_text_count=stats_payload["unique_text_count"],
        vocabulary_size=stats_payload["vocabulary_size"],
        avg_text_length=stats_payload["text_length"]["mean"],
        median_text_length=stats_payload["text_length"]["median"],
        std_text_length=stats_payload["text_length"]["std"],
        vocabulary_richness=stats_payload["type_token_ratio"],
        class_distribution=stats_payload["class_distribution"],
        word_frequency_data=stats_payload["word_frequency"],
        ngram_statistics=stats_payload["ngram_statistics"],
        metrics_payload=stats_payload,
    )
    db.add(stats)
    db.commit()
    db.refresh(dataset)
    return dataset


async def create_dataset_from_upload(
    db: Session,
    upload: UploadFile,
    dataset_type: str,
    task_type: str,
    text_column: str | None,
    label_column: str | None,
) -> Dataset:
    settings = get_settings()
    filename = sanitize_filename(upload.filename or "dataset.csv")
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV uploads are supported.")
    content = await upload.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File exceeds {settings.max_file_size_mb} MB.")
    df = read_csv_bytes(content)
    return persist_dataframe(
        db,
        df,
        name=Path(filename).stem.replace("_", " ").title(),
        dataset_type=dataset_type,
        file_name=filename,
        file_size=len(content),
        task_type=task_type,
        text_column=text_column,
        label_column=label_column,
    )


def load_sample_dataset(db: Session, path: Path, dataset_type: str) -> Dataset:
    content = path.read_bytes()
    df = read_csv_bytes(content)
    return persist_dataframe(
        db,
        df,
        name=f"Demo {dataset_type.title()} Sentiment",
        dataset_type=dataset_type,
        file_name=path.name,
        file_size=len(content),
        task_type="sentiment_classification",
    )

