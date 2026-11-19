import tiktoken
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
pdf = PdfReader("sample.pdf")
encoding = tiktoken.get_encoding("cl100k_base")
pages = []
for i, page in enumerate(pdf.pages):
    page_text = page.extract_text() or ""
    pages.append((i + 1, page_text))
questions = [
    ("What is Python used for?", 1),
    ("What is artificial intelligence?", 2),
    ("What is tokenization?", 3),
    ("What are embeddings?", 4),
    ("What is a vector database?", 5),
    ("What is chunking?", 6),
    ("What does overlap mean?", 7),
    ("What is sentence chunking?", 8),
    ("What is hit rate?", 9),
    ("What is the benefit of a 512-token chunk?", 10)
]
model = SentenceTransformer("all-MiniLM-L6-v2")
def create_chunks(pages, size):
    chunks = []
    overlap = min(50, size - 1)
    for page_no, page_text in pages:
        tokens = encoding.encode(page_text)
        start = 0
        while start < len(tokens):
            end = start + size
            chunk_tokens = tokens[start:end]
            chunk_text = encoding.decode(chunk_tokens)
            chunks.append({
                "text": chunk_text,
                "page": page_no
            })
            start += size - overlap
    return chunks
def calculate_hit_rate(chunks, questions):
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )
    embeddings = embeddings.astype("float32")
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    hits = 0
    for question, correct_page in questions:
        query_embedding = model.encode(
            [question],
            convert_to_numpy=True
        ).astype("float32")
        faiss.normalize_L2(query_embedding)
        distances, indices = index.search(query_embedding, 3)
        retrieved_pages = []
        for idx in indices[0]:
            if idx != -1:
                retrieved_pages.append(chunks[idx]["page"])
        if correct_page in retrieved_pages:
            hits += 1
    hit_rate = (hits / len(questions)) * 100
    return hit_rate
chunk_sizes = [128, 256, 512, 1024]
results = []
for size in chunk_sizes:
    chunks = create_chunks(pages, size)
    hit_rate = calculate_hit_rate(chunks, questions)
    results.append({
        "Chunk Size": size,
        "Total Questions": len(questions),
        "Hit Rate": hit_rate
    })
    print("Chunk Size:", size)
    print("Total Chunks:", len(chunks))
    print("Hit Rate:", hit_rate, "%")
    print()
df = pd.DataFrame(results)
print("\nFinal Hit Rate Table")
print(df)
df.to_csv("hit_rate_table.csv", index=False)
plt.figure(figsize=(8, 5))
plt.plot(
    df["Chunk Size"],
    df["Hit Rate"],
    marker="o",
    color="blue",
    linewidth=2
)
plt.xlabel("Chunk Size")
plt.ylabel("Hit Rate (%)")
plt.title("Hit Rate vs Chunk Size")
plt.xticks(chunk_sizes)
plt.ylim(0, 100)
plt.grid(True)
plt.savefig(
    "hit_rate_graph.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
