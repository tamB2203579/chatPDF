import fitz
from langchain_experimental.text_splitter import SemanticChunker
from sklearn.metrics.pairwise import cosine_similarity

def read_pdf_to_string(filepath):
    doc = fitz.open(filepath)
    text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text()
    return text

def chunking(text, embeddings):
    text_splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount= 90,
        min_chunk_size=100
    )
    return text_splitter.create_documents([text])

def calcucate_cosine_distance(vector1, vector2):
    similarity = cosine_similarity(vector1, vector2)
    distance = 1 - similarity
    return distance

