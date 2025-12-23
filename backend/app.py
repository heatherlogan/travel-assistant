import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from prompt_templates import system_role
from actions import handle_adding_budget, handle_adding_todo, save_todo_list, save_travel_plan, update_todo_list, save_budget, update_budget
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish
from typing import Optional, Type, List, Dict, Any
from pydantic import BaseModel, Field
import re

# Agent Tools
class CreateTodoListTool(BaseTool):
    name = "create_todo_list"
    description = "Creates a new todo list. Input should be the title of the todo list."
    
    def _run(self, title: str) -> str:
        try:
            filename = save_todo_list(title, [])
            return f"Created a new todo list called '{title}'! You can add items to it now."
        except Exception as e:
            return f"Error creating todo list: {str(e)}"
    
    def _arun(self, title: str):
        raise NotImplementedError("This tool does not support async")

class AddTodoItemTool(BaseTool):
    name = "add_todo_item"
    description = "Adds an item to the most recent todo list. Input should be the item text to add."
    
    def _run(self, item_text: str) -> str:
        try:
            todo_lists_dir = os.path.join(os.path.dirname(__file__), "..", "todo_lists")
            if os.path.exists(todo_lists_dir):
                todo_files = [f for f in os.listdir(todo_lists_dir) if f.endswith(".json")]
                if todo_files:
                    todo_files.sort(
                        key=lambda f: os.path.getmtime(os.path.join(todo_lists_dir, f)),
                        reverse=True,
                    )
                    latest_todo = todo_files[0]
                    
                    with open(os.path.join(todo_lists_dir, latest_todo), "r", encoding="utf-8") as f:
                        todo_data = json.load(f)
                    
                    new_item = {
                        "id": len(todo_data["items"]) + 1,
                        "text": item_text,
                        "completed": False,
                        "created": datetime.now().isoformat(),
                    }
                    todo_data["items"].append(new_item)
                    
                    update_todo_list(latest_todo, todo_data["items"])
                    return f"Added '{item_text}' to your todo list!"
                else:
                    return "No todo lists found. Create one first!"
            else:
                return "No todo lists found. Create one first!"
        except Exception as e:
            return f"Error adding todo item: {str(e)}"
    
    def _arun(self, item_text: str):
        raise NotImplementedError("This tool does not support async")

class CreateBudgetTool(BaseTool):
    name = "create_budget"
    description = "Creates a new budget. Input should be the title of the budget."
    
    def _run(self, title: str) -> str:
        try:
            filename = save_budget(title, [])
            return f"Created a new budget called '{title}'! You can add expenses to it now."
        except Exception as e:
            return f"Error creating budget: {str(e)}"
    
    def _arun(self, title: str):
        raise NotImplementedError("This tool does not support async")

class AddBudgetItemTool(BaseTool):
    name = "add_budget_item"
    description = "Adds an expense to the most recent budget. Input should be 'item_name,amount' format."
    
    def _run(self, input_str: str) -> str:
        try:
            if ',' in input_str:
                item_name, amount_str = input_str.split(',', 1)
                item_name = item_name.strip()
                amount = float(amount_str.strip())
            else:
                return "Please provide input in format: 'item_name,amount'"
            
            budgets_dir = os.path.join(os.path.dirname(__file__), "..", "budgets")
            if os.path.exists(budgets_dir):
                budget_files = [f for f in os.listdir(budgets_dir) if f.endswith(".json")]
                if budget_files:
                    budget_files.sort(
                        key=lambda f: os.path.getmtime(os.path.join(budgets_dir, f)),
                        reverse=True,
                    )
                    latest_budget = budget_files[0]
                    
                    with open(os.path.join(budgets_dir, latest_budget), "r", encoding="utf-8") as f:
                        budget_data = json.load(f)
                    
                    new_item = {
                        "id": len(budget_data["items"]) + 1,
                        "name": item_name,
                        "amount": amount,
                        "created": datetime.now().isoformat(),
                    }
                    budget_data["items"].append(new_item)
                    
                    update_budget(latest_budget, budget_data["items"])
                    return f"Added '{item_name}' (${amount:.2f}) to your budget!"
                else:
                    return "No budgets found. Create one first!"
            else:
                return "No budgets found. Create one first!"
        except Exception as e:
            return f"Error adding budget item: {str(e)}"
    
    def _arun(self, input_str: str):
        raise NotImplementedError("This tool does not support async")

class ShowDocumentTool(BaseTool):
    name = "show_document"
    description = "Shows a document (travel plan, todo list, or budget). Input should be 'plan', 'todo', or 'budget'."
    
    def _run(self, doc_type: str) -> str:
        try:
            if doc_type.lower() == 'plan':
                travel_plans_dir = os.path.join(os.path.dirname(__file__), '..', 'travel_plans')
                if os.path.exists(travel_plans_dir):
                    plan_files = [f for f in os.listdir(travel_plans_dir) if f.endswith('.txt')]
                    if plan_files:
                        plan_files.sort(key=lambda f: os.path.getmtime(os.path.join(travel_plans_dir, f)), reverse=True)
                        return f"SHOW_PLAN:{plan_files[0]}"
                return "No travel plans found."
            elif doc_type.lower() == 'todo':
                todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'todo_lists')
                if os.path.exists(todo_lists_dir):
                    todo_files = [f for f in os.listdir(todo_lists_dir) if f.endswith('.json')]
                    if todo_files:
                        todo_files.sort(key=lambda f: os.path.getmtime(os.path.join(todo_lists_dir, f)), reverse=True)
                        return f"SHOW_TODO:{todo_files[0]}"
                return "No todo lists found."
            elif doc_type.lower() == 'budget':
                budgets_dir = os.path.join(os.path.dirname(__file__), '..', 'budgets')
                if os.path.exists(budgets_dir):
                    budget_files = [f for f in os.listdir(budgets_dir) if f.endswith('.json')]
                    if budget_files:
                        budget_files.sort(key=lambda f: os.path.getmtime(os.path.join(budgets_dir, f)), reverse=True)
                        return f"SHOW_BUDGET:{budget_files[0]}"
                return "No budgets found."
            else:
                return "Invalid document type. Use 'plan', 'todo', or 'budget'."
        except Exception as e:
            return f"Error showing document: {str(e)}"
    
    def _arun(self, doc_type: str):
        raise NotImplementedError("This tool does not support async")

class SaveTravelPlanTool(BaseTool):
    name = "save_travel_plan"
    description = "Saves a travel plan for a destination. Input should be 'destination,content' format."
    
    def _run(self, input_str: str) -> str:
        try:
            if ',' in input_str:
                destination, content = input_str.split(',', 1)
                destination = destination.strip()
                content = content.strip()
            else:
                return "Please provide input in format: 'destination,content'"
            
            filename = save_travel_plan(destination, content)
            return f"Saved travel plan for {destination}!"
        except Exception as e:
            return f"Error saving travel plan: {str(e)}"
    
    def _arun(self, input_str: str):
        raise NotImplementedError("This tool does not support async")

# Initialize agent tools
tools = [
    CreateTodoListTool(),
    AddTodoItemTool(),
    CreateBudgetTool(),
    AddBudgetItemTool(),
    ShowDocumentTool(),
    SaveTravelPlanTool()
]

# Initialize agent
agent = None

app = Flask(__name__)
CORS(app, origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')])

openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize LangChain components
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key)

# Global variables
vectorstore = None
qa_chain = None
conversation_history = []

# System prompt template using the fixed systemRole
SYSTEM_PROMPT_TEMPLATE = f"""{system_role}

Context from knowledge base: {{context}}

Question: {{question}}

Answer:"""

SYSTEM_PROMPT = PromptTemplate(
    template=SYSTEM_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

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


@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history, qa_chain, agent
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize vector store if not done
        if qa_chain is None:
            initialize_vectorstore()
        
        # Initialize agent if not done
        if agent is None:
            agent = initialize_agent(
                tools, 
                llm, 
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
                verbose=True,
                handle_parsing_errors=True
            )
        
        # Variables to track what to return
        plan_to_show = None
        todo_to_show = None
        budget_to_show = None
        
        # Prepare context from conversation history
        context = "\n".join([f"User: {msg['user']}\nAssistant: {msg['assistant']}" for msg in conversation_history[-3:]])
        
        # Enhanced prompt that combines travel advice with action capabilities
        enhanced_prompt = f"""
You are a helpful travel assistant specializing in Southeast Asia. You can provide travel advice and also help manage travel documents.

Conversation context: {context}

User message: {user_message}

You have access to these tools for document management:
- create_todo_list: Create a new todo list
- add_todo_item: Add items to existing todo lists
- create_budget: Create a new budget
- add_budget_item: Add expenses to budgets (format: 'item_name,amount')
- show_document: Show documents ('plan', 'todo', or 'budget')
- save_travel_plan: Save travel plans (format: 'destination,content')

First, determine if the user wants to:
1. Manage documents (create/add/show todo lists, budgets, or travel plans)
2. Get travel advice

If they want document management, use the appropriate tools. If they want travel advice, provide helpful information about Southeast Asia travel.

For travel advice, focus on practical tips about destinations, transportation, accommodation, food, culture, and activities in Southeast Asia.
"""
        
        try:
            # Use agent to process the message
            response = agent.run(enhanced_prompt)
            
            # Check if agent response contains document show commands
            if "SHOW_PLAN:" in response:
                plan_to_show = response.split("SHOW_PLAN:")[1].strip()
                response = response.replace(f"SHOW_PLAN:{plan_to_show}", "").strip()
                if not response:
                    response = "Here's your latest travel plan:"
            elif "SHOW_TODO:" in response:
                todo_to_show = response.split("SHOW_TODO:")[1].strip()
                response = response.replace(f"SHOW_TODO:{todo_to_show}", "").strip()
                if not response:
                    response = "Here's your latest todo list:"
            elif "SHOW_BUDGET:" in response:
                budget_to_show = response.split("SHOW_BUDGET:")[1].strip()
                response = response.replace(f"SHOW_BUDGET:{budget_to_show}", "").strip()
                if not response:
                    response = "Here's your latest budget:"
                    
        except Exception as agent_error:
            logging.error(f"Agent error: {str(agent_error)}")
            # Fallback to RAG if agent fails
            if qa_chain:
                enhanced_query = f"Context: {context}\nUser question: {user_message}\n\nPlease provide helpful travel advice for Southeast Asia."
                response = qa_chain.run(enhanced_query)
            else:
                response = "I'm sorry, I'm having trouble processing your request right now. Could you try asking again?"
        
        # Add to conversation history
        conversation_history.append({
            'user': user_message,
            'assistant': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Prepare response with optional documents to show
        response_data = {
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        if plan_to_show:
            response_data['show_plan'] = plan_to_show
        
        if todo_to_show:
            response_data['show_todo'] = todo_to_show
        
        if budget_to_show:
            response_data['show_budget'] = budget_to_show
        
        return jsonify(response_data)
    
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
        travel_plans_dir = os.path.join(os.path.dirname(__file__), '..', 'travel_plans')
        
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
        travel_plans_dir = os.path.join(os.path.dirname(__file__), '..', 'travel_plans')
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
        travel_plans_dir = os.path.join(os.path.dirname(__file__), '..', 'travel_plans')
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
        todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'todo_lists')
        
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
        todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'todo_lists')
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
        todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'todo_lists')
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
        budgets_dir = os.path.join(os.path.dirname(__file__), '..', 'budgets')
        
        if not os.path.exists(budgets_dir):
            return jsonify({'budgets': []})
        
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
        
        return jsonify({'budgets': budgets})
    
    except Exception as e:
        print(f"Error getting budgets: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/budgets/<filename>', methods=['GET'])
def get_budget(filename):
    """Get content of a specific budget"""
    try:
        budgets_dir = os.path.join(os.path.dirname(__file__), '..', 'budgets')
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
        budgets_dir = os.path.join(os.path.dirname(__file__), '..', 'budgets')
        filepath = os.path.join(budgets_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Budget not found'}), 404
        
        os.remove(filepath)
        return jsonify({'message': 'Budget deleted successfully'})
    
    except Exception as e:
        print(f"Error deleting budget: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Initialize vector store on startup
    initialize_vectorstore()
    app.run(debug=True, host='0.0.0.0', port=5000)