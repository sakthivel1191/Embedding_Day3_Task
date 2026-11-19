import tiktoken
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
pdf = PdfReader("sample.pdf")
text = ""
for page in pdf.pages:
    text += page.extract_text() + "\n"
encoding = tiktoken.get_encoding("cl100k_base")
def fixed_chunks(text, size, overlap):
    tokens = encoding.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + size
        chunk = tokens[start:end]
        chunks.append(encoding.decode(chunk))
        start += size - overlap
    return chunks
def sentence_chunks(text, max_tokens):
    sentences = text.replace("?", ".").replace("!", ".").split(".")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence == "":
            continue
        new_chunk = current_chunk + sentence + "."
        token_count = len(encoding.encode(new_chunk))
        if token_count <= max_tokens:
            current_chunk = new_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence + "."
    if current_chunk:
        chunks.append(current_chunk)
    return chunks
fixed_256 = fixed_chunks(text, 256, 32)
fixed_512 = fixed_chunks(text, 512, 50)
sentence_result = sentence_chunks(text, 256)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50
)
recursive_chunks = splitter.split_text(text)
print("Fixed 256/32:", len(fixed_256), "chunks")
print("Fixed 512/50:", len(fixed_512), "chunks")
print("Sentence chunks:", len(sentence_result))
print("Recursive 512/50:", len(recursive_chunks), "chunks")
print("\nExample of fixed-size chunking:")
original_sentence = " ".join(text.split(".")[:2]) + "."
for chunk in fixed_256:
    if chunk and not chunk.rstrip().endswith((".", "?", "!")):
        print(chunk[-100:])
        break
