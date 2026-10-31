from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.dataset import DatasetWithStatistics


class ComparisonCreate(BaseModel):
    original_dataset_id: int
    synthetic_dataset_id: int
    scoring_weights: dict[str, float] | None = None


class ComparisonMetricRead(BaseModel):
    metric_name: str
    original_value: float | None
    synthetic_value: float | None
    absolute_difference: float | None
    relative_difference: float | None
    similarity_score: float | None
    interpretation: str
    category: str
    direction: str

    model_config = {"from_attributes": True}


class ComparisonRead(BaseModel):
    id: int
    original_dataset_id: int
    synthetic_dataset_id: int
    overall_score: float
    fidelity_score: float
    diversity_score: float
    utility_score: float
    status: str
    interpretation: str
    configuration: dict[str, Any]
    payload: dict[str, Any]
    created_at: datetime
    metrics: list[ComparisonMetricRead]

    model_config = {"from_attributes": True}


class ComparisonDetail(ComparisonRead):
    original_dataset: DatasetWithStatistics
    synthetic_dataset: DatasetWithStatistics

