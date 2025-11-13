from openai import OpenAI
from dotenv import load_dotenv
from korvia_memory import remember, load_memory
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("🤖 Korvia Terminal Chat — type 'exit' to quit\n")

user = "krish"
memory = load_memory()

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    remember(user, user_input)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are Korvia AI, a helpful and calm assistant."},
            {"role": "user", "content": user_input}
        ]
    )

    reply = response.choices[0].message.content
    print(f"Korvia: {reply}\n")
    remember("korvia", reply)
