# project_manager.py
import os
import json
from ollama_client import OllamaClient
from plan_refiner import PlanRefiner
import json

class ProjectManager:
    def __init__(self):
        self.client = OllamaClient()
        self.refiner=PlanRefiner(self.client)
        self.project_path = None
        self.file_samples = []
        self.dependencies = []

    def open_project(self, folder_path):
        if not os.path.isdir(folder_path):
            raise ValueError("Invalid folder path")
        self.project_path = folder_path
        self.index_project()

    def index_project(self, max_files=20, max_size_kb=150):
        """
        Scan the project directory to gather relevant code and configuration files.
        Includes dependency detection for better AI context.
        """
        self.file_samples = []
        self.dependencies = []

        # Extract dependencies first
        self.dependencies = self.extract_dependencies()

        # Define which folders to skip
        ignored_dirs = ["node_modules", ".git", "__pycache__", "venv", "env"]

        # Prioritize key config files
        priority_files = [
            "package.json",
            "requirements.txt",
            "setup.py",
            "pyproject.toml",
            "index.js",
            "main.py",
        ]

        for pf in priority_files:
            path = os.path.join(self.project_path, pf)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                self.file_samples.append((path, content))

        # Then collect source code samples
        for root, _, files in os.walk(self.project_path):
            # Skip ignored folders
            if any(ignored in root for ignored in ignored_dirs):
                continue

            for file in files:
                if file.endswith((".py", ".js", ".ts", ".html", ".css", ".jsx", ".tsx")):
                    file_path = os.path.join(root, file)
                    size_kb = os.path.getsize(file_path) / 1024
                    if size_kb < max_size_kb:
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                code = f.read()
                            self.file_samples.append((file_path, code))
                        except Exception:
                            continue

                if len(self.file_samples) >= max_files:
                    break

        # Fallback: if too few files, sample a few more to guarantee context
        if len(self.file_samples) < 5:
            for root, _, files in os.walk(self.project_path):
                if any(ignored in root for ignored in ignored_dirs):
                    continue
                for file in files:
                    if file.endswith((".py", ".js", ".ts", ".jsx", ".tsx")):
                        path = os.path.join(root, file)
                        try:
                            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                                code = f.read()
                            self.file_samples.append((path, code[:2000]))
                        except Exception:
                            continue
                    if len(self.file_samples) >= 10:
                        break

    def extract_dependencies(self):
        """
        Reads known dependency files (package.json, requirements.txt, setup.py)
        and returns a list of dependency names.
        """
        deps = []
        pkg = os.path.join(self.project_path, "package.json")
        req = os.path.join(self.project_path, "requirements.txt")
        setup = os.path.join(self.project_path, "setup.py")

        # Extract from package.json
        if os.path.exists(pkg):
            try:
                with open(pkg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                deps += list(data.get("dependencies", {}).keys())
                deps += list(data.get("devDependencies", {}).keys())
            except Exception:
                pass

        # Extract from requirements.txt
        if os.path.exists(req):
            try:
                with open(req, "r", encoding="utf-8") as f:
                    deps += [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
            except Exception:
                pass

        # Extract from setup.py (very rough, string-based)
        if os.path.exists(setup):
            try:
                with open(setup, "r", encoding="utf-8") as f:
                    for line in f:
                        if "install_requires" in line or "'" in line or '"' in line:
                            deps.append(line.strip())
            except Exception:
                pass

        return deps

    def get_project_plan(self, user_query):
        planning_prompt = f"""
You are an expert project setup assistant.
Understand the user's request and return a structured JSON plan describing what actions to perform.

User request:
"{user_query}"

Follow these formatting rules strictly:

1. The JSON must be a single object (no outer keys like "plan" or "steps").

2. Use **exactly** these top-level keys:
   {{
     "base_directory": "string",                 // folder name where files and commands will be executed.
                                                 // If the user explicitly mentions a folder, use that name.
                                                 // Otherwise, automatically generate a short, meaningful name
                                                 // based on the project type (e.g., "react-project", "flask-api").
     "actions": [
       {{
         "action": "string",                     // one of ["analyze", "write_files", "run_command", "explain"]
         "command": "string (if applicable)",    // required if action = "run_command"
         "files": [                              // required if action = "write_files", else []
            {{
              "path": "string (relative to base_directory)",
              "language": "string",
              "content": "string"
            }}
         ],
         "message": "string"                     // short explanation of this action
       }}
     ]
   }}

3. Always return all keys, even if arrays are empty (e.g., "files": []).

4. Do not include markdown, code fences, or text outside JSON.

5. If unsure about the folder name, make a reasonable assumption based on the project type.

6. All file paths must be relative to the "base_directory".

7. Output valid JSON that can be parsed directly.

Return only JSON, no markdown or commentary.
"""


        json_plan = self.client.generate(planning_prompt)
        # print(json_plan)
        # return
        
        #sometime model return empty content and files so we need refiner
        response=self.refiner.refine_plan(user_query, json_plan)
        return response