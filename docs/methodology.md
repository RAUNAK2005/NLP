# Methodology

## Objective

The framework evaluates how closely a synthetic NLP classification dataset reproduces an original dataset across:

1. Statistical characteristics
2. Linguistic characteristics
3. Diversity
4. Class distributions
5. Semantic characteristics
6. Downstream task utility

## Preprocessing

Raw text is preserved for semantic and TF-IDF evaluation. Lexical metrics use deterministic whitespace normalization, lowercasing, and regex tokenization. Stopword removal is intentionally not applied by default because the project compares distributional properties and should not remove informative task vocabulary unless a metric explicitly requires it.

## Dataset-Independent Metrics

- Record count, valid record count, missing values, duplicates, and unique texts
- Mean, median, standard deviation, minimum, and maximum words per document
- Vocabulary size, total tokens, and type-token ratio
- Word-frequency and n-gram summaries
- Unique text ratio and duplicate rate

## Similarity Metrics

- Vocabulary similarity: Jaccard overlap of original and synthetic vocabulary sets.
- N-gram similarity: Jaccard overlap of unigram and bigram sets.
- TF-IDF similarity: cosine similarity between dataset-level TF-IDF centroids using a shared vectorizer.
- Semantic similarity: centroid cosine similarity over sampled sentence embeddings when `sentence-transformers` is available; otherwise the system records a TF-IDF fallback.
- Class distribution similarity: `1 - Jensen-Shannon distance`.

## Utility Experiment

The main controlled experiment is:

```text
Original train -> classifier -> original test
Synthetic train -> same classifier family -> same original test
```

The original test split is never used to train the synthetic model. The random seed is recorded in comparison configuration.

## Composite Score

The dashboard reports a project-defined composite score:

```text
Overall = Fidelity * 0.40 + Diversity * 0.30 + Utility * 0.30
```

This is a transparent project scoring method, not a universal scientific standard.

