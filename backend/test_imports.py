import os
import sys

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Test the imports
try:
    from flask import Flask
    print("✓ Flask imported successfully")
    
    from flask_cors import CORS
    print("✓ Flask-CORS imported successfully")
    
    from langchain.vectorstores import Chroma
    print("✓ LangChain Chroma imported successfully")
    
    from langchain.embeddings import OpenAIEmbeddings
    print("✓ OpenAI Embeddings imported successfully")
    
    from dotenv import load_dotenv
    print("✓ Python-dotenv imported successfully")
    
    print("\n✅ All dependencies imported successfully!")
    print("Backend is ready to run. Make sure to:")
    print("1. Create a .env file with your OPENAI_API_KEY")
    print("2. Run: python app.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)