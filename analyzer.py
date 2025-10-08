# analyzer.py
import os
import pickle
import hashlib
from sentence_transformers import SentenceTransformer

from ollama_client import OllamaClient
from project_manager import ProjectManager
from intent_detector import IntentDetector


class ProjectAnalyzer:
    def __init__(self):
        self.client = OllamaClient()
        self.project = ProjectManager()
        self.detector = IntentDetector()
        self.currentQuery = ""
        self.embeddings_cache = {}
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.cache_file = "embeddings.pkl"

    # ---------------------------
    # 🧠 Main Project Open Method
    # ---------------------------
    def open_project(self, path):
        """Open a project and automatically build or update embeddings."""
        self.project.open_project(path)
        print(f"📂 Project opened: {path}")

        # Build or update the semantic index
        self._build_project_embeddings(path)

    # --------------------------------
    # ⚡ Build and Cache Embeddings
    # --------------------------------
    def _build_project_embeddings(self, project_path):
        """Build semantic embeddings for project files, with caching."""
        print("🔍 Building semantic index (this may take a moment)...")

        # Load existing embeddings cache (if available)
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "rb") as f:
                self.embeddings_cache = pickle.load(f)
        else:
            self.embeddings_cache = {}

        updated = False
        indexed_files = 0

        for root, _, files in os.walk(project_path):
            # Skip non-source directories
            if any(skip in root for skip in ["node_modules", "dist", ".next", ".git", "__pycache__"]):
                continue

            for f in files:
                if f.endswith((".js", ".jsx", ".ts", ".tsx", ".py")):
                    path = os.path.join(root, f)
                    file_hash = self._hash_file(path)

                    if path not in self.embeddings_cache or self.embeddings_cache[path]["hash"] != file_hash:
                        with open(path, "r", encoding="utf-8", errors="ignore") as file:
                            text = file.read()

                        emb = self.embedding_model.encode(text)
                        self.embeddings_cache[path] = {"hash": file_hash, "embedding": emb}
                        updated = True
                        indexed_files += 1
                        print(f"🧩 Indexed: {path}")

        # Save updated cache
        if updated:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.embeddings_cache, f)
            print(f"✅ Semantic index updated ({indexed_files} new/changed files).")
        else:
            print("⚡ Embeddings are already up to date.")

        # Attach to project object
        self.project.embedding_index = self.embeddings_cache
        
    def update_embeddings(self, changed_files=None):
        """
        Update embeddings for newly created or modified files.
        If `changed_files` is None, it re-scans the entire project (incrementally).
        """
        if not hasattr(self, "embeddings_cache"):
            print("⚠️ Embedding cache not initialized. Run open_project() first.")
            return

        start_time = time.time()
        updated = 0

        if changed_files is None:
            # fallback: re-scan all project files (incremental)
            changed_files = []
            for path in self.embeddings_cache.keys():
                if not os.path.exists(path):
                    continue  # skip deleted files
                changed_files.append(path)

        for path in changed_files:
            if not os.path.exists(path):
                continue

            file_hash = self._hash_file(path)
            cached = self.embeddings_cache.get(path)

            if not cached or cached["hash"] != file_hash:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                    emb = self.embedding_model.encode(text)
                    self.embeddings_cache[path] = {"hash": file_hash, "embedding": emb}
                    updated += 1
                    print(f"🔁 Re-embedded: {path}")
                except Exception as e:
                    print(f"⚠️ Skipped {path}: {e}")

        # Save updates if anything changed
        if updated > 0:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.embeddings_cache, f)
            print(f"✅ Updated embeddings for {updated} files (took {time.time() - start_time:.2f}s)")
        else:
            print("⚡ No embedding updates required — everything is current.")

    def _hash_file(self, path):
        """Compute a fast hash for file change detection."""
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    # --------------------------------
    # 🧠 Ask / Intent Handling
    # --------------------------------
    def ask(self, query):
        self.currentQuery = query
        intent, score = self.detector.detect_intent(query)
        print(f"🧠 Detected intent: {intent} (confidence: {score})")
        return self.take_action(intent)

    def take_action(self, intent):
        if intent == "generative":
            return self.project.get_project_plan(self.currentQuery)
        elif intent == "analytics":
            return self.analyze_technologies("framework")
        else:
            return "⚠️ Intent not recognized."

    # --------------------------------
    # 🧩 Project Analysis (Framework/API/DB)
    # --------------------------------
    def analyze_technologies(self, analysis_type="framework"):
        """
        Analyze project files and dependencies using specialized prompts
        depending on the requested analysis type.
        analysis_type: one of ['framework', 'api', 'database']
        """

        # Prepare code context
        code_snippets = "\n\n".join(
            f"File: {path}\n{code[:800]}" for path, code in self.project.file_samples
        )

        deps = ", ".join(self.project.dependencies)
        dep_text = f"\nDetected dependencies: {deps}\n" if deps else ""

        # --- Specialized prompt templates ---
        PROMPTS = {
            "framework": """
    You are an expert software stack analyst.
    Analyze the provided project code and dependencies.
    Identify what frameworks, libraries, tools, technologies, and external integrations are used.

    Provide a clear structured summary:

    - Backend framework:
    - Frontend framework:
    - Database or APIs:
    - Payment gateways or integrations:
    - Build tools:
    - Programming language:

    Focus strictly on what is evident from code and dependency names.
    Do NOT explain what each technology does.
    """,

            "api": """
    You are an API discovery assistant.
    From the following project code and dependencies, identify all API endpoints,
    routes, and their HTTP methods.

    Return your findings as a structured list in this format:
    - [METHOD] /path
    - [METHOD] /path/:param
    If possible, include the framework or router library (e.g., ExpressJS, Flask, FastAPI, etc.).
    """,

            "database": """
    You are a backend database analysis assistant.
    Analyze the provided code and dependencies to determine what databases or ORMs
    the project uses (e.g., MySQL, PostgreSQL, MongoDB, Prisma, SQLAlchemy).

    Return results like:
    - Database(s) used:
    - ORM or driver libraries:
    - Connection indicators:
    Focus strictly on concrete evidence from imports, configs, or package names.
    """
        }

        # --- Select appropriate prompt template ---
        prompt_template = PROMPTS.get(analysis_type, PROMPTS["framework"])

        # --- Build final prompt for model ---
        final_prompt = f"""
{prompt_template}

{dep_text}

Code samples:
{code_snippets}
"""

        # --- Send the prompt to Ollama model ---
        return self.client.generate(final_prompt)
