from datetime import datetime
from plan_actions import save_travel_plan
from tool_actions import handle_adding_todo, create_new_todo_list
from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
from langchain.tools import tool
    
############## Todo List Tools ##############
@tool 
def create_todo_list_tool(title: str, items: Optional[List[str]] = None) -> str:
    """
    Use this tool to create a new todo list with a given title, and add items to it if the user specifies.
    The todo list should be saved as a json file in the 'documents/todo_lists' directory. 

    Format the title and add a releveant emoji to display alongside the title in the todo list app. 

    IMPORTANT: The 'items' parameter must be a list of individual strings, where each string is a separate todo item.
    
    For example:
    - If user says "get passport and renew drivers licence", pass: ["get passport", "renew drivers licence"]
    - If user says "buy clothes, book hotel, pack bags", pass: ["buy clothes", "book hotel", "pack bags"]
    - For a single item "buy groceries", pass: ["buy groceries"]
    
    :param title: Description
    :type title: str
    :param items: Description
    :type items: Optional[List[str]]
    :return: Description
    :rtype: str
    """
    if items is None:
        items = []
    filename = create_new_todo_list(title, items)
    return f"Created a new todo list called '{title}'! You can add more items to it at any time."

@tool
def add_todo_item_tool(items: List[str], filename: Optional[str] = None) -> str:
    """
    Use this tool to add items to add to the specified todo list, or the most recent todo list if none is specified.
    If the user specifies an existing todo list, use your context to determine which exisiting file to add to.

    IMPORTANT: The 'items' parameter must be a list of individual strings, where each string is a separate todo item.
    
    For example:
    - If user says "get passport and renew drivers licence", pass: ["get passport", "renew drivers licence"]
    - If user says "buy clothes, book hotel, pack bags", pass: ["buy clothes", "book hotel", "pack bags"]
    - For a single item "buy groceries", pass: ["buy groceries"]
    
    DO NOT pass a single string with separators like "get passport\nrenew drivers licence" or "item1,item2".
    Each todo item should be a separate string element in the list.
    
    If the user adds an item that already exists in the todo list, it should not be added again.
    
    :param items: List of todo item strings to add to the most recent todo list
    :type items: List[str]
    :param filename: Optional filename of the todo list to add items to
    :type filename: Optional[str]
    :return: Confirmation message about the items added
    :rtype: str
    """
    response = handle_adding_todo(items, filename)
    return response



################# Travel Planner tools #################

@tool 
def create_travel_plan_tool(destination: str, content: str) -> str:
    """
    Use this tool to create a new travel plan for a specified destination, or a general travel plan if not specified by the user.
    Only suggest this tool when the user explicitly requests you to save the travel plan.
    The plan contain activities, accommodation, dining options, and transport at the destination.

    Use appropriate sections and formatting to organize the travel plan clearly.
    Use either bullet points or free text to outline the travel plan details.
    The travel plan should be saved as a text file in the 'documents/travel_plans' directory.

    Store the travel plan with a filename format like 'destination_YYYYMMDD_HHMMSS.txt'.
    If it is country specific, add the country flag as an emoji in the title of the travel plan.

    :param destination: The destination for the travel plan (e.g., "Thailand")
    :type destination: str
    :param content: The content/details of the travel plan
    :type content: str
    :return: Confirmation message about the created travel plan
    :rtype: str
    """
    response = save_travel_plan(destination, content)
    return response





@tool
def final_answer_tool(answer: str, tools_used: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Use this tool to provide a final answer to the user.
    
    :param answer: The final answer to provide to the user in natural language
    :type answer: str
    :param tools_used: List of tool names that were used
    :type tools_used: Optional[List[str]]
    :return: Dictionary containing the answer and tools used
    :rtype: Dict[str, Any]
    """
    if tools_used is None:
        tools_used = []
    return {"answer": answer, "tools_used": tools_used}

# class CreateBudgetTool(BaseTool):
#     name: str = "create_budget"
#     description: str = "Creates a new budget. Input should be the title of the budget."
    
#     def _run(self, title: str) -> str:
#         try:
#             filename = save_budget(title, [])
#             return f"Created a new budget called '{title}'! You can add expenses to it now."
#         except Exception as e:
#             return f"Error creating budget: {str(e)}"
    
#     def _arun(self, title: str):
#         raise NotImplementedError("This tool does not support async")

# class AddBudgetItemTool(BaseTool):
#     name: str = "add_budget_item"
#     description: str = "Adds an expense to the most recent budget. Input should be 'item_name,amount' format."
    
#     def _run(self, input_str: str) -> str:
#         try:
#             if ',' in input_str:
#                 item_name, amount_str = input_str.split(',', 1)
#                 item_name = item_name.strip()
#                 amount = float(amount_str.strip())
#             else:
#                 return "Please provide input in format: 'item_name,amount'"
            
#             budgets_dir = os.path.join(os.path.dirname(__file__), "..", "budgets")
#             if os.path.exists(budgets_dir):
#                 budget_files = [f for f in os.listdir(budgets_dir) if f.endswith(".json")]
#                 if budget_files:
#                     budget_files.sort(
#                         key=lambda f: os.path.getmtime(os.path.join(budgets_dir, f)),
#                         reverse=True,
#                     )
#                     latest_budget = budget_files[0]
                    
#                     with open(os.path.join(budgets_dir, latest_budget), "r", encoding="utf-8") as f:
#                         budget_data = json.load(f)
                    
#                     new_item = {
#                         "id": len(budget_data["items"]) + 1,
#                         "name": item_name,
#                         "amount": amount,
#                         "created": datetime.now().isoformat(),
#                     }
#                     budget_data["items"].append(new_item)
                    
#                     update_budget(latest_budget, budget_data["items"])
#                     return f"Added '{item_name}' (${amount:.2f}) to your budget!"
#                 else:
#                     return "No budgets found. Create one first!"
#             else:
#                 return "No budgets found. Create one first!"
#         except Exception as e:
#             return f"Error adding budget item: {str(e)}"
    
#     def _arun(self, input_str: str):
#         raise NotImplementedError("This tool does not support async")



# class SaveTravelPlanTool(BaseTool):
#     name: str = "save_travel_plan"
#     description: str = "Saves a travel plan for a destination. Input should be 'destination,content' format."
    
#     def _run(self, input_str: str) -> str:
#         try:
#             if ',' in input_str:
#                 destination, content = input_str.split(',', 1)
#                 destination = destination.strip()
#                 content = content.strip()
#             else:
#                 return "Please provide input in format: 'destination,content'"
            
#             filename = save_travel_plan(destination, content)
#             return f"Saved travel plan for {destination}!"
#         except Exception as e:
#             return f"Error saving travel plan: {str(e)}"
    
#     def _arun(self, input_str: str):
#         raise NotImplementedError("This tool does not support async")
