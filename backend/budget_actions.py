import os
import json
from datetime import datetime
import logging

def handle_adding_budget(user_message, response):
    logging.info("Handling adding budget item...")
    # Find the most recent budget
    budgets_dir = os.path.join(os.path.dirname(__file__), "..", "budgets")
    if os.path.exists(budgets_dir):
        budget_files = [f for f in os.listdir(budgets_dir) if f.endswith(".json")]
        if budget_files:
            # Get most recent budget
            budget_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(budgets_dir, f)),
                reverse=True,
            )
            latest_budget = budget_files[0]

            # Load the budget
            with open(
                os.path.join(budgets_dir, latest_budget), "r", encoding="utf-8"
            ) as f:
                budget_data = json.load(f)

            # Extract item and amount from message
            import re

            # Look for patterns like "add hotel $120" or "add food 50"
            amount_patterns = [
                r"add\s+(.+?)\s+\$([0-9]+(?:\.[0-9]{2})?)\s+to",
                r"add\s+(.+?)\s+([0-9]+(?:\.[0-9]{2})?)\s+to",
                r"add\s+(.+?)\s+\$([0-9]+(?:\.[0-9]{2})?)",
                r"add\s+(.+?)\s+([0-9]+(?:\.[0-9]{2})?)",
            ]

            item_name = None
            amount = None

            for pattern in amount_patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    item_name = match.group(1).strip()
                    amount = float(match.group(2))
                    break

            if item_name and amount is not None:
                # Add new budget item
                new_item = {
                    "id": len(budget_data["items"]) + 1,
                    "name": item_name,
                    "amount": amount,
                    "created": datetime.now().isoformat(),
                }
                budget_data["items"].append(new_item)

                # Update the file
                update_budget(latest_budget, budget_data["items"])
                response += (
                    f"\n\nI've added '{item_name}' (${amount:.2f}) to your budget!"
                )
            else:
                response += "\n\nI couldn't understand the budget item format. Try something like 'add hotel $120 to my budget'."
        else:
            response += "\n\nYou don't have any budget lists yet. Create one first by saying 'create a new budget'."
    return response



def create_new_budget(title, items):
    """Save budget to a file"""

    logging.info("Handling adding budget item...")

    budgets_dir = os.path.join(os.path.dirname(__file__), "..", "budgets")
    os.makedirs(budgets_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title.lower().replace(' ', '_')}_{timestamp}.json"
    filepath = os.path.join(budgets_dir, filename)

    budget_data = {
        "title": title,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "items": items,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(budget_data, f, indent=2, ensure_ascii=False)

    return filename


def update_budget(filename, items):
    """Update an existing budget"""
    budgets_dir = os.path.join(os.path.dirname(__file__), "..", "budgets")
    filepath = os.path.join(budgets_dir, filename)

    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding="utf-8") as f:
        budget_data = json.load(f)

    budget_data["items"] = items
    budget_data["updated"] = datetime.now().isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(budget_data, f, indent=2, ensure_ascii=False)

    return filename