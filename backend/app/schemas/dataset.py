from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DatasetRead(BaseModel):
    id: int
    name: str
    dataset_type: str
    file_name: str
    file_size: int
    row_count: int
    column_count: int
    columns: list[str]
    text_column: str | None
    label_column: str | None
    task_type: str
    sample_rows: list[dict[str, Any]]
    validation_report: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class DatasetStatisticsRead(BaseModel):
    id: int
    dataset_id: int
    missing_count: int
    duplicate_count: int
    unique_text_count: int
    vocabulary_size: int
    avg_text_length: float
    median_text_length: float
    std_text_length: float
    vocabulary_richness: float
    class_distribution: dict[str, Any]
    word_frequency_data: list[dict[str, Any]]
    ngram_statistics: dict[str, Any]
    metrics_payload: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class DatasetWithStatistics(DatasetRead):
    statistics: DatasetStatisticsRead | None = None

