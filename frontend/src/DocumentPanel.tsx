import React from 'react';
import {
  TravelPlan,
  TodoList,
  Budget,
  TravelPlanSummary,
  TodoListSummary,
  BudgetSummary
} from './types';

interface DocumentPanelProps {
  showDocumentPanel: boolean;
  activeTab: 'plans' | 'todos' | 'budgets';
  currentPlan: TravelPlan | null;
  currentTodo: TodoList | null;
  currentBudget: Budget | null;
  documentType: 'plan' | 'todo' | 'budget';
  availablePlans: TravelPlanSummary[];
  availableTodos: TodoListSummary[];
  availableBudgets: BudgetSummary[];
  onCloseDocumentPanel: () => void;
  onTabChange: (tab: 'plans' | 'todos' | 'budgets') => Promise<void>;
  onSelectDocument: (filename: string, type: 'plan' | 'todo' | 'budget') => Promise<void>;
  onDeleteDocument: (filename: string, type: 'plan' | 'todo' | 'budget', event: React.MouseEvent) => Promise<void>;
  onUpdateTodoItem: (itemId: number, completed: boolean) => Promise<void>;
  onBackToList: () => void;
}

const DocumentPanel: React.FC<DocumentPanelProps> = ({
  showDocumentPanel,
  activeTab,
  currentPlan,
  currentTodo,
  currentBudget,
  documentType,
  availablePlans,
  availableTodos,
  availableBudgets,
  onCloseDocumentPanel,
  onTabChange,
  onSelectDocument,
  onDeleteDocument,
  onUpdateTodoItem,
  onBackToList
}) => {
  if (!showDocumentPanel) {
    return null;
  }

  return (
    <div className="document-panel">
      <div className="document-header">
        <div className="document-tabs">
          <button 
            className={`tab ${activeTab === 'plans' ? 'active' : ''}`}
            onClick={() => onTabChange('plans')}
          >
            📋 Travel Plans ({availablePlans.length})
          </button>
          <button 
            className={`tab ${activeTab === 'todos' ? 'active' : ''}`}
            onClick={() => onTabChange('todos')}
          >
            ✅ Todo Lists ({availableTodos.length})
          </button>
          <button 
            className={`tab ${activeTab === 'budgets' ? 'active' : ''}`}
            onClick={() => onTabChange('budgets')}
          >
            💰 Budgets ({availableBudgets.length})
          </button>
        </div>
        <button onClick={onCloseDocumentPanel} className="close-button">
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
                      onClick={() => onSelectDocument(plan.filename, 'plan')}
                    >
                      <div className="document-item-header">
                        <h3>📍 {plan.destination}</h3>
                        <div className="document-actions">
                          <span className="document-date">
                            {new Date(plan.created).toLocaleDateString()}
                          </span>
                          <button 
                            className="delete-button"
                            onClick={(e) => onDeleteDocument(plan.filename, 'plan', e)}
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
                      onClick={() => onSelectDocument(todo.filename, 'todo')}
                    >
                      <div className="document-item-header">
                        <h3>📝 {todo.title}</h3>
                        <div className="document-actions">
                          <span className="document-date">
                            {new Date(todo.created).toLocaleDateString()}
                          </span>
                          <button 
                            className="delete-button"
                            onClick={(e) => onDeleteDocument(todo.filename, 'todo', e)}
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
                      onClick={() => onSelectDocument(budget.filename, 'budget')}
                    >
                      <div className="document-item-header">
                        <h3>💰 {budget.title}</h3>
                        <div className="document-actions">
                          <span className="document-date">
                            {new Date(budget.created).toLocaleDateString()}
                          </span>
                          <button 
                            className="delete-button"
                            onClick={(e) => onDeleteDocument(budget.filename, 'budget', e)}
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
                onClick={onBackToList}
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
                onClick={onBackToList}
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
                          onChange={(e) => onUpdateTodoItem(item.id, e.target.checked)}
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
                onClick={onBackToList}
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
  );
};

export default DocumentPanel;
