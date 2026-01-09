
import os
import json
from datetime import datetime
import logging

def save_travel_plan(destination, content):
    """Save travel plan to a file"""
    travel_plans_dir = os.path.join(os.path.dirname(__file__), "..", "travel_plans")
    os.makedirs(travel_plans_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{destination.lower().replace(' ', '_')}_{timestamp}.txt"
    filepath = os.path.join(travel_plans_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Travel Plan for {destination}\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        f.write(content)

    return filename
