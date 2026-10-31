import re
import unicodedata
from collections import Counter

WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return WHITESPACE_RE.sub(" ", str(value)).strip()


def tokenize(text: str, lowercase: bool = True) -> list[str]:
    source = text.lower() if lowercase else text
    tokens: list[str] = []
    current: list[str] = []
    for char in source:
        category = unicodedata.category(char)
        if category[0] in {"L", "M", "N"} or (char in {"'", "’"} and current):
            current.append(char)
        elif current:
            tokens.append("".join(current).strip("'’"))
            current = []
    if current:
        tokens.append("".join(current).strip("'’"))
    return [token for token in tokens if token]


def build_processed_records(texts: list[str]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for text in texts:
        raw_text = normalize_text(text)
        tokens = tokenize(raw_text)
        records.append(
            {
                "raw_text": raw_text,
                "processed_text": " ".join(tokens),
                "tokens": tokens,
                "word_count": len(tokens),
            }
        )
    return records


def top_ngrams(tokenized_texts: list[list[str]], n: int, top_k: int = 25) -> list[dict[str, object]]:
    counts: Counter[tuple[str, ...]] = Counter()
    for tokens in tokenized_texts:
        if len(tokens) >= n:
            counts.update(tuple(tokens[index : index + n]) for index in range(len(tokens) - n + 1))
    return [{"ngram": " ".join(ngram), "count": count} for ngram, count in counts.most_common(top_k)]
