export interface Message {
  user: string;
  assistant: string;
  timestamp: string;
}

export interface ChatResponse {
  response: string;
  timestamp: string;
  show_plan?: string;
  show_todo?: string;
  show_budget?: string;
}

export interface BudgetItem {
  id: number;
  name: string;
  amount: number;
  created: string;
}

export interface Budget {
  filename: string;
  title: string;
  created: string;
  updated: string;
  items: BudgetItem[];
}

export interface BudgetSummary {
  filename: string;
  title: string;
  created: string;
  updated: string;
  item_count: number;
  total_amount: number;
}

export interface TravelPlan {
  filename: string;
  destination: string;
  content: string;
}

export interface TodoItem {
  id: number;
  text: string;
  completed: boolean;
  created: string;
}

export interface TodoList {
  filename: string;
  title: string;
  created: string;
  updated: string;
  items: TodoItem[];
}

export interface TravelPlanSummary {
  filename: string;
  destination: string;
  created: string;
}

export interface TodoListSummary {
  filename: string;
  title: string;
  created: string;
  updated: string;
  item_count: number;
  completed_count: number;
}
