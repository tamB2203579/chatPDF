import os
import fitz
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.text_splitter import SemanticChunker

OPEN_API_KEY = os.getenv("OPEN_API_KEY")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

db_vectors = None

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form.get("msg")
    return get_Chat_response(msg)

@app.route("/upload", methods=["POST"])
def upload_pdf():
    global db_vectors

    if "file" not in request.files:
        return "No file uploaded", 400
    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    content = read_pdf_to_string(filepath)

    embeddings = OpenAIEmbeddings(api_key=OPEN_API_KEY)
    docs = chunking(content, embeddings)
    db_vectors = FAISS.from_documents(docs, embeddings)

    return "File uploaded and processed successfully"

def read_pdf_to_string(filepath):
    doc = fitz.open(filepath)
    content = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        content += page.get_text()
    return content

def chunking(content, embeddings):
    text_splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=90
    )
    return text_splitter.create_documents([content])

rag_template = """\
Use the following context to answer the user's query in a well-formatted, concise, and clear manner paragraph. If you don't have an answer, respond "Tài liệu pdf mà bạn cung cấp không có thông tin cho câu hỏi của bạn!"

Câu hỏi:
{question}

Trả lời:
{context}
"""

rag_prompt = ChatPromptTemplate.from_template(rag_template)
chat_model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=OPEN_API_KEY)

def get_Chat_response(text):    
    if db_vectors:
        chunks_query_retriever = db_vectors.as_retriever(search_kwargs={"k": 5})
        semantic_rag_chain = (
            {"context": chunks_query_retriever, "question": RunnablePassthrough()}
            | rag_prompt
            | chat_model
            | StrOutputParser()
        )
        return semantic_rag_chain.invoke(text)
    else:
        return chat_model.invoke(text).content

if __name__ == '__main__':
    app.run(debug=True)