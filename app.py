import os
from dotenv import load_dotenv
from flask import Flask, render_template, request 
from werkzeug.utils import secure_filename
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from helper_functions import *

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('API_KEY')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

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
    if "file" not in request.files:
        return "No file uploaded", 400
    
    file = request.files["file"]

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    global db_vectors
    db_vectors = encode_pdf(filepath)

    return "File uploaded successfully"

rag_template = """\
Use only the following context to answer the user's query in a well-formatted, concise, and clear manner paragraph. If you don't have an answer, respond "Tài liệu pdf mà bạn cung cấp không có thông tin cho câu hỏi của bạn!".

Câu hỏi:
{question}

Trả lời:
{context}
"""

rag_prompt = ChatPromptTemplate.from_template(rag_template)
chat_model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

def get_Chat_response(text):
    chunks_query_retriever = db_vectors.as_retriever(search_kwargs={"k": 3, "score_threshold": 0.5})
    
    docs = db_vectors.similarity_search_with_score(text, k=3)
    save_csv(text, docs)

    semantic_rag_chain = (
        {"context": chunks_query_retriever, "question": RunnablePassthrough()}
        | rag_prompt
        | chat_model
        | StrOutputParser()
    )
    return semantic_rag_chain.invoke(text)

if __name__ == '__main__':
    app.run(debug=True) 