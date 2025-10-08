# test_hierarchical_intent_detector.py
from hierarchical_intent_detector import HierarchicalIntentDetector

def main():
    detector = HierarchicalIntentDetector()

    queries = [
        "Which framework is this project using?",
        "Find API routes from this backend",
        "Create me a React project with TailwindCSS",
        "Generate a Flask API backend",
        "Optimize this code for speed",
        "What database ORM does this project use?",
        "Add a new login component in React"
    ]

    print("\n🧠 Running Intent Detection Tests...\n")

    for q in queries:
        main_intent, sub_intent, score = detector.detect_intent(q)
        print(f"Query: {q}")
        print(f" → Main: {main_intent}, Sub: {sub_intent}, Confidence: {score}\n")

if __name__ == "__main__":
    main()
