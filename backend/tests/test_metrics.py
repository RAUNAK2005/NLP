import pandas as pd
import pytest

from app.nlp.similarity import class_distribution_similarity, jaccard_similarity
from app.nlp.preprocessing import tokenize
from app.nlp.statistics import calculate_dataset_statistics
from app.nlp.utility_models import utility_experiment


def test_dataset_statistics_known_values():
    df = pd.DataFrame(
        {
            "text": ["Good product", "Bad product", "Good product", ""],
            "label": ["positive", "negative", "positive", "negative"],
        }
    )
    stats = calculate_dataset_statistics(df, "text", "label")

    assert stats["record_count"] == 4
    assert stats["missing_text_count"] == 1
    assert stats["duplicate_count"] == 1
    assert stats["vocabulary_size"] == 3
    assert stats["type_token_ratio"] == 0.5
    assert stats["class_distribution"]["positive"]["proportion"] == 0.5


def test_jaccard_similarity():
    assert jaccard_similarity({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3, rel=1e-5)
    assert jaccard_similarity(set(), set()) == 1.0


def test_tokenizer_supports_hindi_text():
    tokens = tokenize("यह फिल्म बहुत अच्छी है")

    assert tokens == ["यह", "फिल्म", "बहुत", "अच्छी", "है"]


def test_class_distribution_similarity_identical():
    dist = {"positive": {"proportion": 0.5}, "negative": {"proportion": 0.5}}
    result = class_distribution_similarity(dist, dist)

    assert result["score"] == 1.0
    assert result["js_divergence"] == 0.0


def test_utility_experiment_runs_on_small_balanced_data():
    original_texts = [
        "excellent useful product",
        "great useful product",
        "happy with product",
        "strong good quality",
        "terrible broken product",
        "bad broken product",
        "unhappy with product",
        "weak poor quality",
        "excellent quality",
        "terrible quality",
    ]
    labels = ["pos", "pos", "pos", "pos", "neg", "neg", "neg", "neg", "pos", "neg"]
    synthetic_texts = [
        "good useful item",
        "great happy item",
        "excellent strong item",
        "bad broken item",
        "poor terrible item",
        "weak unhappy item",
    ]
    synthetic_labels = ["pos", "pos", "pos", "neg", "neg", "neg"]

    result = utility_experiment(original_texts, labels, synthetic_texts, synthetic_labels, random_seed=42)

    assert result["available"] is True
    assert "logistic_regression" in result["models"]
