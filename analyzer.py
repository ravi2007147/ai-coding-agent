# analyzer.py
from ollama_client import OllamaClient
from project_manager import ProjectManager
from intent_detector import IntentDetector

class ProjectAnalyzer:
    def __init__(self):
        self.client = OllamaClient()
        self.project = ProjectManager()
        self.detector = IntentDetector()
        self.currentQuery=""

    def open_project(self, path):
        self.project.open_project(path)
        
    def ask(self,query):
        self.currentQuery=query
        intent, score= self.detector.detect_intent(query)
        return self.take_action(intent)
    
    def take_action(self,intent):
        if intent=="generative":
           return self.project.get_project_plan(self.currentQuery)
        

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



