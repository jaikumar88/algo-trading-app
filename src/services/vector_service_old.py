import os
from typing import List, Tuple
import glob
from openai_client import embed_texts
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class InMemoryVectorStore:
    """Simple in-memory vector store using OpenAI embeddings.

    Documents are loaded from text files. Embeddings are computed with
    OpenAI's text-embedding-3-small. Retrieval is a basic
    cosine-similarity ranking.
    """

    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        self.embedding_model = embedding_model
        self.docs: List[str] = []
        self.vectors: List[np.ndarray] = []

    def _embed(self, texts: List[str]) -> List[np.ndarray]:
        if not texts:
            return []
        return embed_texts(texts, model=self.embedding_model)

    def add_documents_from_dir(self, dir_path: str, ext: str = "*.txt"):
        pattern = os.path.join(dir_path, ext)
        files = glob.glob(pattern)
        texts = []
        for p in files:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    texts.append(f.read())
            except Exception:
                continue
        if texts:
            vecs = self._embed(texts)
            self.docs.extend(texts)
            self.vectors.extend(vecs)

    def add_documents(self, texts: List[str]):
        vecs = self._embed(texts)
        self.docs.extend(texts)
        self.vectors.extend(vecs)

    def query(
        self, query_text: str, top_k: int = 3
    ) -> List[Tuple[str, float]]:
        if not self.docs:
            return []
        q_vec = self._embed([query_text])[0]

        # Ensure we have a proper 2D float matrix for the vectors
        try:
            mat = np.array(self.vectors, dtype=float)
        except Exception:
            # fallback: try stacking
            mat = np.vstack([np.asarray(v, dtype=float) for v in self.vectors])

        if mat.ndim == 1:
            # single vector present; make it 2D
            mat = mat.reshape(1, -1)

        # compute cosine similarities safely
        q_arr = np.asarray(q_vec, dtype=float).reshape(1, -1)
        sims = cosine_similarity(mat, q_arr)
        # sims shape is (n_docs, 1) — convert to 1D
        sims = np.asarray(sims).squeeze()
        # higher is better
        idx = np.argsort(-sims)[:top_k]
        return [(self.docs[i], float(sims[i])) for i in idx]
