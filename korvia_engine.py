from openai import OpenAI
import os, json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class KorviaEngine:
    def __init__(self, user="krish", personality="Calm, smart, and adaptive"):
        self.user = user
        self.personality = personality
        self.memory_file = f"memory_{user}.json"
        self.memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_memory(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4)

    def think(self, user_input):
        context = "\n".join([f"{m['role']}: {m['content']}" for m in self.memory[-6:]])
        messages = [
            {"role": "system", "content": f"You are Korvia AI, a {self.personality} assistant."},
            {"role": "system", "content": f"Recent memory:\n{context}"},
            {"role": "user", "content": user_input}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        reply = response.choices[0].message.content
        self.memory.append({"role": "user", "content": user_input})
        self.memory.append({"role": "assistant", "content": reply})
        self._save_memory()
        return reply
