import json
from monitor import ResourceMonitor

class OptimizationEngine:
    def __init__(self, config_path="configs/model_config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
    def optimize_parameters(self, prompt_length):
        """Dynamically adjusts LLM parameters based on current system resources."""
        cpu_usage = ResourceMonitor.get_cpu_usage()
        ram_usage = ResourceMonitor.get_ram_usage()
        
        # Default starting point (Optimized for Edge devices)
        model = "phi3:mini"
        num_ctx = 512
        num_predict = 200
        temperature = 0.3
        
        # Adaptive Parameter Tuning based on real-time metrics
        if cpu_usage > self.config["optimization_thresholds"]["high_cpu_usage"]:
            # Extreme optimization mode: minimize context and limits
            num_ctx = 256
            num_predict = 100
            temperature = 0.1
            
        elif ram_usage > self.config["optimization_thresholds"]["high_ram_usage"]:
            # Reduce context window heavily to save memory
            num_ctx = 256
            model = "phi3:mini"
            
        else:
            # If we have resources, maybe we can bump context slightly based on prompt length
            if prompt_length > 300:
                num_ctx = 1024
            if prompt_length > 1000 and cpu_usage < 50:
                # Upgrade to larger model if resources are plentiful
                model = "llama3.2:8b" 
                num_ctx = 2048
                num_predict = 500
        
        return {
            "model": model,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
            "temperature": temperature,
            "cpu_usage_at_time": cpu_usage,
            "ram_usage_at_time": ram_usage
        }
