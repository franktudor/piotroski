import os
import requests
from typing import List, Dict, Any

class OllamaLLM:
    def __init__(self, model: str = None, host: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
        self.host  = host  or os.getenv("OLLAMA_HOST",  "http://localhost:11434")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.host}{path}"
        r = requests.post(url, json=payload, timeout=600)
        if r.status_code >= 400:
            raise requests.HTTPError(f"{r.status_code} {r.reason} for {url}\n{r.text}", response=r)
        return r.json()

    def call(self, messages: List[Dict[str, str]], **gen_options) -> Dict[str, str]:
        prompt = "\n".join(m.get("content", "") for m in messages if m.get("content"))
        prompt = prompt.encode("utf-8", "replace").decode("utf-8")
        payload = {"model": self.model, "prompt": prompt, "stream": False, "options": gen_options or {}}
        data = self._post("/api/generate", payload)
        return {"content": data.get("response", "")}
