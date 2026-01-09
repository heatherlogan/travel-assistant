import logging
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_classic.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from prompt_templates import  SYSTEM_PROMPT
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize LangChain components
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
llm = ChatOpenAI(openai_api_key=openai_api_key)

# Global variables
vectorstore = None
qa_chain = None
conversation_history = []

def initialize_vectorstore():

    """Initialize the vector store with documents"""
    global vectorstore, qa_chain
    
    # Create documents directory if it doesn't exist
    documents_dir = os.path.join(os.path.dirname(__file__), '..', 'documents')
    os.makedirs(documents_dir, exist_ok=True)
    
    # Load existing documents
    documents = []
    if os.path.exists(documents_dir) and os.listdir(documents_dir):
        loader = DirectoryLoader(documents_dir, glob="*.txt", loader_cls=TextLoader)
        documents = loader.load()
    
    # documents.append(Document(page_content=default_knowledge, metadata={"source": "default_knowledge"}))
    
    if documents:
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(texts, embeddings)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": SYSTEM_PROMPT}
        )

