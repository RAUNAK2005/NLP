# Research Notes

## Possible Hypotheses

H1: Synthetic datasets generated to resemble real datasets will preserve similar class distributions.

H2: Synthetic datasets will exhibit measurable semantic similarity to their corresponding original datasets.

H3: Synthetic datasets with higher linguistic fidelity will generally demonstrate better downstream classification utility.

H4: Synthetic datasets may show reduced diversity or increased repetition compared with original datasets.

These are hypotheses to test, not claims already proven by the application.

## Important Limitation

A synthetic dataset that is highly similar to an original dataset is not automatically better. High similarity may indicate fidelity, while excessive similarity may also indicate memorization or insufficient novelty. That is why the project evaluates fidelity, diversity, and utility together.

## Recommended Experiment Logging

For each dataset pair, record:

- Dataset source and generation method
- Task type
- Text and label columns
- Random seed
- Train/test split strategy
- Metric definitions
- Model family and vectorizer configuration
- Scoring weights
- Exported JSON report

