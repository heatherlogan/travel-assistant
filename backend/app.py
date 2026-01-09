import logging
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from documents import initialize_vectorstore
from chat_model import CustomAgentExecutor
from tool_actions import update_todo_list
from documents import vectorstore

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler() 
    ]
)

agent = None
conversation_history = []

app = Flask(__name__)
CORS(app, origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')])

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history, agent, vectorstore
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        logging.info(f"Received user message: {user_message}")
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize vector store if not done
        if vectorstore is None:
            initialize_vectorstore()
        
        # Initialize agent if not done
        if agent is None:
            agent = CustomAgentExecutor(max_iterations=3)
            
        answer = agent.invoke(input=user_message, conversation_history=conversation_history)

        logging.info(f"Agent invocation completed: {answer}")
        
        # Parse the answer if it's a JSON string
        if isinstance(answer, str):
            try:
                answer_data = json.loads(answer)
                response_text = answer_data.get('answer', answer)
            except json.JSONDecodeError:
                response_text = answer
        else:
            response_text = str(answer)
        
        # Add to conversation history
        conversation_history.append({
            'user': user_message,
            'assistant': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({'response': response_text})
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify({'history': conversation_history})

@app.route('/history', methods=['DELETE'])
def clear_history():
    global conversation_history
    conversation_history = []
    return jsonify({'message': 'History cleared successfully'})

@app.route('/documents', methods=['POST'])
def upload_document():
    try:
        data = request.get_json()
        content = data.get('content', '')
        title = data.get('title', 'Untitled Document')
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        # Save document
        documents_dir = os.path.join(os.path.dirname(__file__), '..', 'documents')
        os.makedirs(documents_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title.lower().replace(' ', '_')}_{timestamp}.txt"
        filepath = os.path.join(documents_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Reinitialize vector store to include new document
        initialize_vectorstore()
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'filename': filename
        })
    
    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/travel-plans', methods=['GET'])
def get_travel_plans():
    """Get list of all travel plan files"""
    try:
        travel_plans_dir = os.path.join(os.path.dirname(__file__), '..', 'documents/travel_plans')
        
        if not os.path.exists(travel_plans_dir):
            return jsonify({'plans': []})
        
        plans = []
        for filename in os.listdir(travel_plans_dir):
            if filename.endswith('.txt') and filename != '.gitkeep':
                filepath = os.path.join(travel_plans_dir, filename)
                # Extract destination from filename (before the timestamp)
                destination = filename.split('_')[0].title()
                # Get file modification time
                mod_time = os.path.getmtime(filepath)
                created = datetime.fromtimestamp(mod_time).isoformat()
                
                plans.append({
                    'filename': filename,
                    'destination': destination,
                    'created': created
                })
        
        # Sort by creation time (newest first)
        plans.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'plans': plans})
    
    except Exception as e:
        print(f"Error getting travel plans: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/travel-plans/<filename>', methods=['GET'])
def get_travel_plan(filename):
    """Get content of a specific travel plan"""
    try:
        travel_plans_dir = os.path.join(os.path.dirname(__file__), '..', 'documents/travel_plans')
        filepath = os.path.join(travel_plans_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Travel plan not found'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract destination from filename
        destination = filename.split('_')[0].title()
        
        return jsonify({
            'filename': filename,
            'destination': destination,
            'content': content
        })
    
    except Exception as e:
        print(f"Error getting travel plan: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/travel-plans/<filename>', methods=['DELETE'])
def delete_travel_plan(filename):
    """Delete a specific travel plan"""
    try:
        travel_plans_dir = os.path.join(os.path.dirname(__file__), '..', 'documents/travel_plans')
        filepath = os.path.join(travel_plans_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Travel plan not found'}), 404
        
        os.remove(filepath)
        return jsonify({'message': 'Travel plan deleted successfully'})
    
    except Exception as e:
        print(f"Error deleting travel plan: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/todo-lists', methods=['GET'])
def get_todo_lists():
    """Get list of all todo lists"""
    try:
        todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'documents/todo_lists')
        
        if not os.path.exists(todo_lists_dir):
            return jsonify({'lists': []})
        
        lists = []
        for filename in os.listdir(todo_lists_dir):
            if filename.endswith('.json') and filename != '.gitkeep':
                filepath = os.path.join(todo_lists_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        todo_data = json.load(f)
                    
                    lists.append({
                        'filename': filename,
                        'title': todo_data.get('title', filename.split('_')[0].title()),
                        'created': todo_data.get('created', ''),
                        'updated': todo_data.get('updated', ''),
                        'item_count': len(todo_data.get('items', [])),
                        'completed_count': len([item for item in todo_data.get('items', []) if item.get('completed', False)])
                    })
                except:
                    continue
        
        # Sort by creation time (newest first)
        lists.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'lists': lists})
    
    except Exception as e:
        print(f"Error getting todo lists: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/todo-lists/<filename>', methods=['GET'])
def get_todo_list(filename):
    """Get content of a specific todo list"""
    try:
        todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'documents/todo_lists')
        filepath = os.path.join(todo_lists_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Todo list not found'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            todo_data = json.load(f)
        
        return jsonify({
            'filename': filename,
            'title': todo_data.get('title', ''),
            'created': todo_data.get('created', ''),
            'updated': todo_data.get('updated', ''),
            'items': todo_data.get('items', [])
        })
    
    except Exception as e:
        print(f"Error getting todo list: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/todo-lists/<filename>', methods=['PUT'])
def update_todo_list_endpoint(filename):
    """Update a specific todo list"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        result = update_todo_list(filename, items)
        if result:
            return jsonify({'message': 'Todo list updated successfully', 'filename': result})
        else:
            return jsonify({'error': 'Todo list not found'}), 404
    
    except Exception as e:
        print(f"Error updating todo list: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/todo-lists/<filename>', methods=['DELETE'])
def delete_todo_list(filename):
    """Delete a specific todo list"""
    try:
        todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'documents/todo_lists')
        filepath = os.path.join(todo_lists_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Todo list not found'}), 404
        
        os.remove(filepath)
        return jsonify({'message': 'Todo list deleted successfully'})
    
    except Exception as e:
        print(f"Error deleting todo list: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/budgets', methods=['GET'])
def get_budgets():
    """Get list of all budgets"""
    try:
        budgets_dir = os.path.join(os.path.dirname(__file__), '..', 'documents/budgets')
        
        if not os.path.exists(budgets_dir):
            return jsonify({'documents/budgets': []})
        
        budgets = []
        for filename in os.listdir(budgets_dir):
            if filename.endswith('.json') and filename != '.gitkeep':
                filepath = os.path.join(budgets_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        budget_data = json.load(f)
                    
                    # Calculate total amount
                    total_amount = sum(item.get('amount', 0) for item in budget_data.get('items', []))
                    
                    budgets.append({
                        'filename': filename,
                        'title': budget_data.get('title', filename.split('_')[0].title()),
                        'created': budget_data.get('created', ''),
                        'updated': budget_data.get('updated', ''),
                        'item_count': len(budget_data.get('items', [])),
                        'total_amount': total_amount
                    })
                except:
                    continue
        
        # Sort by creation time (newest first)
        budgets.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'documents/budgets': budgets})
    
    except Exception as e:
        print(f"Error getting budgets: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/budgets/<filename>', methods=['GET'])
def get_budget(filename):
    """Get content of a specific budget"""
    try:
        budgets_dir = os.path.join(os.path.dirname(__file__), '..', 'documents/budgets')
        filepath = os.path.join(budgets_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Budget not found'}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            budget_data = json.load(f)
        
        return jsonify({
            'filename': filename,
            'title': budget_data.get('title', ''),
            'created': budget_data.get('created', ''),
            'updated': budget_data.get('updated', ''),
            'items': budget_data.get('items', [])
        })
    
    except Exception as e:
        print(f"Error getting budget: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/budgets/<filename>', methods=['PUT'])
def update_budget_endpoint(filename):
    """Update a specific budget"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        result = update_budget(filename, items)
        if result:
            return jsonify({'message': 'Budget updated successfully', 'filename': result})
        else:
            return jsonify({'error': 'Budget not found'}), 404
    
    except Exception as e:
        print(f"Error updating budget: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/budgets/<filename>', methods=['DELETE'])
def delete_budget(filename):
    """Delete a specific budget"""
    try:
        budgets_dir = os.path.join(os.path.dirname(__file__), '..', 'documents/budgets')
        filepath = os.path.join(budgets_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Budget not found'}), 404
        
        os.remove(filepath)
        return jsonify({'message': 'Budget deleted successfully'})
    
    except Exception as e:
        print(f"Error deleting budget: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/documents/list', methods=['GET'])
def list_all_documents():
    """List all documents with their metadata"""
    try:
        from middleware import create_middleware_stack
        middleware = create_middleware_stack()
        
        summary = middleware['document'].get_document_summary()
        statistics = middleware['document'].get_document_statistics() if hasattr(middleware['document'], 'get_document_statistics') else {}
        
        return jsonify({
            'summary': summary,
            'statistics': statistics,
            'message': 'Documents listed successfully'
        })
    
    except Exception as e:
        print(f"Error listing documents: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/documents/search', methods=['POST'])
def search_documents():
    """Search documents by keyword"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', '')
        max_results = data.get('max_results', 5)
        
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        from middleware import create_middleware_stack
        middleware = create_middleware_stack()
        
        context = middleware['document'].get_relevant_context(keyword)
        
        return jsonify({
            'keyword': keyword,
            'context': context,
            'message': f'Search completed for: {keyword}'
        })
    
    except Exception as e:
        print(f"Error searching documents: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/documents/read/<filename>', methods=['GET'])
def read_document(filename):
    """Read a specific document by filename"""
    try:
        from middleware import create_middleware_stack
        middleware = create_middleware_stack()
        
        content = middleware['document'].read_specific_document(filename)
        
        if content is None:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'filename': filename,
            'content': content,
            'message': f'Document read successfully: {filename}'
        })
    
    except Exception as e:
        print(f"Error reading document: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Initialize vector store on startup
    initialize_vectorstore()
    app.run(debug=True, host='0.0.0.0', port=5000)