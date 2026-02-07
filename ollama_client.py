import requests
import json
import sys
import time

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="llama3", timeout=2000, retries=3):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.retries = retries

    def list_models(self):
        """Fetch list of available models from Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except Exception as e:
            print(f"\n❌ Error listing models: {e}", file=sys.stderr)
            return []

    def _request_with_retry(self, endpoint, payload):
        """Helper to handle requests with retries and exponential backoff."""
        for attempt in range(self.retries):
            try:
                response = requests.post(f"{self.base_url}{endpoint}", json=payload, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
                wait_time = (attempt + 1) * 2
                print(f"\n⚠️  Ollama connection issue (attempt {attempt+1}/{self.retries}): {e}. Retrying in {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
            except Exception as e:
                print(f"\n❌ Unexpected error calling Ollama: {e}", file=sys.stderr)
                break
        return {}

    def generate(self, prompt, temperature=0.7, stop=None):
        """Standard generation call."""
        options = {"temperature": temperature}
        if stop:
            options["stop"] = stop
            
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": options
        }

        result = self._request_with_retry("/api/generate", payload)
        return result.get("response", "").strip()

    def chat(self, messages, temperature=0.7):
        """Chat-based interface for more interactive sessions."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        result = self._request_with_retry("/api/chat", payload)
        return result.get("message", {}).get("content", "").strip() if result else ""
