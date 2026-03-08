import requests
import time

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def generate(self, model, prompt, num_ctx, num_predict, temperature):
        """Sends a generation request to the local Ollama instance."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": num_ctx,
                "num_predict": num_predict,
                "temperature": temperature
            }
        }
        
        start_time = time.time()
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            end_time = time.time()
            
            return {
                "response": data.get("response", ""),
                "eval_count": data.get("eval_count", 0), # tokens generated
                "latency": end_time - start_time,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
