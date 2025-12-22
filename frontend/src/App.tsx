import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface Message {
  user: string;
  assistant: string;
  timestamp: string;
}

interface ChatResponse {
  response: string;
  timestamp: string;
  show_plan?: string;
  show_todo?: string;
}

interface TravelPlan {
  filename: string;
  destination: string;
  content: string;
}

interface TodoItem {
  id: number;
  text: string;
  completed: boolean;
  created: string;
}

interface TodoList {
  filename: string;
  title: string;
  created: string;
  updated: string;
  items: TodoItem[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [currentPlan, setCurrentPlan] = useState<TravelPlan | null>(null);
  const [currentTodo, setCurrentTodo] = useState<TodoList | null>(null);
  const [showDocumentPanel, setShowDocumentPanel] = useState(false);
  const [documentType, setDocumentType] = useState<'plan' | 'todo'>('plan');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load conversation history on component mount
    loadHistory();
  }, []);

  const loadTodoList = async (filename: string) => {
    try {
      const response = await fetch(`http://localhost:5000/todo-lists/${filename}`);
      if (response.ok) {
        const todo: TodoList = await response.json();
        setCurrentTodo(todo);
        setCurrentPlan(null);
        setDocumentType('todo');
        setShowDocumentPanel(true);
      } else {
        console.error('Error loading todo list');
      }
    } catch (error) {
      console.error('Error loading todo list:', error);
    }
  };

  const updateTodoItem = async (itemId: number, completed: boolean) => {
    if (!currentTodo) return;

    try {
      const updatedItems = currentTodo.items.map(item =>
        item.id === itemId ? { ...item, completed } : item
      );

      const response = await fetch(`http://localhost:5000/todo-lists/${currentTodo.filename}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ items: updatedItems }),
      });

      if (response.ok) {
        setCurrentTodo({
          ...currentTodo,
          items: updatedItems
        });
      } else {
        console.error('Error updating todo item');
      }
    } catch (error) {
      console.error('Error updating todo item:', error);
    }
  };

  const loadTravelPlan = async (filename: string) => {
    try {
      const response = await fetch(`http://localhost:5000/travel-plans/${filename}`);
      if (response.ok) {
        const plan: TravelPlan = await response.json();
        setCurrentPlan(plan);
        setCurrentTodo(null);
        setDocumentType('plan');
        setShowDocumentPanel(true);
      } else {
        console.error('Error loading travel plan');
      }
    } catch (error) {
      console.error('Error loading travel plan:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch('http://localhost:5000/history');
      const data = await response.json();
      setMessages(data.history || []);
      setIsFirstLoad(data.history?.length === 0);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      const data: ChatResponse = await response.json();
      
      if (response.ok) {
        const newMessage: Message = {
          user: message,
          assistant: data.response,
          timestamp: data.timestamp
        };
        
        setMessages(prev => [...prev, newMessage]);
        setInputMessage('');
        setIsFirstLoad(false);
        
        // Check if response includes a plan or todo to show
        if (data.show_plan) {
          await loadTravelPlan(data.show_plan);
        } else if (data.show_todo) {
          await loadTodoList(data.show_todo);
        }
      } else {
        console.error('Error sending message:', data);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearHistory = async () => {
    try {
      await fetch('http://localhost:5000/history', {
        method: 'DELETE',
      });
      setMessages([]);
      setIsFirstLoad(true);
      setCurrentPlan(null);
      setCurrentTodo(null);
      setShowDocumentPanel(false);
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  const closeDocumentPanel = () => {
    setShowDocumentPanel(false);
    setCurrentPlan(null);
    setCurrentTodo(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputMessage);
    }
  };

  // Show welcome message if no history and first load
  const showWelcome = isFirstLoad && messages.length === 0;

  return (
    <div className="App">
      <header className="app-header">
        <h1>🌏 Travel Assistant</h1>
        <div className="header-buttons">
          {showDocumentPanel && (
            <button 
              onClick={closeDocumentPanel} 
              className="toggle-button"
            >
              Hide Document
            </button>
          )}
          <button 
            onClick={clearHistory} 
            className="clear-button"
            disabled={messages.length === 0}
          >
            Clear History
          </button>
        </div>
      </header>
      
      <div className="main-container">
        <div className={`chat-container ${showDocumentPanel ? 'split-view' : ''}`}>
          <div className="messages-container">
            {showWelcome && (
              <div className="welcome-message">
                <div className="message assistant-message">
                  <div className="message-content">
                    Hello! I'm your travel assistant. I'm here to help you plan an amazing trip. Where would you like to travel? You can mention specific countries like Thailand, Vietnam, Cambodia, or cities like Bangkok, Ho Chi Minh City, or Siem Reap.
                    <br /><br />
                    <em>💡 Try saying "show Thailand plan" to view your saved travel documents!</em>
                    <br />
                    <em>📝 You can also create todo lists by saying "create a new todo list" or "add buy sunscreen to my todo list"</em>
                  </div>
                  <div className="message-time">
                    {new Date().toLocaleTimeString()}
                  </div>
                </div>
              </div>
            )}
            
            {messages.map((message, index) => (
              <div key={index} className="conversation">
                <div className="message user-message">
                  <div className="message-content">{message.user}</div>
                  <div className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                <div className="message assistant-message">
                  <div className="message-content">{message.assistant}</div>
                  <div className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message assistant-message loading">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          <form onSubmit={handleSubmit} className="input-form">
            <div className="input-container">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about travel plans, destinations, activities, or say 'show [country] plan' to view travel documents. You can also create todo lists or add items to existing lists..."
                disabled={isLoading}
                rows={3}
              />
              <button type="submit" disabled={isLoading || !inputMessage.trim()}>
                {isLoading ? '...' : 'Send'}
              </button>
            </div>
          </form>
        </div>
        
        {showDocumentPanel && (currentPlan || currentTodo) && (
          <div className="document-panel">
            <div className="document-header">
              {documentType === 'plan' && currentPlan && (
                <h2>📋 {currentPlan.destination} Travel Plan</h2>
              )}
              {documentType === 'todo' && currentTodo && (
                <h2>✅ {currentTodo.title}</h2>
              )}
              <button onClick={closeDocumentPanel} className="close-button">
                ✕
              </button>
            </div>
            <div className="document-content">
              {documentType === 'plan' && currentPlan && (
                <pre>{currentPlan.content}</pre>
              )}
              {documentType === 'todo' && currentTodo && (
                <div className="todo-list">
                  <div className="todo-meta">
                    <p className="todo-info">
                      Created: {new Date(currentTodo.created).toLocaleDateString()}
                      {currentTodo.updated !== currentTodo.created && (
                        <span> • Updated: {new Date(currentTodo.updated).toLocaleDateString()}</span>
                      )}
                    </p>
                    <p className="todo-progress">
                      {currentTodo.items.filter(item => item.completed).length} of {currentTodo.items.length} completed
                    </p>
                  </div>
                  {currentTodo.items.length === 0 ? (
                    <p className="empty-todo">No items yet. Add some by chatting with the assistant!</p>
                  ) : (
                    <ul className="todo-items">
                      {currentTodo.items.map((item) => (
                        <li key={item.id} className={`todo-item ${item.completed ? 'completed' : ''}`}>
                          <label className="todo-checkbox">
                            <input
                              type="checkbox"
                              checked={item.completed}
                              onChange={(e) => updateTodoItem(item.id, e.target.checked)}
                            />
                            <span className="checkmark"></span>
                            <span className="todo-text">{item.text}</span>
                          </label>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
