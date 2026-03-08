import pandas as pd
import matplotlib.pyplot as plt
import os

def render_plots():
    csv_path = "logs/results.csv"
    if not os.path.exists(csv_path):
        print("Results file not found. Run main.py first.")
        return
        
    df = pd.read_csv(csv_path)
    
    if df.empty:
         print("No data to plot.")
         return

    os.makedirs("graphs/outputs", exist_ok=True)
    
    # 1. Latency Comparison
    plt.figure(figsize=(10, 6))
    df.groupby("Mode")["Latency(s)"].mean().plot(kind="bar", color=["#4CAF50", "#F44336"])
    plt.title("Average Latency: Optimized vs Unoptimized")
    plt.ylabel("Seconds (Lower is better)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("graphs/outputs/latency_comparison.png")
    
    # 2. Tokens/sec Comparison
    plt.figure(figsize=(10, 6))
    df.groupby("Mode")["Tokens/sec"].mean().plot(kind="bar", color=["#4CAF50", "#F44336"])
    plt.title("Average Tokens/Sec: Optimized vs Unoptimized")
    plt.ylabel("Tokens/Sec (Higher is better)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("graphs/outputs/tokens_per_sec.png")
    
    # 3. CPU Efficiency
    plt.figure(figsize=(10, 6))
    df.groupby("Mode")["EfficiencyScore"].mean().plot(kind="bar", color=["#4CAF50", "#F44336"])
    plt.title("CPU Efficiency Score (Tokens per CPU %)")
    plt.ylabel("Score (Higher is better)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("graphs/outputs/cpu_efficiency.png")

    print(f"📊 Graphs successfully saved to 'graphs/outputs/'!")

if __name__ == "__main__":
    render_plots()
