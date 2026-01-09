"""
Middleware for document processing and context injection
"""
import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from documents import vectorstore, initialize_vectorstore

class DocumentMiddleware:
    """Middleware to handle document retrieval and context injection"""
    
    def __init__(self, similarity_threshold: float = 0.7, max_docs: int = 5):
        self.similarity_threshold = similarity_threshold
        self.max_docs = max_docs
        self.logger = logging.getLogger(__name__)
    
    def get_relevant_context(self, query: str) -> str:
        """
        Retrieve relevant documents based on the query
        """
        if vectorstore is None:
            initialize_vectorstore()
        
        if vectorstore is None:
            return "No documents available for context."
        
        try:
            # Perform similarity search
            relevant_docs = vectorstore.similarity_search_with_score(
                query, 
                k=self.max_docs
            )
            
            if not relevant_docs:
                return "No relevant documents found."
            
            # Filter by similarity threshold and format context
            context_parts = []
            for doc, score in relevant_docs:
                if score <= self.similarity_threshold:  
                    # Extract metadata for context
                    source = doc.metadata.get('source', 'Unknown')
                    filename = os.path.basename(source)
                    
                    context_parts.append(f"[From {filename}]: {doc.page_content}")
            
            if not context_parts:
                return "No documents meet the similarity threshold."
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            self.logger.error(f"Error retrieving document context: {e}")
            return "Error retrieving document context."
    
    def get_document_summary(self) -> Dict[str, Any]:
        """
        Get a summary of available documents by type
        """
        try:
            documents_dir = os.path.join(os.path.dirname(__file__), '..', 'documents')
            summary = {
                'travel_plans': [],
                'budgets': [],
                'todo_lists': [],
                'other': []
            }
            
            for root, dirs, files in os.walk(documents_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, documents_dir)
                    
                    if 'travel_plans' in rel_path:
                        summary['travel_plans'].append(file)
                    elif 'budgets' in rel_path:
                        summary['budgets'].append(file)
                    elif 'todo_lists' in rel_path:
                        summary['todo_lists'].append(file)
                    else:
                        summary['other'].append(file)
            
            return summary
        except Exception as e:
            self.logger.error(f"Error getting document summary: {e}")
            return {}
    
    def read_specific_document(self, filename: str, document_type: str = None) -> Optional[str]:
        """
        Read a specific document by filename
        """
        try:
            documents_dir = os.path.join(os.path.dirname(__file__), '..', 'documents')
            
            # Search for the file
            for root, dirs, files in os.walk(documents_dir):
                if filename in files:
                    file_path = os.path.join(root, filename)
                    
                    if filename.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            return json.dumps(data, indent=2)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return f.read()
            
            return None
        except Exception as e:
            self.logger.error(f"Error reading document {filename}: {e}")
            return None

class QueryEnhancementMiddleware:
    """Middleware to enhance queries with document awareness"""
    
    def __init__(self, document_middleware: DocumentMiddleware):
        self.doc_middleware = document_middleware
        self.logger = logging.getLogger(__name__)
    
    def enhance_query(self, query: str) -> Dict[str, Any]:
        """
        Enhance the query with relevant context and metadata
        """
        try:
            # Get relevant context
            context = self.doc_middleware.get_relevant_context(query)
            
            # Get document summary for reference
            doc_summary = self.doc_middleware.get_document_summary()
            
            # Check if query mentions specific documents
            mentioned_docs = self._extract_mentioned_documents(query)
            
            enhanced_data = {
                'original_query': query,
                'context': context,
                'document_summary': doc_summary,
                'mentioned_documents': mentioned_docs,
                'enhancement_timestamp': datetime.now().isoformat()
            }
            
            return enhanced_data
            
        except Exception as e:
            self.logger.error(f"Error enhancing query: {e}")
            return {
                'original_query': query,
                'context': '',
                'error': str(e)
            }
    
    def _extract_mentioned_documents(self, query: str) -> List[str]:
        """
        Extract potentially mentioned document names from the query
        """
        mentioned = []
        query_lower = query.lower()
        
        # Common document-related keywords
        doc_keywords = [
            'budget', 'plan', 'todo', 'list', 'itinerary', 
            'schedule', 'thailand', 'hong kong', 'new zealand', 
            'southeast asia', 'vaccination'
        ]
        
        for keyword in doc_keywords:
            if keyword in query_lower:
                mentioned.append(keyword)
        
        return mentioned

class ConversationMiddleware:
    """Middleware to manage conversation context and history"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)
    
    def process_conversation_context(self, current_query: str, conversation_history: List[Dict]) -> str:
        """
        Process conversation history to maintain context
        """
        if not conversation_history:
            return ""
        
        # Get recent conversation
        recent_history = conversation_history[-self.max_history:]
        
        # Format conversation context
        context_parts = ["Recent conversation context:"]
        for entry in recent_history:
            user_msg = entry.get('user', '')
            assistant_msg = entry.get('assistant', '')
            
            if user_msg:
                context_parts.append(f"User: {user_msg}")
            if assistant_msg:
                context_parts.append(f"Assistant: {assistant_msg}")
        
        return "\n".join(context_parts)

# Factory function to create middleware instances
def create_middleware_stack():
    """
    Create a complete middleware stack for document processing
    """
    document_middleware = DocumentMiddleware(
        similarity_threshold=0.7,
        max_docs=5
    )
    
    query_enhancement = QueryEnhancementMiddleware(document_middleware)
    conversation_middleware = ConversationMiddleware(max_history=5)
    
    return {
        'document': document_middleware,
        'query_enhancement': query_enhancement,
        'conversation': conversation_middleware
    }