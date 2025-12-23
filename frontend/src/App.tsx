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
  show_budget?: string;
}

interface BudgetItem {
  id: number;
  name: string;
  amount: number;
  created: string;
}

interface Budget {
  filename: string;
  title: string;
  created: string;
  updated: string;
  items: BudgetItem[];
}

interface BudgetSummary {
  filename: string;
  title: string;
  created: string;
  updated: string;
  item_count: number;
  total_amount: number;
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

interface TravelPlanSummary {
  filename: string;
  destination: string;
  created: string;
}

interface TodoListSummary {
  filename: string;
  title: string;
  created: string;
  updated: string;
  item_count: number;
  completed_count: number;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [currentPlan, setCurrentPlan] = useState<TravelPlan | null>(null);
  const [currentTodo, setCurrentTodo] = useState<TodoList | null>(null);
  const [currentBudget, setCurrentBudget] = useState<Budget | null>(null);
  const [showDocumentPanel, setShowDocumentPanel] = useState(true);
  const [documentType, setDocumentType] = useState<'plan' | 'todo' | 'budget'>('plan');
  const [activeTab, setActiveTab] = useState<'plans' | 'todos' | 'budgets'>('plans');
  const [availablePlans, setAvailablePlans] = useState<TravelPlanSummary[]>([]);
  const [availableTodos, setAvailableTodos] = useState<TodoListSummary[]>([]);
  const [availableBudgets, setAvailableBudgets] = useState<BudgetSummary[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load conversation history and available documents on component mount
    loadHistory();
    loadAvailableDocuments();
  }, []);

  const loadAvailableDocuments = async () => {
    try {
      const [plansResponse, todosResponse, budgetsResponse] = await Promise.all([
        fetch('http://localhost:5000/travel-plans'),
        fetch('http://localhost:5000/todo-lists'),
        fetch('http://localhost:5000/budgets')
      ]);
      
      if (plansResponse.ok) {
        const plansData = await plansResponse.json();
        setAvailablePlans(plansData.plans || []);
      }
      
      if (todosResponse.ok) {
        const todosData = await todosResponse.json();
        setAvailableTodos(todosData.lists || []);
      }
      
      if (budgetsResponse.ok) {
        const budgetsData = await budgetsResponse.json();
        setAvailableBudgets(budgetsData.budgets || []);
      }
    } catch (error) {
      console.error('Error loading available documents:', error);
    }
  };

  const loadTodoList = async (filename: string) => {
    try {
      const response = await fetch(`http://localhost:5000/todo-lists/${filename}`);
      if (response.ok) {
        const todo: TodoList = await response.json();
        setCurrentTodo(todo);
        setCurrentPlan(null);
        setCurrentBudget(null);
        setDocumentType('todo');
        setShowDocumentPanel(true);
        await loadAvailableDocuments();
      } else {
        console.error('Error loading todo list');
      }
    } catch (error) {
      console.error('Error loading todo list:', error);
    }
  };

  const loadBudget = async (filename: string) => {
    try {
      const response = await fetch(`http://localhost:5000/budgets/${filename}`);
      if (response.ok) {
        const budget: Budget = await response.json();
        setCurrentBudget(budget);
        setCurrentPlan(null);
        setCurrentTodo(null);
        setDocumentType('budget');
        setShowDocumentPanel(true);
        await loadAvailableDocuments();
      } else {
        console.error('Error loading budget');
      }
    } catch (error) {
      console.error('Error loading budget:', error);
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

  const updateBudgetItem = async (itemId: number, name: string, amount: number) => {
    if (!currentBudget) return;

    try {
      const updatedItems = currentBudget.items.map(item =>
        item.id === itemId ? { ...item, name, amount } : item
      );

      const response = await fetch(`http://localhost:5000/budgets/${currentBudget.filename}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ items: updatedItems }),
      });

      if (response.ok) {
        setCurrentBudget({
          ...currentBudget,
          items: updatedItems
        });
      } else {
        console.error('Error updating budget item');
      }
    } catch (error) {
      console.error('Error updating budget item:', error);
    }
  };

  const loadTravelPlan = async (filename: string) => {
    try {
      const response = await fetch(`http://localhost:5000/travel-plans/${filename}`);
      if (response.ok) {
        const plan: TravelPlan = await response.json();
        setCurrentPlan(plan);
        setCurrentTodo(null);
        setCurrentBudget(null);
        setDocumentType('plan');
        setShowDocumentPanel(true);
        await loadAvailableDocuments();
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
        
        // Check if response includes a plan, todo, or budget to show
        if (data.show_plan) {
          await loadTravelPlan(data.show_plan);
        } else if (data.show_todo) {
          await loadTodoList(data.show_todo);
        } else if (data.show_budget) {
          await loadBudget(data.show_budget);
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
      setCurrentBudget(null);
      setShowDocumentPanel(false);
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  const closeDocumentPanel = () => {
    setShowDocumentPanel(false);
    setCurrentPlan(null);
    setCurrentTodo(null);
    setCurrentBudget(null);
  };

  const handleTabChange = async (tab: 'plans' | 'todos' | 'budgets') => {
    setActiveTab(tab);
    if (!showDocumentPanel) {
      setShowDocumentPanel(true);
      await loadAvailableDocuments();
    }
  };

  const selectDocument = async (filename: string, type: 'plan' | 'todo' | 'budget') => {
    if (type === 'plan') {
      await loadTravelPlan(filename);
      setDocumentType('plan');
    } else if (type === 'todo') {
      await loadTodoList(filename);
      setDocumentType('todo');
    } else if (type === 'budget') {
      await loadBudget(filename);
      setDocumentType('budget');
    }
  };

  const deleteDocument = async (filename: string, type: 'plan' | 'todo' | 'budget', event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent clicking through to select document
    
    if (!confirm(`Are you sure you want to delete this ${type}?`)) {
      return;
    }

    try {
      let endpoint = '';
      if (type === 'plan') {
        endpoint = `http://localhost:5000/travel-plans/${filename}`;
      } else if (type === 'todo') {
        endpoint = `http://localhost:5000/todo-lists/${filename}`;
      } else if (type === 'budget') {
        endpoint = `http://localhost:5000/budgets/${filename}`;
      }

      const response = await fetch(endpoint, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Clear current document if it's the one being deleted
        if ((type === 'plan' && currentPlan?.filename === filename) ||
            (type === 'todo' && currentTodo?.filename === filename) ||
            (type === 'budget' && currentBudget?.filename === filename)) {
          setCurrentPlan(null);
          setCurrentTodo(null);
          setCurrentBudget(null);
        }
        
        // Reload available documents
        await loadAvailableDocuments();
      } else {
        console.error(`Error deleting ${type}:`, await response.text());
        alert(`Failed to delete ${type}. Please try again.`);
      }
    } catch (error) {
      console.error(`Error deleting ${type}:`, error);
      alert(`Failed to delete ${type}. Please try again.`);
    }
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
                    <br />
                    <em>💰 Track your expenses by saying "create a new budget" or "add hotel $120 to my budget"</em>
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
                placeholder="Ask me about travel plans, destinations, activities, or say 'show [country] plan' to view travel documents. You can also create todo lists, budgets, or add items like 'add hotel $120 to my budget'..."
                disabled={isLoading}
                rows={3}
              />
              <button type="submit" disabled={isLoading || !inputMessage.trim()}>
                {isLoading ? '...' : 'Send'}
              </button>
            </div>
          </form>
        </div>
        
        {showDocumentPanel && (
          <div className="document-panel">
            <div className="document-header">
              <div className="document-tabs">
                <button 
                  className={`tab ${activeTab === 'plans' ? 'active' : ''}`}
                  onClick={() => handleTabChange('plans')}
                >
                  📋 Travel Plans ({availablePlans.length})
                </button>
                <button 
                  className={`tab ${activeTab === 'todos' ? 'active' : ''}`}
                  onClick={() => handleTabChange('todos')}
                >
                  ✅ Todo Lists ({availableTodos.length})
                </button>
                <button 
                  className={`tab ${activeTab === 'budgets' ? 'active' : ''}`}
                  onClick={() => handleTabChange('budgets')}
                >
                  💰 Budgets ({availableBudgets.length})
                </button>
              </div>
              <button onClick={closeDocumentPanel} className="close-button">
                ✕
              </button>
            </div>
            
            <div className="document-content">
              {/* Show document/todo lists when no specific item is selected */}
              {!currentPlan && !currentTodo && !currentBudget && (
                <div className="document-browser">
                  {activeTab === 'plans' && (
                    <div className="document-list">
                      {availablePlans.length === 0 ? (
                        <p className="empty-list">No travel plans yet. Create some by chatting about destinations!</p>
                      ) : (
                        availablePlans.map((plan) => (
                          <div 
                            key={plan.filename} 
                            className="document-item"
                            onClick={() => selectDocument(plan.filename, 'plan')}
                          >
                            <div className="document-item-header">
                              <h3>📍 {plan.destination}</h3>
                              <div className="document-actions">
                                <span className="document-date">
                                  {new Date(plan.created).toLocaleDateString()}
                                </span>
                                <button 
                                  className="delete-button"
                                  onClick={(e) => deleteDocument(plan.filename, 'plan', e)}
                                  title="Delete travel plan"
                                >
                                  🗑️
                                </button>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                  
                  {activeTab === 'todos' && (
                    <div className="document-list">
                      {availableTodos.length === 0 ? (
                        <p className="empty-list">No todo lists yet. Create some by saying "create a new todo list"!</p>
                      ) : (
                        availableTodos.map((todo) => (
                          <div 
                            key={todo.filename} 
                            className="document-item"
                            onClick={() => selectDocument(todo.filename, 'todo')}
                          >
                            <div className="document-item-header">
                              <h3>📝 {todo.title}</h3>
                              <div className="document-actions">
                                <span className="document-date">
                                  {new Date(todo.created).toLocaleDateString()}
                                </span>
                                <button 
                                  className="delete-button"
                                  onClick={(e) => deleteDocument(todo.filename, 'todo', e)}
                                  title="Delete todo list"
                                >
                                  🗑️
                                </button>
                              </div>
                            </div>
                            <div className="todo-preview">
                              <span className="progress-indicator">
                                {todo.completed_count} of {todo.item_count} completed
                              </span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                  
                  {activeTab === 'budgets' && (
                    <div className="document-list">
                      {availableBudgets.length === 0 ? (
                        <p className="empty-list">No budgets yet. Create some by saying "create a new budget"!</p>
                      ) : (
                        availableBudgets.map((budget) => (
                          <div 
                            key={budget.filename} 
                            className="document-item"
                            onClick={() => selectDocument(budget.filename, 'budget')}
                          >
                            <div className="document-item-header">
                              <h3>💰 {budget.title}</h3>
                              <div className="document-actions">
                                <span className="document-date">
                                  {new Date(budget.created).toLocaleDateString()}
                                </span>
                                <button 
                                  className="delete-button"
                                  onClick={(e) => deleteDocument(budget.filename, 'budget', e)}
                                  title="Delete budget"
                                >
                                  🗑️
                                </button>
                              </div>
                            </div>
                            <div className="budget-preview">
                              <span className="budget-total">
                                ${budget.total_amount.toFixed(2)} ({budget.item_count} items)
                              </span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              )}
              
              {/* Show specific document content when selected */}
              {documentType === 'plan' && currentPlan && (
                <div className="document-viewer">
                  <div className="viewer-header">
                    <button 
                      className="back-button"
                      onClick={() => { setCurrentPlan(null); setCurrentTodo(null); setCurrentBudget(null); }}
                    >
                      ← Back to {activeTab === 'plans' ? 'Travel Plans' : activeTab === 'todos' ? 'Todo Lists' : 'Budgets'}
                    </button>
                    <h2>📋 {currentPlan.destination} Travel Plan</h2>
                  </div>
                  <div className="document-text">
                    <pre>{currentPlan.content}</pre>
                  </div>
                </div>
              )}
              
              {documentType === 'todo' && currentTodo && (
                <div className="document-viewer">
                  <div className="viewer-header">
                    <button 
                      className="back-button"
                      onClick={() => { setCurrentPlan(null); setCurrentTodo(null); setCurrentBudget(null); }}
                    >
                      ← Back to {activeTab === 'plans' ? 'Travel Plans' : activeTab === 'todos' ? 'Todo Lists' : 'Budgets'}
                    </button>
                    <h2>✅ {currentTodo.title}</h2>
                  </div>
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
                </div>
              )}
              
              {documentType === 'budget' && currentBudget && (
                <div className="document-viewer">
                  <div className="viewer-header">
                    <button 
                      className="back-button"
                      onClick={() => { setCurrentPlan(null); setCurrentTodo(null); setCurrentBudget(null); }}
                    >
                      ← Back to {activeTab === 'plans' ? 'Travel Plans' : activeTab === 'todos' ? 'Todo Lists' : 'Budgets'}
                    </button>
                    <h2>💰 {currentBudget.title}</h2>
                  </div>
                  <div className="budget-content">
                    <div className="budget-meta">
                      <p className="budget-info">
                        Created: {new Date(currentBudget.created).toLocaleDateString()}
                        {currentBudget.updated !== currentBudget.created && (
                          <span> • Updated: {new Date(currentBudget.updated).toLocaleDateString()}</span>
                        )}
                      </p>
                    </div>
                    {currentBudget.items.length === 0 ? (
                      <p className="empty-budget">No budget items yet. Add some by chatting with the assistant!</p>
                    ) : (
                      <div className="budget-table-container">
                        <table className="budget-table">
                          <thead>
                            <tr>
                              <th>Item</th>
                              <th>Amount</th>
                            </tr>
                          </thead>
                          <tbody>
                            {currentBudget.items.map((item) => (
                              <tr key={item.id} className="budget-item">
                                <td className="item-name">{item.name}</td>
                                <td className="item-amount">${item.amount.toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                          <tfoot>
                            <tr className="budget-total-row">
                              <td className="total-label"><strong>Total</strong></td>
                              <td className="total-amount">
                                <strong>${currentBudget.items.reduce((sum, item) => sum + item.amount, 0).toFixed(2)}</strong>
                              </td>
                            </tr>
                          </tfoot>
                        </table>
                      </div>
                    )}
                  </div>
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
