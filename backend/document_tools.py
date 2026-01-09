"""
Document management tools for the travel assistant
"""
import os
import json
from typing import Dict, Any, List, Optional
from langchain.tools import tool
from middleware import DocumentMiddleware

# Initialize document middleware
doc_middleware = DocumentMiddleware()

@tool
def list_available_documents() -> Dict[str, Any]:
    """
    List all available documents organized by type.
    Use this when the user asks about what documents are available.
    """
    try:
        summary = doc_middleware.get_document_summary()
        return {
            "status": "success",
            "documents": summary,
            "message": f"Found documents: {len(summary.get('travel_plans', []))} travel plans, "
                      f"{len(summary.get('budgets', []))} budgets, "
                      f"{len(summary.get('todo_lists', []))} todo lists, "
                      f"{len(summary.get('other', []))} other documents"
        }
    except Exception as e:
        return {"status": "error", "message": f"Error listing documents: {str(e)}"}

@tool
def read_specific_document(filename: str) -> Dict[str, Any]:
    """
    Read the content of a specific document by filename.
    Use this when the user asks about a specific document.
    
    Args:
        filename: The name of the file to read (e.g., "thailand_20251223_095643.txt")
    """
    try:
        content = doc_middleware.read_specific_document(filename)
        if content is None:
            return {
                "status": "error", 
                "message": f"Document '{filename}' not found. Use list_available_documents to see available files."
            }
        
        return {
            "status": "success",
            "filename": filename,
            "content": content,
            "message": f"Successfully read document: {filename}"
        }
    except Exception as e:
        return {"status": "error", "message": f"Error reading document: {str(e)}"}

@tool
def search_documents_by_keyword(keyword: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search for documents containing specific keywords or phrases.
    Use this when the user wants to find documents related to specific topics.
    
    Args:
        keyword: The keyword or phrase to search for
        max_results: Maximum number of results to return (default: 5)
    """
    try:
        context = doc_middleware.get_relevant_context(keyword)
        
        if "No relevant documents found" in context or "No documents available" in context:
            return {
                "status": "info",
                "keyword": keyword,
                "results": [],
                "message": f"No documents found containing '{keyword}'"
            }
        
        # Parse the context to extract document sources
        results = []
        context_parts = context.split('\n\n')
        
        for part in context_parts[:max_results]:
            if '[From ' in part:
                # Extract filename and content
                start = part.find('[From ') + 6
                end = part.find(']: ')
                if start > 5 and end > start:
                    filename = part[start:end]
                    content_snippet = part[end + 3:end + 203] + "..." if len(part) > end + 200 else part[end + 3:]
                    results.append({
                        "filename": filename,
                        "content_snippet": content_snippet
                    })
        
        return {
            "status": "success",
            "keyword": keyword,
            "results": results,
            "message": f"Found {len(results)} documents containing '{keyword}'"
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Error searching documents: {str(e)}"}

@tool
def get_document_statistics() -> Dict[str, Any]:
    """
    Get statistics about the document collection.
    Use this when the user wants an overview of their document collection.
    """
    try:
        summary = doc_middleware.get_document_summary()
        
        total_docs = sum(len(docs) for docs in summary.values())
        
        # Get file sizes and dates if possible
        documents_dir = os.path.join(os.path.dirname(__file__), '..', 'documents')
        recent_files = []
        
        for root, dirs, files in os.walk(documents_dir):
            for file in files[-5:]:  # Get last 5 files
                file_path = os.path.join(root, file)
                try:
                    stat = os.stat(file_path)
                    recent_files.append({
                        "name": file,
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })
                except:
                    continue
        
        return {
            "status": "success",
            "total_documents": total_docs,
            "by_type": {k: len(v) for k, v in summary.items()},
            "recent_files": sorted(recent_files, key=lambda x: x["modified"], reverse=True)[:5],
            "message": f"Document collection contains {total_docs} total files"
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Error getting statistics: {str(e)}"}

# Export tools for use in the main tools module
document_tools = [
    list_available_documents,
    read_specific_document,
    search_documents_by_keyword,
    get_document_statistics
]