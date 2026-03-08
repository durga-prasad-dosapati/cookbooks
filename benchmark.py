import csv
import os
from ollama_client import OllamaClient
from optimizer import OptimizationEngine
from monitor import ResourceMonitor

class Benchmark:
    def __init__(self):
        self.client = OllamaClient()
        self.optimizer = OptimizationEngine()
        self.results_path = "logs/results.csv"
        
        # Ensure log dir exists
        os.makedirs("logs", exist_ok=True)
        if not os.path.exists(self.results_path):
            with open(self.results_path, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Model", "NumCtx", "NumPredict", "Latency(s)", "CPU(%)", "RAM(%)", "Tokens/sec", "EfficiencyScore", "Mode"])

    def run_inference(self, prompt, use_optimizer=True, static_model="phi3:mini"):
        """Runs the LLM inference and records performance metrics."""
        prompt_length = len(prompt.split())
        
        if use_optimizer:
            params = self.optimizer.optimize_parameters(prompt_length)
            model = params["model"]
            num_ctx = params["num_ctx"]
            num_predict = params["num_predict"]
            temperature = params["temperature"]
            cpu_usage = params["cpu_usage_at_time"]
            ram_usage = params["ram_usage_at_time"]
            mode = "Optimized"
        else:
            # Traditional greedy approach (Unoptimized)
            model = static_model
            num_ctx = 4096
            num_predict = 1000 
            temperature = 0.8
            # Measure resources anyway
            cpu_usage = ResourceMonitor.get_cpu_usage()
            ram_usage = ResourceMonitor.get_ram_usage()
            mode = "Unoptimized"
            
        print(f"Running query... Mode: {mode}, Model: {model}, Ctx: {num_ctx}")
        result = self.client.generate(model, prompt, num_ctx, num_predict, temperature)
        
        if result["success"]:
            latency = result["latency"]
            tokens = result["eval_count"]
            
            # Metric calculation
            tokens_per_sec = tokens / latency if latency > 0 else 0
            # Efficiency = Tokens generated relative to CPU usage
            efficiency = tokens / (cpu_usage + 1) # +1 avoids DivByZero
            
            print(f"Result: {latency:.2f}s | {cpu_usage}% CPU | {tokens_per_sec:.2f} tok/s | Eff: {efficiency:.2f}\n")
            
            # Log results
            with open(self.results_path, "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    model, 
                    num_ctx, 
                    num_predict, 
                    round(latency, 2), 
                    cpu_usage, 
                    ram_usage, 
                    round(tokens_per_sec, 2), 
                    round(efficiency, 2), 
                    mode
                ])
        else:
            print(f"Error during inference: {result.get('error')}")
