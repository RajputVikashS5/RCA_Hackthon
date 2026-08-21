from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import sentence_transformers


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

PROJECT_ROOT = BACKEND_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class FakeSentenceTransformer:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def encode(self, texts, convert_to_numpy: bool = True, show_progress_bar: bool = False):
        single_input = isinstance(texts, str)
        items = [texts] if single_input else list(texts)

        vectors = []
        for text in items:
            lower_text = text.lower()
            vector = np.array(
                [
                    float(len(text)),
                    float(lower_text.count("payment") * 5 + lower_text.count("database") * 4 + lower_text.count("service") * 3),
                    float(lower_text.count("error") * 4 + lower_text.count("failure") * 4 + lower_text.count("outage") * 5),
                    float(lower_text.count("incident") * 2 + lower_text.count("root cause") * 3 + lower_text.count("resolution") * 2),
                    float(sum(ord(char) for char in text) % 997),
                    float(text.count(" ")),
                ],
                dtype=np.float32,
            )
            vectors.append(vector)

        array = np.vstack(vectors).astype(np.float32)
        return array[0] if single_input else array


sentence_transformers.SentenceTransformer = FakeSentenceTransformer
