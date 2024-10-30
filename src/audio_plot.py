import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define the path to the aggregated data file and plot save directory
aggregated_csv_path = os.path.join("results", "final", "summary", "audio_metrics_aggregated_by_country_gender.csv")
plot_save_directory = os.path.join("results", "final", "plots")
os.makedirs(plot_save_directory, exist_ok=True)

# Load the data
data = pd.read_csv(aggregated_csv_path)

# Set plot style for better aesthetics
sns.set(style="whitegrid")

# List of metrics to plot
metrics = ["avg_pitch", "avg_intensity", "speech_rate"]

# Box plots
for metric in metrics:
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=data, x="gender", y=metric, hue="country")
    plt.title(f"Box Plot of {metric.replace('_', ' ').title()} by Gender and Country")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_save_directory, f"boxplot_{metric}.png"), dpi=300)
    plt.close()

# Violin plots
for metric in metrics:
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=data, x="gender", y=metric, hue="country", split=True)
    plt.title(f"Violin Plot of {metric.replace('_', ' ').title()} by Gender and Country")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_save_directory, f"violinplot_{metric}.png"), dpi=300)
    plt.close()

# Bar plots with error bars (mean and standard deviation)
for metric in metrics:
    plt.figure(figsize=(10, 6))
    sns.barplot(data=data, x="gender", y=metric, hue="country", ci="sd")
    plt.title(f"Bar Plot of {metric.replace('_', ' ').title()} by Gender and Country")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_save_directory, f"barplot_{metric}.png"), dpi=300)
    plt.close()

print("Plots have been generated and saved to the results/final/plots directory.")
