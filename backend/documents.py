import logging
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader, JSONLoader

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize LangChain components
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
llm = ChatOpenAI(openai_api_key=openai_api_key)

vectorstore = None

def initialize_vectorstore():

    """Initialize the vector store with documents"""
    global vectorstore
    
    # Create documents directory if it doesn't exist
    documents_dir = os.path.join(os.path.dirname(__file__), '..', 'documents')
    os.makedirs(documents_dir, exist_ok=True)

    print("Reading documents from:", documents_dir)

    # Load existing documents with separate loaders
    documents = []
    if os.path.exists(documents_dir) and os.listdir(documents_dir):
        # Load .txt files
        try:
            txt_loader = DirectoryLoader(documents_dir, glob="**/*.txt", loader_cls=TextLoader)
            txt_documents = txt_loader.load()
            documents.extend(txt_documents)
            print(f"Loaded {len(txt_documents)} .txt documents")
        except Exception as e:
            print(f"Error loading .txt files: {e}")
        
        # Load .json files 
        try:
            json_loader = DirectoryLoader(
                documents_dir, 
                glob="**/*.json", 
                loader_cls=JSONLoader,
                loader_kwargs={'jq_schema': '.', 'text_content': False}
            )
            json_documents = json_loader.load()
            documents.extend(json_documents)
            print(f"Loaded {len(json_documents)} .json documents")
        except Exception as e:
            print(f"Error loading .json files: {e}")
    
    print(f"Total loaded {len(documents)} documents for vectorstore initialization.")
    
    if documents:
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(texts, embeddings)