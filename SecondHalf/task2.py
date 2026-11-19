import chromadb
import uuid
import hashlib
import json
client = chromadb.PersistentClient(path="./vector_db")
collection = client.get_or_create_collection(
    name="policy_documents"
)
NAMESPACE = uuid.NAMESPACE_DNS
def create_stable_id(chunk):
    value = f'{chunk["source"]}:{chunk["page"]}:{chunk["chunk_index"]}'
    return str(uuid.uuid5(NAMESPACE, value))
def index_document(file_path):
    chunks = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            chunks.append(json.loads(line))
    ids = []
    documents = []
    metadatas = []
    for chunk in chunks:
        ids.append(create_stable_id(chunk))
        documents.append(chunk["text"])
        metadatas.append({
            "source": chunk["source"],
            "page": chunk["page"],
            "section": chunk["section"],
            "chunk_index": chunk["chunk_index"],
            "word_count": chunk["word_count"],
            "doc_type": chunk["doc_type"],
            "created_date": chunk["created_date"],
            "ingested_at": chunk["ingested_at"]
        })
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
def get_vector_count():
    return collection.count()
def delete_document(source_name):
    collection.delete(
        where={"source": source_name}
    )
def get_file_hash(file_path):
    sha = hashlib.sha256()
    with open(file_path, "rb") as file:
        sha.update(file.read())
    return sha.hexdigest()
index_document("chunks.jsonl")
print("Run 1:", get_vector_count(), "points")
index_document("chunks.jsonl")
print("Run 2 (no change):", get_vector_count(), "points")
index_document("chunks.jsonl")
print("Run 3 (same file):", get_vector_count(), "points")
delete_document("policy.txt")
print("After deletion:", get_vector_count(), "points")
