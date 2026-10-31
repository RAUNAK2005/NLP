from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.models import Comparison, ComparisonMetric, Dataset, EvaluationMetric, EvaluationRun
from app.nlp.similarity import (
    class_distribution_similarity,
    jaccard_similarity,
    ngram_set,
    repeated_ngram_rate,
    semantic_similarity,
    tfidf_dataset_similarity,
    character_ngram_jsd,
)
from app.nlp.utility_models import utility_experiment


METRIC_INFO = {
    "Vocabulary Similarity": {
        "definition": "Overlap between original and synthetic vocabularies.",
        "formula": "|V_original intersection V_synthetic| / |V_original union V_synthetic|",
        "direction": "higher_is_better",
    },
    "Bigram Similarity": {
        "definition": "Overlap between observed bigrams in both datasets.",
        "formula": "Jaccard similarity over unique bigram sets.",
        "direction": "higher_is_better",
    },
    "TF-IDF Similarity": {
        "definition": "Cosine similarity between dataset-level TF-IDF centroids.",
        "formula": "cosine(mean(TFIDF_original), mean(TFIDF_synthetic))",
        "direction": "higher_is_better",
    },
    "Semantic Similarity": {
        "definition": "Distribution-level semantic similarity using embeddings when available.",
        "formula": "cosine(mean(embeddings_original_sample), mean(embeddings_synthetic_sample))",
        "direction": "higher_is_better",
    },
    "Class Distribution Similarity": {
        "definition": "Similarity between label distributions.",
        "formula": "1 - Jensen-Shannon distance",
        "direction": "higher_is_better",
    },
    "Macro F1 Retention": {
        "definition": "How much original-test macro F1 is retained when training on synthetic data.",
        "formula": "synthetic_to_real_macro_f1 / real_to_real_macro_f1",
        "direction": "higher_is_better",
    },
    "Character N-gram JSD": {
        "definition": "Surface-form divergence measured by the Jensen-Shannon Divergence of character 3-gram distributions.",
        "formula": "JSD(orig_char_3grams, synth_char_3grams)",
        "direction": "lower_is_better",
    },
}


def _records_to_frame(dataset: Dataset) -> pd.DataFrame:
    return pd.DataFrame(dataset.raw_records)


def _text_and_label(dataset: Dataset) -> tuple[list[str], list[str]]:
    frame = _records_to_frame(dataset)
    texts = frame[dataset.text_column].fillna("").astype(str).tolist()
    labels = frame[dataset.label_column].fillna("").astype(str).str.strip().tolist()
    return texts, labels


def _relative_difference(original: float, synthetic: float) -> float:
    denominator = max(abs(original), 1e-9)
    return round(abs(original - synthetic) / denominator, 6)


def _similarity_from_difference(original: float, synthetic: float) -> float:
    return round(max(0.0, 1.0 - _relative_difference(original, synthetic)), 6)


def _metric(
    name: str,
    original: float | None,
    synthetic: float | None,
    similarity: float | None,
    category: str,
    direction: str,
    interpretation: str,
) -> dict[str, Any]:
    diff = None if original is None or synthetic is None else round(synthetic - original, 6)
    rel = None if original is None or synthetic is None else _relative_difference(original, synthetic)
    return {
        "metric_name": name,
        "original_value": original,
        "synthetic_value": synthetic,
        "absolute_difference": diff,
        "relative_difference": rel,
        "similarity_score": similarity,
        "category": category,
        "direction": direction,
        "interpretation": interpretation,
    }


def _score(values: list[float]) -> float:
    usable = [max(0.0, min(1.0, value)) for value in values if value is not None]
    return round((sum(usable) / len(usable)) * 100, 2) if usable else 0.0


def _interpretation(payload: dict[str, Any]) -> str:
    fidelity = payload["scores"]["fidelity_score"]
    diversity = payload["scores"]["diversity_score"]
    utility = payload["scores"]["utility_score"]
    overall = payload["scores"]["overall_score"]
    vocab = payload["similarity"]["vocabulary_similarity"]
    macro_retention = payload["utility"].get("best_macro_f1_retention")
    duplicate_delta = payload["diversity"]["synthetic_duplicate_rate"] - payload["diversity"]["original_duplicate_rate"]

    quality = "strong" if overall >= 80 else "moderate" if overall >= 60 else "limited"
    lines = [
        f"The synthetic dataset shows {quality} overall alignment with the original dataset under the project-defined composite score.",
        f"Fidelity is {fidelity:.1f}/100, supported by vocabulary similarity of {vocab:.1%} and the available distributional comparisons.",
    ]
    if duplicate_delta > 0.03:
        lines.append("Diversity needs attention: the synthetic dataset has a noticeably higher duplicate rate than the original dataset.")
    else:
        lines.append(f"Diversity is {diversity:.1f}/100, with no large duplicate-rate increase detected.")
    if macro_retention is None:
        lines.append("Utility could not be fully estimated because the classification experiment did not have enough shared labeled examples.")
    else:
        lines.append(f"Downstream utility retention is approximately {macro_retention:.1%} using the best available baseline model on the original holdout test set.")
    lines.append("High similarity is interpreted as fidelity, not proof of scientific superiority; excessive similarity may also indicate memorization or insufficient novelty.")
    return " ".join(lines)


def create_evaluation_run(db: Session, dataset: Dataset, run_type: str, metrics_payload: dict[str, Any], config: dict[str, Any]) -> EvaluationRun:
    run = EvaluationRun(
        dataset_id=dataset.id,
        run_type=run_type,
        status="completed",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        config=config,
    )
    db.add(run)
    db.flush()
    for name, value, category in [
        ("record_count", metrics_payload["record_count"], "quality"),
        ("vocabulary_size", metrics_payload["vocabulary_size"], "diversity"),
        ("type_token_ratio", metrics_payload["type_token_ratio"], "diversity"),
        ("duplicate_rate", metrics_payload["diversity"]["duplicate_rate"], "quality"),
        ("avg_text_length", metrics_payload["text_length"]["mean"], "distribution"),
    ]:
        db.add(EvaluationMetric(evaluation_run_id=run.id, metric_name=name, metric_value=float(value), metric_category=category))
    return run


def create_comparison(db: Session, original_dataset_id: int, synthetic_dataset_id: int, weights: dict[str, float] | None = None) -> Comparison:
    settings = get_settings()
    original = (
        db.query(Dataset)
        .options(selectinload(Dataset.statistics))
        .filter(Dataset.id == original_dataset_id)
        .first()
    )
    synthetic = (
        db.query(Dataset)
        .options(selectinload(Dataset.statistics))
        .filter(Dataset.id == synthetic_dataset_id)
        .first()
    )
    if not original or not synthetic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both datasets were not found.")
    if not original.statistics or not synthetic.statistics:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Both datasets must have statistics before comparison.")

    weights = weights or {
        "fidelity": settings.fidelity_weight,
        "diversity": settings.diversity_weight,
        "utility": settings.utility_weight,
    }
    total_weight = max(sum(weights.values()), 1e-9)
    weights = {key: value / total_weight for key, value in weights.items()}

    original_stats = original.statistics.metrics_payload
    synthetic_stats = synthetic.statistics.metrics_payload
    original_texts, original_labels = _text_and_label(original)
    synthetic_texts, synthetic_labels = _text_and_label(synthetic)

    vocabulary_similarity = jaccard_similarity(set(original_stats["vocabulary"]), set(synthetic_stats["vocabulary"]))
    unigram_similarity = jaccard_similarity(
        ngram_set(original_stats["processed_records"], 1), ngram_set(synthetic_stats["processed_records"], 1)
    )
    bigram_similarity = jaccard_similarity(
        ngram_set(original_stats["processed_records"], 2), ngram_set(synthetic_stats["processed_records"], 2)
    )
    tfidf_similarity = tfidf_dataset_similarity(original_texts, synthetic_texts)
    semantic = semantic_similarity(
        original_texts,
        synthetic_texts,
        settings.default_sample_size,
        settings.random_seed,
        settings.embedding_model,
    )
    class_similarity = class_distribution_similarity(original_stats["class_distribution"], synthetic_stats["class_distribution"])
    length_similarity = _similarity_from_difference(original_stats["text_length"]["mean"], synthetic_stats["text_length"]["mean"])
    char_jsd = character_ngram_jsd(original_texts, synthetic_texts)

    original_unique_ratio = original_stats["diversity"]["unique_text_ratio"]
    synthetic_unique_ratio = synthetic_stats["diversity"]["unique_text_ratio"]
    original_duplicate_rate = original_stats["diversity"]["duplicate_rate"]
    synthetic_duplicate_rate = synthetic_stats["diversity"]["duplicate_rate"]
    original_repetition = repeated_ngram_rate(original_stats["processed_records"])
    synthetic_repetition = repeated_ngram_rate(synthetic_stats["processed_records"])
    diversity_similarity = _similarity_from_difference(original_unique_ratio, synthetic_unique_ratio)
    repetition_similarity = _similarity_from_difference(original_repetition, synthetic_repetition)
    duplicate_score = max(0.0, 1 - synthetic_duplicate_rate)

    utility = utility_experiment(original_texts, original_labels, synthetic_texts, synthetic_labels, settings.random_seed)
    model_retentions = [
        value["macro_f1_retention"]
        for value in utility.get("models", {}).values()
        if isinstance(value, dict) and "macro_f1_retention" in value
    ]
    best_macro_retention = max(model_retentions) if model_retentions else None

    fidelity_components = [
        vocabulary_similarity,
        unigram_similarity,
        bigram_similarity,
        tfidf_similarity["score"],
        semantic["score"],
        class_similarity["score"],
        length_similarity,
    ]
    diversity_components = [synthetic_unique_ratio, duplicate_score, synthetic_stats["type_token_ratio"], diversity_similarity, repetition_similarity]
    utility_components = [best_macro_retention] if best_macro_retention is not None else []
    fidelity_score = _score(fidelity_components)
    diversity_score = _score(diversity_components)
    utility_score = _score(utility_components)
    overall_score = round(
        fidelity_score * weights["fidelity"] + diversity_score * weights["diversity"] + utility_score * weights["utility"],
        2,
    )

    metrics = [
        _metric(
            "Record Count",
            float(original_stats["record_count"]),
            float(synthetic_stats["record_count"]),
            _similarity_from_difference(original_stats["record_count"], synthetic_stats["record_count"]),
            "quality",
            "match_original",
            "Record counts should be comparable for a controlled evaluation, but exact equality is not required.",
        ),
        _metric(
            "Average Text Length",
            float(original_stats["text_length"]["mean"]),
            float(synthetic_stats["text_length"]["mean"]),
            length_similarity,
            "distribution",
            "match_original",
            "Text length is compared by relative difference because neither longer nor shorter is inherently better.",
        ),
        _metric("Vocabulary Size", float(original_stats["vocabulary_size"]), float(synthetic_stats["vocabulary_size"]), _similarity_from_difference(original_stats["vocabulary_size"], synthetic_stats["vocabulary_size"]), "diversity", "match_original", "Vocabulary size indicates lexical coverage relative to the original dataset."),
        _metric("Type-Token Ratio", float(original_stats["type_token_ratio"]), float(synthetic_stats["type_token_ratio"]), _similarity_from_difference(original_stats["type_token_ratio"], synthetic_stats["type_token_ratio"]), "diversity", "match_original", "Type-token ratio estimates lexical richness while remaining sensitive to dataset length."),
        _metric("Duplicate Rate", float(original_duplicate_rate), float(synthetic_duplicate_rate), max(0.0, 1 - synthetic_duplicate_rate), "diversity", "lower_is_better", "Lower duplicate rate generally indicates healthier synthetic diversity."),
        _metric("Vocabulary Similarity", None, None, vocabulary_similarity, "similarity", "higher_is_better", "Jaccard vocabulary overlap measures lexical fidelity."),
        _metric("Bigram Similarity", None, None, bigram_similarity, "similarity", "higher_is_better", "Bigram overlap checks whether local phrase patterns are preserved."),
        _metric("Class Distribution Similarity", None, None, class_similarity["score"], "distribution", "higher_is_better", "Label distribution similarity uses bounded Jensen-Shannon distance."),
        _metric("TF-IDF Similarity", None, None, tfidf_similarity["score"], "similarity", "higher_is_better", "Shared TF-IDF centroid similarity compares dataset-level lexical distributions."),
        _metric("Semantic Similarity", None, None, semantic["score"], "similarity", "higher_is_better", "Semantic similarity uses sentence embeddings when available and records fallback behavior when not."),
        _metric("Macro F1 Retention", None, None, best_macro_retention, "utility", "higher_is_better", "Macro F1 retention compares Synthetic->Real against the Real->Real baseline on the same original test split."),
        _metric("Character N-gram JSD", None, None, char_jsd["divergence"], "diversity", "lower_is_better", "Character 3-gram distribution divergence acts as an intrinsic proxy for privacy preservation."),
    ]

    scores = {
        "fidelity_score": fidelity_score,
        "diversity_score": diversity_score,
        "utility_score": utility_score,
        "overall_score": overall_score,
    }
    payload = {
        "scores": scores,
        "weights": weights,
        "similarity": {
            "vocabulary_similarity": vocabulary_similarity,
            "unigram_similarity": unigram_similarity,
            "bigram_similarity": bigram_similarity,
            "tfidf_similarity": tfidf_similarity,
            "semantic_similarity": semantic,
            "class_distribution_similarity": class_similarity,
            "length_similarity": length_similarity,
            "character_ngram_jsd": char_jsd,
        },
        "diversity": {
            "original_unique_ratio": original_unique_ratio,
            "synthetic_unique_ratio": synthetic_unique_ratio,
            "original_duplicate_rate": original_duplicate_rate,
            "synthetic_duplicate_rate": synthetic_duplicate_rate,
            "original_repetition_rate": original_repetition,
            "synthetic_repetition_rate": synthetic_repetition,
        },
        "utility": {**utility, "best_macro_f1_retention": best_macro_retention},
        "metric_definitions": METRIC_INFO,
        "methodology_note": "Project-defined composite evaluation score; not a universal scientific standard.",
    }
    payload["interpretation"] = _interpretation(payload)
    config = {
        "task_type": original.task_type,
        "random_seed": settings.random_seed,
        "embedding_model": settings.embedding_model,
        "sample_size": settings.default_sample_size,
        "scoring_weights": weights,
        "classifier_models": ["logistic_regression", "linear_svm", "naive_bayes"],
        "preprocessing": {
            "semantic_evaluation": "raw text preserved",
            "lexical_metrics": "whitespace normalization, lowercasing, regex tokenization",
        },
    }

    original_run = create_evaluation_run(db, original, "original_analysis", original_stats, config)
    synthetic_run = create_evaluation_run(db, synthetic, "synthetic_analysis", synthetic_stats, config)
    comparison = Comparison(
        original_dataset_id=original.id,
        synthetic_dataset_id=synthetic.id,
        original_run_id=original_run.id,
        synthetic_run_id=synthetic_run.id,
        overall_score=overall_score,
        fidelity_score=fidelity_score,
        diversity_score=diversity_score,
        utility_score=utility_score,
        interpretation=payload["interpretation"],
        configuration=config,
        payload=payload,
    )
    db.add(comparison)
    db.flush()
    for metric in metrics:
        db.add(ComparisonMetric(comparison_id=comparison.id, **metric))
    db.commit()
    return get_comparison(db, comparison.id)


def get_comparison(db: Session, comparison_id: int) -> Comparison:
    comparison = (
        db.query(Comparison)
        .options(selectinload(Comparison.metrics))
        .filter(Comparison.id == comparison_id)
        .first()
    )
    if not comparison:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comparison not found.")
    return comparison

