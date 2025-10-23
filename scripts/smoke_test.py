import os
import json
from vector_store import InMemoryVectorStore
from openai_client import chat_completion


def run_smoke():
    os.environ.setdefault("MOCK_OPENAI", "true")
    store = InMemoryVectorStore()
    docs_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    store.add_documents_from_dir(docs_dir)

    q = "What is Retrieval-Augmented Generation?"
    results = store.query(q, top_k=2)
    context = "\n\n---\n\n".join([f"[DOC] {d}" for d, _ in results])

    system_prompt = "You are a helpful assistant."
    user_prompt = f"Context:\n{context}\n\nUser question: {q}"

    resp = chat_completion(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    print("SMOKE TEST RESPONSE:\n")
    print(resp["choices"][0]["message"]["content"])


if __name__ == "__main__":
    run_smoke()
