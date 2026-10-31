from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.database import Base


JsonType = JSON().with_variant(JSONB, "postgresql")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)


class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_type: Mapped[str] = mapped_column(String(32), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    column_count: Mapped[int] = mapped_column(Integer, nullable=False)
    columns: Mapped[list[str]] = mapped_column(JsonType, default=list, nullable=False)
    text_column: Mapped[str | None] = mapped_column(String(255), nullable=True)
    label_column: Mapped[str | None] = mapped_column(String(255), nullable=True)
    task_type: Mapped[str] = mapped_column(String(64), default="sentiment_classification", nullable=False)
    sample_rows: Mapped[list[dict]] = mapped_column(JsonType, default=list, nullable=False)
    validation_report: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)
    raw_records: Mapped[list[dict]] = mapped_column(JsonType, default=list, nullable=False)

    statistics: Mapped["DatasetStatistics"] = relationship(
        back_populates="dataset", cascade="all, delete-orphan", uselist=False
    )
    evaluation_runs: Mapped[list["EvaluationRun"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")


class DatasetStatistics(Base, TimestampMixin):
    __tablename__ = "dataset_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, unique=True)
    missing_count: Mapped[int] = mapped_column(Integer, nullable=False)
    duplicate_count: Mapped[int] = mapped_column(Integer, nullable=False)
    unique_text_count: Mapped[int] = mapped_column(Integer, nullable=False)
    vocabulary_size: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_text_length: Mapped[float] = mapped_column(Float, nullable=False)
    median_text_length: Mapped[float] = mapped_column(Float, nullable=False)
    std_text_length: Mapped[float] = mapped_column(Float, nullable=False)
    vocabulary_richness: Mapped[float] = mapped_column(Float, nullable=False)
    class_distribution: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)
    word_frequency_data: Mapped[list[dict]] = mapped_column(JsonType, default=list, nullable=False)
    ngram_statistics: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)
    metrics_payload: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="statistics")


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    run_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="completed", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    config: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="evaluation_runs")
    metrics: Mapped[list["EvaluationMetric"]] = relationship(back_populates="evaluation_run", cascade="all, delete-orphan")


class EvaluationMetric(Base):
    __tablename__ = "evaluation_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    evaluation_run_id: Mapped[int] = mapped_column(ForeignKey("evaluation_runs.id"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    metric_category: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_metadata: Mapped[dict] = mapped_column("metadata", JsonType, default=dict, nullable=False)

    evaluation_run: Mapped[EvaluationRun] = relationship(back_populates="metrics")


class Comparison(Base, TimestampMixin):
    __tablename__ = "comparisons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    original_dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    synthetic_dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    original_run_id: Mapped[int | None] = mapped_column(ForeignKey("evaluation_runs.id"), nullable=True)
    synthetic_run_id: Mapped[int | None] = mapped_column(ForeignKey("evaluation_runs.id"), nullable=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    fidelity_score: Mapped[float] = mapped_column(Float, nullable=False)
    diversity_score: Mapped[float] = mapped_column(Float, nullable=False)
    utility_score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="completed", nullable=False)
    interpretation: Mapped[str] = mapped_column(Text, nullable=False)
    configuration: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)
    payload: Mapped[dict] = mapped_column(JsonType, default=dict, nullable=False)

    metrics: Mapped[list["ComparisonMetric"]] = relationship(back_populates="comparison", cascade="all, delete-orphan")


class ComparisonMetric(Base):
    __tablename__ = "comparison_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comparison_id: Mapped[int] = mapped_column(ForeignKey("comparisons.id"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    original_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    synthetic_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    absolute_difference: Mapped[float | None] = mapped_column(Float, nullable=True)
    relative_difference: Mapped[float | None] = mapped_column(Float, nullable=True)
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    interpretation: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    direction: Mapped[str] = mapped_column(String(64), nullable=False)

    comparison: Mapped[Comparison] = relationship(back_populates="metrics")

