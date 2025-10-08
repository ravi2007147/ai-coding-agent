# intent_detector.py (improved)
from sentence_transformers import SentenceTransformer, util
import torch

class IntentDetector:
    def __init__(self):
        # more semantically accurate embedding model
        self.model = SentenceTransformer("all-mpnet-base-v2")

        # few-shot examples for each intent
        self.intents = {
            "analytics": [
                "analyze existing project",
                "understand what technology or framework is used",
                "find what tech stack or backend this project uses",
                "detect libraries, dependencies, or frameworks",
                "which database, api, or language is used in this codebase"
            ],
            "generative": [
                "create a new project or application",
                "generate code or scaffold a project",
                "build a new API backend or frontend project",
                "set up a project using React, Flask, or Electron",
                "make or modify source code according to user request"
            ]
        }

        # pre-compute averaged embeddings
        self.intent_embeddings = {}
        for name, examples in self.intents.items():
            emb = [self.model.encode(e, convert_to_tensor=True) for e in examples]
            self.intent_embeddings[name] = torch.stack(emb).mean(dim=0)

    def detect_intent(self, query):
        query_emb = self.model.encode(query, convert_to_tensor=True)
        scores = {
            name: float(util.cos_sim(query_emb, emb))
            for name, emb in self.intent_embeddings.items()
        }
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]
        return best_intent, round(confidence, 3)
