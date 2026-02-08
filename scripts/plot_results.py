# scripts/plot_results.py
import matplotlib.pyplot as plt
import os

def plot_speedup():
    # YOUR ACTUAL DATA (Update these numbers based on your specific run)
    labels = ['Cold Start (Standard)', 'AI Prefetch (Ours)']
    times = [0.0189, 0.0103]  # Seconds
    colors = ['#ff9999', '#66b3ff'] # Red for slow, Blue for fast

    # Calculate percentage for the label
    speedup = ((times[0] - times[1]) / times[0]) * 100

    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, times, color=colors, edgecolor='black')

    # Add title and labels
    plt.ylabel('Launch Time (Seconds)', fontsize=12)
    plt.title(f'Performance Comparison: {speedup:.2f}% Speedup', fontsize=14, fontweight='bold')
    
    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.0005, f'{yval}s', 
                 ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Save the chart
    output_file = "results_chart.png"
    plt.savefig(output_file, dpi=300)
    print(f"[*] Graph saved as {output_file}")
    print("[*] You can open this image to show your professor!")

if __name__ == "__main__":
    plot_speedup()
