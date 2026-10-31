from collections import Counter
from typing import Any

import numpy as np
from scipy.spatial.distance import jensenshannon
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clamp01(value: float) -> float:
    if np.isnan(value) or np.isinf(value):
        return 0.0
    return float(max(0.0, min(1.0, value)))


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    return round(len(left & right) / len(union), 6) if union else 0.0


def ngram_set(processed_records: list[dict[str, Any]], n: int) -> set[str]:
    values: set[str] = set()
    for record in processed_records:
        tokens = record.get("tokens", [])
        values.update(" ".join(tokens[index : index + n]) for index in range(max(0, len(tokens) - n + 1)))
    return values


def tfidf_dataset_similarity(original_texts: list[str], synthetic_texts: list[str]) -> dict[str, Any]:
    if not original_texts or not synthetic_texts:
        return {"score": 0.0, "method": "tfidf_centroid_cosine", "available": False}
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(original_texts + synthetic_texts)
    original_centroid = matrix[: len(original_texts)].mean(axis=0)
    synthetic_centroid = matrix[len(original_texts) :].mean(axis=0)
    score = float(cosine_similarity(np.asarray(original_centroid), np.asarray(synthetic_centroid))[0][0])
    return {
        "score": round(clamp01(score), 6),
        "method": "TF-IDF centroid cosine similarity using a shared vectorizer fitted on both datasets for distribution comparison",
        "available": True,
    }


def class_distribution_similarity(original: dict[str, Any], synthetic: dict[str, Any]) -> dict[str, Any]:
    labels = sorted(set(original.keys()) | set(synthetic.keys()))
    if not labels:
        return {"score": 1.0, "js_divergence": 0.0, "absolute_differences": {}}
    original_probs = np.array([original.get(label, {}).get("proportion", 0.0) for label in labels], dtype=float)
    synthetic_probs = np.array([synthetic.get(label, {}).get("proportion", 0.0) for label in labels], dtype=float)
    if original_probs.sum() == 0 or synthetic_probs.sum() == 0:
        return {"score": 0.0, "js_divergence": 1.0, "absolute_differences": {}}
    js_distance = float(jensenshannon(original_probs, synthetic_probs, base=2.0))
    differences = {
        label: round(abs(float(original_probs[index] - synthetic_probs[index])), 6)
        for index, label in enumerate(labels)
    }
    return {
        "score": round(clamp01(1 - js_distance), 6),
        "js_divergence": round(js_distance, 6),
        "absolute_differences": differences,
    }


def repeated_ngram_rate(processed_records: list[dict[str, Any]], n: int = 3) -> float:
    counts: Counter[str] = Counter()
    for record in processed_records:
        tokens = record.get("tokens", [])
        counts.update(" ".join(tokens[index : index + n]) for index in range(max(0, len(tokens) - n + 1)))
    total = sum(counts.values())
    if not total:
        return 0.0
    repeated = sum(count for count in counts.values() if count > 1)
    return round(repeated / total, 6)


def character_ngram_jsd(original_texts: list[str], synthetic_texts: list[str]) -> dict[str, Any]:
    if not original_texts or not synthetic_texts:
        return {"score": 0.0, "divergence": 1.0, "available": False}
    
    from sklearn.feature_extraction.text import CountVectorizer
    
    try:
        vectorizer = CountVectorizer(analyzer="char", ngram_range=(3, 3), max_features=10000)
        vectorizer.fit(original_texts + synthetic_texts)
        
        orig_counts = np.asarray(vectorizer.transform(original_texts).sum(axis=0)).flatten()
        synth_counts = np.asarray(vectorizer.transform(synthetic_texts).sum(axis=0)).flatten()
        
        orig_total = orig_counts.sum()
        synth_total = synth_counts.sum()
        
        if orig_total == 0 or synth_total == 0:
            return {"score": 0.0, "divergence": 1.0, "available": True}
            
        orig_probs = orig_counts / orig_total
        synth_probs = synth_counts / synth_total
        
        js_div = float(jensenshannon(orig_probs, synth_probs, base=2.0))
        return {
            "score": round(clamp01(1 - js_div), 6),
            "divergence": round(js_div, 6),
            "available": True,
        }
    except Exception:
        return {"score": 0.0, "divergence": 1.0, "available": False}


def semantic_similarity(original_texts: list[str], synthetic_texts: list[str], sample_size: int, random_seed: int, model_name: str) -> dict[str, Any]:
    rng = np.random.default_rng(random_seed)
    original_sample = list(original_texts)
    synthetic_sample = list(synthetic_texts)
    if len(original_sample) > sample_size:
        original_sample = [original_sample[index] for index in rng.choice(len(original_sample), sample_size, replace=False)]
    if len(synthetic_sample) > sample_size:
        synthetic_sample = [synthetic_sample[index] for index in rng.choice(len(synthetic_sample), sample_size, replace=False)]

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name)
        original_embeddings = model.encode(original_sample, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
        synthetic_embeddings = model.encode(synthetic_sample, batch_size=64, show_progress_bar=False, normalize_embeddings=True)
        score = float(cosine_similarity([np.mean(original_embeddings, axis=0)], [np.mean(synthetic_embeddings, axis=0)])[0][0])
        return {
            "score": round(clamp01(score), 6),
            "available": True,
            "embedding_model": model_name,
            "sample_size": min(sample_size, len(original_sample), len(synthetic_sample)),
            "similarity_method": "centroid_cosine_similarity",
        }
    except Exception as exc:
        fallback = tfidf_dataset_similarity(original_sample, synthetic_sample)
        return {
            "score": fallback["score"],
            "available": False,
            "embedding_model": model_name,
            "sample_size": min(sample_size, len(original_sample), len(synthetic_sample)),
            "similarity_method": "tfidf_fallback_centroid_cosine",
            "error": "Sentence embedding model unavailable; used TF-IDF fallback for local reproducibility.",
            "technical_error": str(exc)[:240],
        }

