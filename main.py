# test_intent_detection.py
from analyzer import ProjectAnalyzer
from intent_detector import IntentDetector

pa = ProjectAnalyzer()
pa.open_project("/Users/smayra/email-sync/")
query="Create me a React project with TailwindCSS."
result = pa.ask(query)
print(result)