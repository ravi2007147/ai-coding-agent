# test_smart_assistant.py
from smart_assistant import SmartAssistant

assistant = SmartAssistant()

queries = [
    "Which framework is this project using?",
    "Add a new login component in React",
    "Generate a Flask API backend"
]

for q in queries:
    print("\n💬 User:", q)
    response = assistant.handle_query(q)
    print("🤖 Assistant:", response)
