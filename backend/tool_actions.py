import os
import json
from datetime import datetime
import logging
from typing import List, Optional

def create_new_todo_list(title, items):
    """Save todo list to a file"""
    todo_lists_dir = os.path.join(os.path.dirname(__file__), "..", "documents/todo_lists")
    os.makedirs(todo_lists_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title.lower().replace(' ', '_')}_{timestamp}.json"
    filepath = os.path.join(todo_lists_dir, filename)

    # Convert string items to dictionary format
    formatted_items = []
    if items:
        for i, item_text in enumerate(items):
            formatted_items.append({
                "id": i + 1,
                "text": item_text,
                "completed": False,
                "created": datetime.now().isoformat(),
            })

    todo_data = {
        "title": title,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "items": formatted_items,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(todo_data, f, indent=2, ensure_ascii=False)

    return filename


def handle_adding_todo(items: List[str], filename: Optional[str] = None):
    logging.info("Handling adding todo items %s to %s", items, filename)
    # Find the most recent todo list
    todo_lists_dir = os.path.join(os.path.dirname(__file__), "..", "documents", "todo_lists")
    response = ""
    todo_file = None
    if os.path.exists(todo_lists_dir):
        todo_files = [f for f in os.listdir(todo_lists_dir) if f.endswith(".json")]
        if todo_files:
            if filename:
                # Use the specified filename
                if filename in todo_files:
                    todo_file = filename
                else:
                    response += f"\n\nCouldn't find todo list '{filename}'. Using the most recent one instead."
                    # Get most recent todo list
                    todo_files.sort(
                        key=lambda f: os.path.getmtime(os.path.join(todo_lists_dir, f)),
                        reverse=True,
                    )
                    todo_file = todo_files[0]
            else:
                # No filename provided, get most recent todo list
                todo_files.sort(
                    key=lambda f: os.path.getmtime(os.path.join(todo_lists_dir, f)),
                    reverse=True,
                )
                todo_file = todo_files[0]

            # Load the todo list (only if we have a valid todo_file)
            if todo_file:
                with open(
                    os.path.join(todo_lists_dir, todo_file), "r", encoding="utf-8"
                ) as f:
                    todo_data = json.load(f)

                # Check for duplicates and add items
                for item in items:
                    if any(existing_item["text"] == item for existing_item in todo_data["items"]
                    ):
                        response += f"\n\nThe item '{item}' is already in your todo list, so I didn't add it again."
                        continue
                    
                    # Add new item
                    new_item = {
                        "id": len(todo_data["items"]) + 1,
                        "text": item,
                        "completed": False,
                        "created": datetime.now().isoformat(),
                    }
                    todo_data["items"].append(new_item)

                # Update the file
                update_todo_list(todo_file, todo_data["items"])
                
                # Create a proper response message
                if len(items) == 1:
                    response += f"\n\nI've added '{items[0]}' to your todo list!"
                else:
                    items_str = "', '".join(items)
                    response += f"\n\nI've added '{items_str}' to your todo list!"
        else:
            response += "\n\nYou don't have any todo lists yet. Create one first by saying 'create a new todo list'."
    else:
        response += "\n\nYou don't have any todo lists yet. Create one first by saying 'create a new todo list'."
    
    return response


def update_todo_list(filename, items):
    """Update an existing todo list"""
    logging.info("Updating todo list with items... %s", items)
    todo_lists_dir = os.path.join(os.path.dirname(__file__), "..", "documents/todo_lists")
    filepath = os.path.join(todo_lists_dir, filename)

    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        todo_data = json.load(f)

    todo_data["items"] = items
    todo_data["updated"] = datetime.now().isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(todo_data, f, indent=2, ensure_ascii=False)

    return f"Todo list updated successfully with items {items}"