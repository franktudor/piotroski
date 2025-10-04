import os
import requests
from typing import List, Dict, Any

class LLMService:
    def __init__(self, model: str = None, host: str = None):
        self.model = model or os.getenv("MODEL_NAME", "llama3")
        self.host  = host  or os.getenv("OLLAMA_HOST",  "http://localhost:11434")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.host}{path}"
        try:
            r = requests.post(url, json=payload, timeout=20) # 2s LLM timeout + buffer
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            # Log the error, maybe add more robust error handling
            print(f"Error connecting to Ollama: {e}")
            raise

    def generate(self, prompt: str, **gen_options) -> str:
        """
        Generates a response from the LLM.
        """
        final_options = {"temperature": 0.2, "max_tokens": 256}
        final_options.update(gen_options)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": final_options
        }

        data = self._post("/api/generate", payload)
        return data.get("response", "").strip()

    def get_bio(self, profile_data: dict) -> str:
        """
        Generates a company biography using a specific prompt.
        """
        prompt_template = """
Write a neutral 80-word company bio for {ticker} using this structured data:
{name}, {exchange}, {industry}, {sector}.
Do not speculate. If data is missing, omit it. No adjectives. Return plain text only.
"""
        prompt = prompt_template.format(**profile_data)
        return self.generate(prompt)

    def get_cash_cow_summary(self, financial_data: dict) -> str:
        """
        Generates a cash cow summary using a specific prompt.
        """
        prompt_template = """
Summarize free-cash-flow strength for {ticker} using:
FCF {fcf}, FCF Yield {fcf_yield}%, OCF {ocf}, Capex {capex},
NI {ni}, Debt/Assets {lev}, Interest coverage {icov}.
Use terse bullets. No hype. No forward guidance.
"""
        prompt = prompt_template.format(**financial_data)
        return self.generate(prompt)