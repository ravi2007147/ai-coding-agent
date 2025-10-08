# test_intent_detection.py
from intent_detector import IntentDetector

detector = IntentDetector()

queries = [
    "Which framework is this project using?",
    "Find what tech stack was used to build this app",
    "Create me a React project with TailwindCSS",
    "Generate a Flask API backend",
    "What database ORM does this use?"
]

detector = IntentDetector()
for q in queries:
    intent, score = detector.detect_intent(q)
    print(f"{q}\n→ Intent: {intent} (confidence: {score})\n")

