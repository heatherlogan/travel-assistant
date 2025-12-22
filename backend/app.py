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

load_dotenv()

app = Flask(__name__)
CORS(app, origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')])

# Initialize OpenAI
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
    
    # Add default Southeast Asia travel knowledge
    default_knowledge = """
    Backpacker Travel Information:
    
    Popular destinations in Southeast Asia include:
    - Thailand: Bangkok, Chiang Mai, Phuket, Krabi
    - Vietnam: Ho Chi Minh City, Hanoi, Hoi An, Da Nang
    - Cambodia: Siem Reap (Angkor Wat), Phnom Penh
    - Laos: Luang Prabang, Vientiane
    - Myanmar: Yangon, Bagan, Mandalay
    - Malaysia: Kuala Lumpur, Penang, Langkawi
    - Singapore: City-state with gardens, food, and culture
    - Indonesia: Bali, Jakarta, Yogyakarta
    - Philippines: Manila, Cebu, Palawan, Boracay
    
    Best time to visit: November to March (dry season)
    Currency: Varies by country (Thai Baht, Vietnamese Dong, etc.)
    Visa requirements: Check specific country requirements
    
    Transportation:
    - Flights between countries
    - Buses and trains for overland travel
    - Tuk-tuks and taxis for local transport
    - Motorbike rentals popular in many areas
    
    Accommodation:
    - Hostels for budget travelers
    - Boutique hotels and resorts
    - Homestays for cultural immersion
    
    Food highlights:
    - Thai: Pad Thai, Tom Yum, Green Curry
    - Vietnamese: Pho, Banh Mi, Spring Rolls
    - Indonesian: Nasi Goreng, Satay, Rendang
    """
    
    documents.append(Document(page_content=default_knowledge, metadata={"source": "default_knowledge"}))
    
    if documents:
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(texts, embeddings)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
        )

def save_travel_plan(destination, content):
    """Save travel plan to a file"""
    travel_plans_dir = os.path.join(os.path.dirname(__file__), '..', 'travel_plans')
    os.makedirs(travel_plans_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{destination.lower().replace(' ', '_')}_{timestamp}.txt"
    filepath = os.path.join(travel_plans_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Travel Plan for {destination}\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        f.write(content)
    
    return filename

def save_todo_list(title, items):
    """Save todo list to a file"""
    todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'todo_lists')
    os.makedirs(todo_lists_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title.lower().replace(' ', '_')}_{timestamp}.json"
    filepath = os.path.join(todo_lists_dir, filename)
    
    todo_data = {
        'title': title,
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat(),
        'items': items
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(todo_data, f, indent=2, ensure_ascii=False)
    
    return filename

def update_todo_list(filename, items):
    """Update an existing todo list"""
    todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'todo_lists')
    filepath = os.path.join(todo_lists_dir, filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        todo_data = json.load(f)
    
    todo_data['items'] = items
    todo_data['updated'] = datetime.now().isoformat()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(todo_data, f, indent=2, ensure_ascii=False)
    
    return filename

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history, qa_chain
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Initialize vector store if not done
        if qa_chain is None:
            initialize_vectorstore()
        
        # Check if this is the first message or asking about destination
        is_first_message = len(conversation_history) == 0
        is_destination_related = any(word in user_message.lower() for word in ['travel', 'go', 'visit', 'destination', 'trip'])
        
        if is_first_message:
            response = "Hello! I'm your Southeast Asia travel assistant. I'm here to help you plan an amazing trip. Where would you like to travel to in Southeast Asia? You can mention specific countries like Thailand, Vietnam, Cambodia, or cities like Bangkok, Ho Chi Minh City, or Siem Reap."
        else:
            # Prepare context from conversation history
            context = "\n".join([f"User: {msg['user']}\nAssistant: {msg['assistant']}" for msg in conversation_history[-3:]])
            
            # Create a more specific query for the RAG system
            enhanced_query = f"Context: {context}\nUser question: {user_message}\n\nPlease provide helpful travel advice for Southeast Asia."
            
            if qa_chain:
                response = qa_chain.run(enhanced_query)
            else:
                response = "I'm sorry, I'm having trouble accessing my knowledge base right now. Could you try asking again?"
            
            # Check if user is asking to show/display a travel plan or todo list
            show_keywords = ['show', 'display', 'view', 'see', 'open']
            plan_keywords = ['plan', 'plans', 'document', 'documents']
            todo_keywords = ['todo', 'to-do', 'list', 'task', 'tasks', 'checklist']
            
            is_asking_for_plan = any(show_word in user_message.lower() for show_word in show_keywords) and \
                                any(plan_word in user_message.lower() for plan_word in plan_keywords)
            
            is_asking_for_todo = any(show_word in user_message.lower() for show_word in show_keywords) and \
                               any(todo_word in user_message.lower() for todo_word in todo_keywords)
            
            # Check for todo list creation commands
            create_todo_keywords = ['create', 'new', 'make', 'start']
            is_creating_todo = any(create_word in user_message.lower() for create_word in create_todo_keywords) and \
                             any(todo_word in user_message.lower() for todo_word in todo_keywords)
            
            # Check for adding items to todo list
            add_keywords = ['add', 'include', 'put']
            is_adding_to_todo = any(add_word in user_message.lower() for add_word in add_keywords) and \
                              any(todo_word in user_message.lower() for todo_word in todo_keywords)
            
            # Check if user mentioned a specific destination to save
            destinations = ['thailand', 'vietnam', 'cambodia', 'laos', 'myanmar', 'malaysia', 'singapore', 'indonesia', 'philippines']
            mentioned_destination = None
            for dest in destinations:
                if dest in user_message.lower():
                    mentioned_destination = dest.title()
                    break
            
            # Variables to track what to return
            plan_to_show = None
            todo_to_show = None
            
            # Handle todo list creation
            if is_creating_todo:
                # Extract title from message
                import re
                title_patterns = [
                    r'create.*?(?:todo|to-do|list).*?(?:for|called|named)\s+(.+?)(?:\.|$|,)',
                    r'new.*?(?:todo|to-do|list).*?(?:for|called|named)\s+(.+?)(?:\.|$|,)',
                    r'(?:todo|to-do|list).*?(?:for|called|named)\s+(.+?)(?:\.|$|,)'
                ]
                
                title = None
                for pattern in title_patterns:
                    match = re.search(pattern, user_message, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        break
                
                if not title:
                    title = "Travel Todo List"
                
                # Create new todo list with initial items if mentioned
                items = []
                filename = save_todo_list(title, items)
                response += f"\n\nI've created a new todo list called '{title}' for you! You can add items to it by saying things like 'add buy sunscreen to my todo list'."
            
            # Handle adding items to existing todo list
            elif is_adding_to_todo:
                # Find the most recent todo list
                todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'todo_lists')
                if os.path.exists(todo_lists_dir):
                    todo_files = [f for f in os.listdir(todo_lists_dir) if f.endswith('.json')]
                    if todo_files:
                        # Get most recent todo list
                        todo_files.sort(key=lambda f: os.path.getmtime(os.path.join(todo_lists_dir, f)), reverse=True)
                        latest_todo = todo_files[0]
                        
                        # Load the todo list
                        with open(os.path.join(todo_lists_dir, latest_todo), 'r', encoding='utf-8') as f:
                            todo_data = json.load(f)
                        
                        # Extract item from message (simple extraction)
                        item_text = user_message.lower()
                        for add_word in add_keywords:
                            if add_word in item_text:
                                item_start = item_text.find(add_word) + len(add_word)
                                item_text = item_text[item_start:].strip()
                                # Remove common todo list words
                                for todo_word in ['to my todo', 'to the todo', 'to my list', 'to the list', 'to my checklist']:
                                    item_text = item_text.replace(todo_word, '').strip()
                                break
                        
                        if item_text:
                            # Add new item
                            new_item = {
                                'id': len(todo_data['items']) + 1,
                                'text': item_text,
                                'completed': False,
                                'created': datetime.now().isoformat()
                            }
                            todo_data['items'].append(new_item)
                            
                            # Update the file
                            update_todo_list(latest_todo, todo_data['items'])
                            response += f"\n\nI've added '{item_text}' to your todo list!"
            
            # If asking to show a plan for a specific destination, find the most recent plan
            if is_asking_for_plan and mentioned_destination:
                travel_plans_dir = os.path.join(os.path.dirname(__file__), '..', 'travel_plans')
                if os.path.exists(travel_plans_dir):
                    # Find the most recent plan for the destination
                    matching_files = [f for f in os.listdir(travel_plans_dir) 
                                    if f.startswith(mentioned_destination.lower()) and f.endswith('.txt')]
                    if matching_files:
                        # Sort by modification time (newest first)
                        matching_files.sort(key=lambda f: os.path.getmtime(os.path.join(travel_plans_dir, f)), reverse=True)
                        plan_to_show = matching_files[0]
            
            # If asking to show a todo list
            elif is_asking_for_todo:
                todo_lists_dir = os.path.join(os.path.dirname(__file__), '..', 'todo_lists')
                if os.path.exists(todo_lists_dir):
                    todo_files = [f for f in os.listdir(todo_lists_dir) if f.endswith('.json')]
                    if todo_files:
                        # Get most recent todo list or find specific one mentioned
                        todo_files.sort(key=lambda f: os.path.getmtime(os.path.join(todo_lists_dir, f)), reverse=True)
                        todo_to_show = todo_files[0]
            
            if mentioned_destination and is_destination_related and not is_asking_for_plan:
                plan_content = f"User interest: {user_message}\nRecommendation: {response}"
                filename = save_travel_plan(mentioned_destination, plan_content)
                response += f"\n\nI've saved your interest in {mentioned_destination} to your travel plans!"
        
        # Add to conversation history
        conversation_history.append({
            'user': user_message,
            'assistant': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Prepare response with optional plan to show
        response_data = {
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        if plan_to_show:
            response_data['show_plan'] = plan_to_show
        
        if todo_to_show:
            response_data['show_todo'] = todo_to_show
        
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Initialize vector store on startup
    initialize_vectorstore()
    app.run(debug=True, host='0.0.0.0', port=5000)