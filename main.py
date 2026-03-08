from benchmark import Benchmark

def main():
    print("Optimizing LLM Inference for Intel Devices")
    benchmark = Benchmark()
    
    prompts = [
        "Explain quantum computing in 5 sentences.",
        "Write a python script to reverse a linked list.",
        "Summarize the plot of the Matrix."
    ]
    
    print("\n--- Running Unoptimized Baseline ---")
    for prompt in prompts:
        # We explicitly show unoptimized behaviour on a typical model
        benchmark.run_inference(prompt, use_optimizer=False, static_model="llama3.2:8b")
        
    print("\n--- Running Optimized Edge Engine ---")
    for prompt in prompts:
        benchmark.run_inference(prompt, use_optimizer=True)
        
    print("\nExperiments complete! Check logs/results.csv")
    print("Run `python graphs/plot_results.py` to visualize the benchmarks.")

if __name__ == "__main__":
    main()
