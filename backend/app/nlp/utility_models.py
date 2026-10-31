from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


def _metrics(y_true: list[str], y_pred: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 6),
        "precision_macro": round(float(precision_score(y_true, y_pred, average="macro", zero_division=0)), 6),
        "recall_macro": round(float(recall_score(y_true, y_pred, average="macro", zero_division=0)), 6),
        "f1_macro": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 6),
        "f1_weighted": round(float(f1_score(y_true, y_pred, average="weighted", zero_division=0)), 6),
    }


def _model_factory(model_name: str, random_seed: int) -> Pipeline:
    estimators = {
        "logistic_regression": LogisticRegression(max_iter=1000, random_state=random_seed, class_weight="balanced"),
        "linear_svm": LinearSVC(random_state=random_seed, class_weight="balanced"),
        "naive_bayes": MultinomialNB(),
    }
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=1)),
            ("classifier", estimators[model_name]),
        ]
    )


def utility_experiment(
    original_texts: list[str],
    original_labels: list[str],
    synthetic_texts: list[str],
    synthetic_labels: list[str],
    random_seed: int,
) -> dict[str, Any]:
    label_set = set(original_labels) & set(synthetic_labels)
    if len(label_set) < 2 or len(original_texts) < 8 or len(synthetic_texts) < 4:
        return {
            "available": False,
            "reason": "Utility evaluation requires at least two shared classes and enough records for a train/test split.",
        }

    original_pairs = [(text, label) for text, label in zip(original_texts, original_labels, strict=False) if label in label_set and text]
    synthetic_pairs = [(text, label) for text, label in zip(synthetic_texts, synthetic_labels, strict=False) if label in label_set and text]
    if len(original_pairs) < 8 or len(synthetic_pairs) < 4:
        return {"available": False, "reason": "After filtering empty text and unmatched labels, too few examples remained."}

    x_original, y_original = zip(*original_pairs, strict=False)
    x_synthetic, y_synthetic = zip(*synthetic_pairs, strict=False)
    stratify = y_original if min({label: y_original.count(label) for label in set(y_original)}.values()) >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        list(x_original),
        list(y_original),
        test_size=0.3,
        random_state=random_seed,
        stratify=stratify,
    )

    results: dict[str, Any] = {
        "available": True,
        "methodology": "Real->Real and Synthetic->Real use the same original holdout test split. The original test split is not used for training.",
        "random_seed": random_seed,
        "test_size": 0.3,
        "shared_labels": sorted(label_set),
        "models": {},
    }
    for model_name in ["logistic_regression", "linear_svm", "naive_bayes"]:
        try:
            real_model = _model_factory(model_name, random_seed)
            real_model.fit(x_train, y_train)
            real_predictions = real_model.predict(x_test)

            synthetic_model = _model_factory(model_name, random_seed)
            synthetic_model.fit(list(x_synthetic), list(y_synthetic))
            synthetic_predictions = synthetic_model.predict(x_test)

            real_metrics = _metrics(list(y_test), real_predictions)
            synthetic_metrics = _metrics(list(y_test), synthetic_predictions)
            baseline_f1 = max(real_metrics["f1_macro"], 1e-9)
            results["models"][model_name] = {
                "real_to_real": real_metrics,
                "synthetic_to_real": synthetic_metrics,
                "macro_f1_retention": round(min(synthetic_metrics["f1_macro"] / baseline_f1, 1.2), 6),
                "vectorizer": "TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=1)",
            }
        except Exception as exc:
            results["models"][model_name] = {"available": False, "error": str(exc)[:240]}
    return results

