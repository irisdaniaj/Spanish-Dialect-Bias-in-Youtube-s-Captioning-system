import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define the path to the data files and plot save directory
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
aggregated_csv_path = os.path.join(base_dir, "results/final/summary/audio_metrics.csv")
country_csv_path = os.path.join(base_dir, "results/final/summary/audio_metrics_aggregated_by_country.csv")
gender_csv_path = os.path.join(base_dir, "results/final/summary/audio_metrics_aggregated_by_gender.csv")
plot_save_directory = os.path.join(base_dir, "results/final/plots")
os.makedirs(plot_save_directory, exist_ok=True)

# Load the data
data = pd.read_csv(aggregated_csv_path)
country_data = pd.read_csv(country_csv_path)
gender_data = pd.read_csv(gender_csv_path)

# Set plot style
sns.set(style="whitegrid")

# Metrics to plot
metrics = ["avg_pitch", "avg_intensity"]
metric_names = {"avg_pitch": "Average Pitch", "avg_intensity": "Average Intensity"}

# Plot data from main file (by country and gender)
for metric in metrics:
    plt.figure(figsize=(10, 6))
    # Sort the data by country to ensure alphabetical order
    sorted_data = data.sort_values(by="country")
    
    sns.barplot(
        data=sorted_data, 
        x="country", 
        y=metric, 
        hue="gender", 
        ci="sd", 
        palette=["orange", "mediumpurple"]
    )
    plt.title(f"{metric_names[metric]} by Country and Gender")
    plt.xlabel("Country")
    plt.ylabel(metric_names[metric])
    plt.xticks(rotation=45)
    plt.legend(title="Gender")
    plt.tight_layout()
    
    # Save the plot
    plot_filename = f"{metric}_by_country_and_gender.png"
    plt.savefig(os.path.join(plot_save_directory, plot_filename), dpi=300)
    plt.close()


# Plot data from country aggregated file
for metric in metrics:
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=country_data, 
        x="country", 
        y=metric, 
        ci="sd", 
        color="royalblue"
    )
    plt.title(f"{metric_names[metric]} by Country")
    plt.xlabel("Country")
    plt.ylabel(metric_names[metric])
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plot_filename = f"{metric}_by_country.png"
    plt.savefig(os.path.join(plot_save_directory, plot_filename), dpi=300)
    plt.close()

# Plot data from gender aggregated file
for metric in metrics:
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=gender_data, 
        x="gender", 
        y=metric, 
        ci="sd", 
        palette=["mediumpurple", "orange"]
    )
    plt.title(f"{metric_names[metric]} by Gender")
    plt.xlabel("Gender")
    plt.ylabel(metric_names[metric])
    plt.tight_layout()
    
    # Save the plot
    plot_filename = f"{metric}_by_gender.png"
    plt.savefig(os.path.join(plot_save_directory, plot_filename), dpi=300)
    plt.close()

print("Plots for avg_pitch and avg_intensity by country, gender, and both have been generated and saved in the 'results/final/plots' directory.")
