import React, { useState, useEffect } from 'react';
import {
  Message,
  ChatResponse,
  TravelPlan,
  TodoList,
  Budget,
  TravelPlanSummary,
  TodoListSummary,
  BudgetSummary 
} from './types';
import ChatSection from './ChatSection';
import DocumentPanel from './DocumentPanel';
import './App.css';

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

    // Add user message to history immediately
    const userMessage: Message = {
      user: message,
      assistant: '', // Will be filled when response arrives
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsFirstLoad(false);
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
        // Update the last message with the assistant's response
        setMessages(prev => {
          const updatedMessages = [...prev];
          const lastMessage = updatedMessages[updatedMessages.length - 1];
          if (lastMessage && lastMessage.user === message) {
            updatedMessages[updatedMessages.length - 1] = {
              ...lastMessage,
              assistant: data.response,
              timestamp: data.timestamp
            };
          }
          return updatedMessages;
        });
        
        // Check if response includes a plan, todo, or budget to show
        if (data.show_plan) {
          await loadTravelPlan(data.show_plan);
        } else if (data.show_todo) {
          await loadTodoList(data.show_todo);
        } else if (data.show_budget) {
          await loadBudget(data.show_budget);
        }
        
        // Store current todo info before refresh
        const wasViewingTodo = currentTodo && documentType === 'todo';
        const currentTodoTitle = currentTodo?.title;
        const currentTodoCreated = currentTodo?.created;
        
        // Refresh available documents after each chat response in case new ones were created
        // or existing ones were modified (especially todo lists when items are added)
        await loadAvailableDocuments();
        
        // If we were viewing a todo list and the response might have modified it,
        // refresh the current todo list
        if (wasViewingTodo && currentTodoTitle) {
          // Find the most recently updated todo list that matches our current one
          try {
            const todosResponse = await fetch('http://localhost:5000/todo-lists');
            if (todosResponse.ok) {
              const todosData = await todosResponse.json();
              const matchingTodo = todosData.lists?.find((todo: TodoListSummary) => 
                todo.title === currentTodoTitle || todo.created === currentTodoCreated
              );
              if (matchingTodo) {
                await loadTodoList(matchingTodo.filename);
              }
            }
          } catch (error) {
            console.error('Error refreshing current todo list:', error);
          }
        }
      } else {
        // Update the last message with error response
        setMessages(prev => {
          const updatedMessages = [...prev];
          const lastMessage = updatedMessages[updatedMessages.length - 1];
          if (lastMessage && lastMessage.user === message) {
            updatedMessages[updatedMessages.length - 1] = {
              ...lastMessage,
              assistant: 'Sorry, I encountered an error processing your request. Please try again.',
              timestamp: new Date().toISOString()
            };
          }
          return updatedMessages;
        });
        console.error('Error sending message:', data);
      }
    } catch (error) {
      // Update the last message with error response
      setMessages(prev => {
        const updatedMessages = [...prev];
        const lastMessage = updatedMessages[updatedMessages.length - 1];
        if (lastMessage && lastMessage.user === message) {
          updatedMessages[updatedMessages.length - 1] = {
            ...lastMessage,
            assistant: 'Sorry, I encountered a network error. Please check your connection and try again.',
            timestamp: new Date().toISOString()
          };
        }
        return updatedMessages;
      });
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

  const showDocumentPanelHandler = async () => {
    setShowDocumentPanel(true);
    await loadAvailableDocuments();
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
    
    // eslint-disable-next-line no-restricted-globals
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

  const handleBackToList = () => {
    setCurrentPlan(null);
    setCurrentTodo(null);
    setCurrentBudget(null);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🌏 Travel Assistant</h1>
        <div className="header-buttons">
          {showDocumentPanel ? (
            <button 
              onClick={closeDocumentPanel} 
              className="toggle-button"
            >
              Hide Document
            </button>
          ) : (
            <button 
              onClick={showDocumentPanelHandler} 
              className="toggle-button"
            >
              Show Document
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
        <ChatSection
          messages={messages}
          inputMessage={inputMessage}
          isLoading={isLoading}
          isFirstLoad={isFirstLoad}
          showDocumentPanel={showDocumentPanel}
          onInputChange={setInputMessage}
          onSubmit={handleSubmit}
          onKeyPress={handleKeyPress}
        />
        
        <DocumentPanel
          showDocumentPanel={showDocumentPanel}
          activeTab={activeTab}
          currentPlan={currentPlan}
          currentTodo={currentTodo}
          currentBudget={currentBudget}
          documentType={documentType}
          availablePlans={availablePlans}
          availableTodos={availableTodos}
          availableBudgets={availableBudgets}
          onCloseDocumentPanel={closeDocumentPanel}
          onTabChange={handleTabChange}
          onSelectDocument={selectDocument}
          onDeleteDocument={deleteDocument}
          onUpdateTodoItem={updateTodoItem}
          onBackToList={handleBackToList}
        />
      </div>
    </div>
  );
}

export default App;
