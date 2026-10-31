from collections import Counter
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

from app.nlp.preprocessing import build_processed_records, top_ngrams


def histogram(values: list[int], bins: int = 10) -> list[dict[str, float]]:
    if not values:
        return []
    counts, edges = np.histogram(values, bins=min(bins, max(1, len(set(values)))))
    return [
        {"bin_start": float(edges[index]), "bin_end": float(edges[index + 1]), "count": int(count)}
        for index, count in enumerate(counts)
    ]


def class_distribution(labels: list[str]) -> dict[str, dict[str, float]]:
    total = len(labels)
    counts = Counter(labels)
    if total == 0:
        return {}
    return {
        str(label): {"count": int(count), "proportion": round(count / total, 6)}
        for label, count in sorted(counts.items(), key=lambda item: str(item[0]))
    }


def extract_lda_topics(texts: list[str], n_topics: int = 3, n_words: int = 5) -> list[dict[str, Any]]:
    if not texts or len(texts) < n_topics:
        return []
    
    # Filter out empty strings
    valid_texts = [t for t in texts if t.strip()]
    if len(valid_texts) < n_topics:
        return []

    try:
        vectorizer = CountVectorizer(stop_words="english", max_df=0.95, min_df=2)
        X = vectorizer.fit_transform(valid_texts)
        if X.shape[1] < n_words:
            return []

        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=10)
        lda.fit(X)
        feature_names = vectorizer.get_feature_names_out()
        
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_features_ind = topic.argsort()[: -n_words - 1 : -1]
            top_features = [feature_names[i] for i in top_features_ind]
            topics.append({
                "topic_id": topic_idx + 1,
                "keywords": top_features
            })
        return topics
    except Exception:
        return []


def calculate_dataset_statistics(df: pd.DataFrame, text_column: str, label_column: str | None) -> dict[str, Any]:
    raw_texts = ["" if pd.isna(value) else str(value) for value in df[text_column].tolist()]
    processed = build_processed_records(raw_texts)
    tokens_by_doc = [record["tokens"] for record in processed]
    flat_tokens = [token for tokens in tokens_by_doc for token in tokens]
    word_counts = [int(record["word_count"]) for record in processed]
    unique_texts = set(record["raw_text"] for record in processed if record["raw_text"])
    token_counts = Counter(flat_tokens)
    total_tokens = len(flat_tokens)
    vocab_size = len(token_counts)
    missing_text_count = sum(1 for record in processed if not record["raw_text"])
    duplicate_count = int(pd.Series([record["raw_text"] for record in processed]).duplicated().sum())
    labels = []
    missing_label_count = 0
    if label_column:
        for value in df[label_column].tolist():
            if pd.isna(value) or str(value).strip() == "":
                missing_label_count += 1
            else:
                labels.append(str(value).strip())

    mean_length = float(np.mean(word_counts)) if word_counts else 0.0
    median_length = float(np.median(word_counts)) if word_counts else 0.0
    std_length = float(np.std(word_counts)) if word_counts else 0.0

    return {
        "record_count": int(len(df)),
        "valid_record_count": int(len(df) - missing_text_count - missing_label_count),
        "missing_text_count": int(missing_text_count),
        "missing_label_count": int(missing_label_count),
        "duplicate_count": duplicate_count,
        "unique_text_count": len(unique_texts),
        "number_of_classes": len(set(labels)),
        "total_tokens": total_tokens,
        "vocabulary_size": vocab_size,
        "vocabulary": sorted(token_counts.keys()),
        "type_token_ratio": round(vocab_size / total_tokens, 6) if total_tokens else 0.0,
        "text_length": {
            "mean": round(mean_length, 4),
            "median": round(median_length, 4),
            "std": round(std_length, 4),
            "min": int(min(word_counts)) if word_counts else 0,
            "max": int(max(word_counts)) if word_counts else 0,
            "histogram": histogram(word_counts),
        },
        "class_distribution": class_distribution(labels),
        "word_frequency": [{"term": term, "count": int(count)} for term, count in token_counts.most_common(25)],
        "ngram_statistics": {
            "top_unigrams": top_ngrams(tokens_by_doc, 1),
            "top_bigrams": top_ngrams(tokens_by_doc, 2),
            "unique_unigrams": vocab_size,
            "unique_bigrams": len({" ".join(tokens[index : index + 2]) for tokens in tokens_by_doc for index in range(max(0, len(tokens) - 1))}),
        },
        "diversity": {
            "unique_text_ratio": round(len(unique_texts) / len(df), 6) if len(df) else 0.0,
            "duplicate_rate": round(duplicate_count / len(df), 6) if len(df) else 0.0,
            "vocabulary_richness": round(vocab_size / total_tokens, 6) if total_tokens else 0.0,
        },
        "lda_topics": extract_lda_topics(raw_texts),
        "processed_records": processed,
    }

