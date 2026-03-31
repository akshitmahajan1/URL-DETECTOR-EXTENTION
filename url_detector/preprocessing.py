import math
from collections import Counter
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    length = len(s)
    entropy = 0.0
    for c in counts.values():
        p_x = c / length
        entropy -= p_x * math.log2(p_x)
    return entropy


def extract_manual_features(url: str) -> List[float]:
    length = len(url)
    digit_count = sum(ch.isdigit() for ch in url)
    special_chars = ".-_"
    special_count = sum(ch in special_chars for ch in url)
    entropy = shannon_entropy(url)
    return [
        float(length),
        float(digit_count),
        float(special_count),
        float(entropy),
    ]


def build_char_vocab(urls: pd.Series, extra_chars: str = "") -> Dict[str, int]:
    charset = set()
    for url in urls.astype(str):
        charset.update(list(url))
    charset.update(list(extra_chars))
    # Reserve 0 for padding, 1 for unknown
    char2idx = {"<UNK>": 1}
    for i, ch in enumerate(sorted(charset), start=2):
        char2idx[ch] = i
    return char2idx


def url_to_sequence(url: str, char2idx: Dict[str, int], max_len: int) -> List[int]:
    seq = []
    for ch in str(url):
        seq.append(char2idx.get(ch, char2idx["<UNK>"]))
        if len(seq) >= max_len:
            break
    # pad or truncate
    if len(seq) < max_len:
        seq = seq + [0] * (max_len - len(seq))
    return seq


def preprocess_dataframe(
    df: pd.DataFrame,
    url_column: str,
    label_column: str,
    max_len: int,
    char2idx: Dict[str, int],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    urls = df[url_column].astype(str).tolist()
    labels = df[label_column].astype(int).to_numpy()

    seqs = [url_to_sequence(u, char2idx, max_len) for u in urls]
    X_seq = np.array(seqs, dtype="int32")

    manual_feats = [extract_manual_features(u) for u in urls]
    X_manual = np.array(manual_feats, dtype="float32")

    return X_seq, X_manual, labels
