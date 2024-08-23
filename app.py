from flask import Flask, request, jsonify, render_template
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

def crear_app():
    # Cargar las variables de entorno desde el archivo .env
    load_dotenv()
    
    app = Flask(__name__)
    
    CORS(app, resources={r"/chat": {"origins": "https://thermesuc.github.io"}})
    
    # Configura tu clave API de OpenAI
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:  
        raise ValueError("La clave API de OpenAI no está configurada.")
    
    # Configura el cliente de OpenAI
    openai_client = OpenAI(api_key=openai_api_key)
    
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
    
    
    personalidad = "Eres un asistente útil y amable llamado ThermesAI. Tu tarea es ayudar a responder una pregunta dada en un documento. El primer paso es extraer citas relevantes a la pregunta del documento, delimitado por ####. Debes proporcionar la lista de citas usando '/'. Responde con '¡No se encontraron citas relevantes!'si no se encontraron citas relevantes. Solo puedes responder en español. Si no encuentras información acerca de la pregunta que ha sido dada, busca en la base de datos de OpenAI, asegurate que la respuesta sea precisa, correcta y relevante, menciona que no se encontro en los textos dado, pero que encontraste la información en otro lugar."
    
    @app.route('/chat', methods=['POST'])
    def chat():
        user_input = request.json.get("message")
        
        if not user_input:
            return jsonify({"error": "No se proporcionó ningún mensaje."}), 400
    
        try:
            # Usa qa_chain para obtener la respuesta de la base de datos local
            local_response = qa_chain.run(user_input)
            
            # Si la respuesta local es insatisfactoria, usa la API de OpenAI
            if not local_response or "i don't know" in local_response.lower():
                # Ajustar el prompt para responder en español
                prompt = f"{personalidad} {user_input}"
                openai_response = openai_client.generate([prompt])
                chatbot_response = openai_response.generations[0][0].text.strip()
                print("Response to client:", chatbot_response)
            else:
                chatbot_response = local_response
                print("Response to client:", chatbot_response)
            
            return jsonify({"response": chatbot_response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app
if __name__ == '__main__':
    app = crear_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
