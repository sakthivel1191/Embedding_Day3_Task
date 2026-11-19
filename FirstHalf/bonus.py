from langchain_text_splitters import MarkdownHeaderTextSplitter
markdown_text = """
# Python
Python is a programming language.
## Variables
Variables store values.
## Functions
Functions are reusable blocks of code.
# Machine Learning
Machine learning allows computers to learn from data.
## Supervised Learning
Supervised learning uses labelled data.
## Unsupervised Learning
Unsupervised learning uses unlabelled data.
"""
headers = [
    ("#", "Main Topic"),
    ("##", "Sub Topic")
]
splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers
)
chunks = splitter.split_text(markdown_text)
for chunk in chunks:
    print(chunk.page_content)
    print(chunk.metadata)
    print("----------------")
    