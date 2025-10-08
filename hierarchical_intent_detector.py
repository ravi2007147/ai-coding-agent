# hierarchical_intent_detector.py
from sentence_transformers import SentenceTransformer, util
import torch

class HierarchicalIntentDetector:
    def __init__(self):
        self.model = SentenceTransformer("all-mpnet-base-v2")

        self.intent_hierarchy = {
            "analytics": {
                "framework_analysis": [
                    "which framework or tech stack is used",
                    "find frameworks, libraries or tools used",
                    "detect backend or frontend technologies",
                    "analyze programming language or framework"
                ],
                "api_analysis": [
                    "list all api endpoints or routes",
                    "find api urls, methods, or handlers",
                    "detect backend routes or http methods"
                ],
                "database_analysis": [
                    "find what database or orm is used",
                    "detect sql, mysql, mongodb, or sqlalchemy",
                    "which database technology is used"
                ]
            },
            "generative": {
                "project_creation": [
                    "create a new project or scaffold",
                    "generate a flask, react or electron app",
                    "build a new web or api project"
                ],
                "component_generation": [
                    "create a new ui component or frontend page",
                    "generate react component, form or modal",
                    "add new frontend feature or element"
                ],
                "code_refactor": [
                    "refactor existing code",
                    "optimize or rewrite code for better structure",
                    "clean up functions or files"
                ]
            }
        }

        # store precomputed embeddings
        self.embeddings = {}
        for main_intent, sub_intents in self.intent_hierarchy.items():
            for sub_intent, examples in sub_intents.items():
                emb = [self.model.encode(e, convert_to_tensor=True) for e in examples]
                self.embeddings[(main_intent, sub_intent)] = torch.stack(emb).mean(dim=0)

    def detect_intent(self, query):
        query_emb = self.model.encode(query, convert_to_tensor=True)
        scores = {
            key: float(util.cos_sim(query_emb, emb))
            for key, emb in self.embeddings.items()
        }

        # find best match
        best_key = max(scores, key=scores.get)
        main_intent, sub_intent = best_key
        confidence = round(scores[best_key], 3)
        return main_intent, sub_intent, confidence
