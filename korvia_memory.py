import json
import os

MEMORY_FILE = "korvia_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

def remember(user, message):
    memory = load_memory()
    memory[user] = memory.get(user, []) + [message]
    save_memory(memory)
