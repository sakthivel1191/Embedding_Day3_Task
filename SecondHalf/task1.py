import pymupdf
import json
import os
import re
from datetime import datetime
from docx import Document
def read_pdf(file_path):
    doc = pymupdf.open(file_path)
    pages = []
    for page_number, page in enumerate(doc, start=1):
        data = page.get_text("dict")
        text = ""
        headings = []
        for block in data["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text += span["text"] + " "
                    if span["size"] >= 16 and span["text"].strip():
                        headings.append(span["text"].strip())
        pages.append({
            "page": page_number,
            "text": text,
            "headings": headings
        })
    return pages
def read_word(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return [{"page": 1, "text": text, "headings": []}]
def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    headings = re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE)
    return [{"page": 1, "text": text, "headings": headings}]
def create_chunks(text, chunk_size=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks
def describe_chunk(chunk):
    return f'{chunk["source"]}, page {chunk["page"]}, {chunk["section"]}'
def extract_metadata(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    if extension == ".pdf":
        pages = read_pdf(file_path)
        doc_type = "PDF"
    elif extension == ".docx":
        pages = read_word(file_path)
        doc_type = "Word"
    elif extension == ".txt":
        pages = read_txt(file_path)
        doc_type = "TXT"
    else:
        raise ValueError("Unsupported file format")
    all_chunks = []
    chunk_index = 0
    current_section = "General"
    for page_data in pages:
        headings = page_data["headings"]
        chunks = create_chunks(page_data["text"],20)
        for i, chunk_text in enumerate(chunks):
            if headings and i < len(headings):
                current_section = headings[i]
            chunk = {
                "id": chunk_index,
                "source": os.path.basename(file_path),
                "doc_type": doc_type,
                "page": page_data["page"],
                "section": current_section,
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "ingested_at": datetime.now().isoformat(),
                "chunk_index": chunk_index,
                "word_count": len(chunk_text.split()),
                "text": chunk_text
            }
            all_chunks.append(chunk)
            chunk_index += 1
    return all_chunks
file_path = "policy.txt"
chunks = extract_metadata(file_path)
with open("chunks.jsonl", "w", encoding="utf-8") as file:
    for chunk in chunks:
        file.write(json.dumps(chunk) + "\n")
for chunk in chunks[:3]:
    print(json.dumps(chunk, indent=4))
    print(describe_chunk(chunk))
