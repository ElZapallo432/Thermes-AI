from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_openai import OpenAI
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configura tu clave API de OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("La clave API de OpenAI no está configurada.")

# Configura el cliente de OpenAI
openai_client = OpenAI(api_key=openai_api_key, max_tokens= -1)

# Loader de .txt
document_paths = ['data.txt', 'data1.txt', 'data2.txt', 'data3.txt', 'data10.txt']
documents = []
for path in document_paths:
    loader = TextLoader(path, encoding="UTF-8")
    documents.extend(loader.load())

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

incrustacion = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, incrustacion)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Configura el RetrievalQA para la cadena de recuperación
qa_chain = RetrievalQA.from_chain_type(
    llm=openai_client,
    chain_type="stuff",  # Puedes ajustar el tipo de cadena según tus necesidades
    retriever=vectorstore.as_retriever(),
    memory=memory
)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    
    if not user_input:
        return jsonify({"error": "No se proporcionó ningún mensaje."}), 400

    try:
        # Usa qa_chain para obtener la respuesta de la base de datos local
        local_response = qa_chain.run(user_input)
        
        # Si la respuesta local es insatisfactoria, usa la API de OpenAI
        if not local_response or "i don't know." in local_response.lower():
            openai_response = openai_client.generate([user_input])
            chatbot_response = openai_response.generations[0][0].text.strip()
        else:
            chatbot_response = local_response
        
        return jsonify({"response": chatbot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
