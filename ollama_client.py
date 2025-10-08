# ollama_client.py
import requests
import json

class OllamaClient:
    def __init__(self, model="deepseek-coder:6.7b", host="http://192.168.1.14:11434"):
        self.model = model
        self.host = host

    def generate(self, prompt, json_response=True):
        """Send a prompt to Ollama and return clean structured response if it's JSON."""
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
        )

        try:
            data = response.json()
        except Exception as e:
            print("❌ Invalid response from Ollama:", e)
            return response.text.strip()

        text = data.get("response", "").strip()

        # 🧠 If expecting JSON, check if starts with ```json
        if json_response:
            if text.startswith("```json"):
                # Strip the markdown fences
                text = text.removeprefix("```json").strip()
                if text.endswith("```"):
                    text = text[: -3].strip()

                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    print("⚠️ Failed to parse fenced JSON:", e)
                    return text

            elif text.startswith("{") and text.endswith("}"):
                # Plain valid JSON without fences
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    print("⚠️ Failed to parse plain JSON:", e)
                    return text

        # fallback: return text if not JSON
        return text

