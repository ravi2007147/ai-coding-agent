# smart_assistant.py
from hierarchical_intent_detector import HierarchicalIntentDetector
from analyzer import ProjectAnalyzer

class SmartAssistant:
    def __init__(self):
        self.detector = HierarchicalIntentDetector()
        self.analyzer = ProjectAnalyzer()

    def handle_query(self, user_query: str):
        main_intent, sub_intent, confidence = self.detector.detect_intent(user_query)
        print(f"🧠 Detected Intent: {main_intent} → {sub_intent} (Confidence: {confidence})")

        if confidence < 0.5:
            return "⚠️ I'm not confident about the intent. Please rephrase your request."

        # Route based on intent
        if main_intent == "analytics":
            if sub_intent == "framework_analysis":
                return self.analyzer.analyze_technologies()
            elif sub_intent == "api_analysis":
                return self.analyzer.analyze_apis()
            elif sub_intent == "database_analysis":
                return self.analyzer.analyze_database()

        elif main_intent == "generative":
            if sub_intent == "project_creation":
                return self.analyzer.generate_project(user_query)
            elif sub_intent == "component_generation":
                return self.analyzer.generate_component(user_query)
            elif sub_intent == "code_refactor":
                return self.analyzer.refactor_code(user_query)

        return "❓ I couldn't match your request to a specific function."
