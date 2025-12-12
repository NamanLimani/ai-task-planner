import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_comparison():
    # Load data
    try:
        df = pd.read_csv("data/evaluation_results.csv")
    except:
        print("Error: Run evaluate_models.py first!")
        return

    # Group data
    summary = df.groupby("agent")[["success_rate", "energy_left"]].mean().reset_index()
    
    # Setup Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 1. Success Rate
    sns.barplot(data=summary, x="agent", y="success_rate", ax=axes[0], palette="viridis")
    axes[0].set_title("Task Completion Rate (Higher is Better)")
    axes[0].set_ylim(0, 1.0)
    for p in axes[0].patches:
        axes[0].annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                         ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points')

    # 2. Energy Conservation
    sns.barplot(data=summary, x="agent", y="energy_left", ax=axes[1], palette="magma")
    axes[1].set_title("Average Remaining Energy (Higher = Less Burnout)")
    
    plt.tight_layout()
    plt.savefig("data/comparison_plot.png")
    print("Plot saved to data/comparison_plot.png")

if __name__ == "__main__":
    plot_comparison()