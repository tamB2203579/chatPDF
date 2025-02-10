import os
import fitz
import pandas as pd
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

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

def encode_pdf(path):
    text = read_pdf_to_string(path)
    text_splitter = SemanticChunker(
        OpenAIEmbeddings(),
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=90,
        min_chunk_size=100
    )
    docs = text_splitter.create_documents([text])
    vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())
    return vector_store

def save_csv(query, docs, path="training.csv"):
    data= []
    for doc, score in docs:
        data.append({
            "query": query,
            "answer": doc.page_content,
            "score": score
        })
    df = pd.DataFrame(data)
    if os.path.exists(path):
        df.to_csv(path, mode='a', header=False, index=False, encoding='utf-8')
    else:
        df.to_csv(path, index=False, encoding='utf-8')