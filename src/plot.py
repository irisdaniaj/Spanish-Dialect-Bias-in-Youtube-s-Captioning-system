import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Function to create and save bar plots
def create_and_save_barplot(data, x, y, hue, title, xlabel, ylabel, output_filename, color=None, palette=None, ylim=None):
    plt.figure(figsize=(10, 6))
    sns.barplot(x=x, y=y, hue=hue, data=data, color=color, palette=palette)

    # Customize the plot
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    # Set y-axis limits if provided
    if ylim is not None:
        plt.ylim(ylim)
        
    plt.xticks(rotation=30)
    plt.tight_layout()

    # Save the plot
    output_dir = '../results/final/plots'  # Directory to save the plot
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    output_file_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_file_path, dpi=300)  # Save the plot as a .png file with high resolution

    # Show the plot
    plt.show()

# Load and plot the overall_country.csv data
overall_country_csv = '../results/final/summary/overall_country.csv'
overall_country_data = pd.read_csv(overall_country_csv)

# Plot for WER with custom y-axis limit
create_and_save_barplot(
    data=overall_country_data,
    x='country',
    y='overall_wer',
    hue=None,
    title='Word Error Rate (WER) by Country',
    xlabel='Country',
    ylabel='Word Error Rate',
    output_filename='wer_by_country.png', 
    color="royalblue",
    ylim=(0, 0.30)  # Custom y-axis limit for WER
)

# Plot for CER with a different y-axis limit
create_and_save_barplot(
    data=overall_country_data,
    x='country',
    y='overall_cer',
    hue=None,
    title='Character Error Rate (CER) by Country',
    xlabel='Country',
    ylabel='Character Error Rate',
    output_filename='cer_by_country.png', 
    color="royalblue",
    ylim=(0, 0.15)  # Custom y-axis limit for CER
)

# Plot for Recall
create_and_save_barplot(
    data=overall_country_data,
    x='country',
    y='overall_recall',
    hue=None,
    title='Recall by Country',
    xlabel='Country',
    ylabel='Recall',
    output_filename='recall_by_country.png', 
    color="royalblue",
    ylim=(0, 1.0)  # Custom y-axis limit for Recall
)

# Load and reshape the overall_country_gender.csv data
overall_country_gender_csv = '../results/final/summary/overall_country_gender.csv'
overall_country_gender_data = pd.read_csv(overall_country_gender_csv)

# Melt the data to have 'country', 'gender', and the metrics columns
melted_data_wer = pd.melt(overall_country_gender_data, id_vars='country', value_vars=['wer_F', 'wer_M'], 
                          var_name='gender', value_name='wer')
melted_data_cer = pd.melt(overall_country_gender_data, id_vars='country', value_vars=['cer_F', 'cer_M'], 
                          var_name='gender', value_name='cer')
melted_data_recall = pd.melt(overall_country_gender_data, id_vars='country', value_vars=['recall_F', 'recall_M'], 
                             var_name='gender', value_name='recall')

# Map gender values
melted_data_wer['gender'] = melted_data_wer['gender'].map({'wer_F': 'Female', 'wer_M': 'Male'})
melted_data_cer['gender'] = melted_data_cer['gender'].map({'cer_F': 'Female', 'cer_M': 'Male'})
melted_data_recall['gender'] = melted_data_recall['gender'].map({'recall_F': 'Female', 'recall_M': 'Male'})

# Create bar plots for WER, CER, and Recall by country and gender
create_and_save_barplot(
    data=melted_data_wer,
    x='country',
    y='wer',
    hue='gender',
    title='Word Error Rate (WER) by Country and Gender',
    xlabel='Country',
    ylabel='Word Error Rate',
    output_filename='wer_by_country_and_gender.png', 
    palette=["mediumpurple", "orange"], 
    ylim=(0, 0.30)  # Custom y-axis limit for WER
)

create_and_save_barplot(
    data=melted_data_cer,
    x='country',
    y='cer',
    hue='gender',
    title='Character Error Rate (CER) by Country and Gender',
    xlabel='Country',
    ylabel='Character Error Rate',
    output_filename='cer_by_country_and_gender.png', 
    palette=["mediumpurple", "orange"], 
    ylim=(0, 0.20)  # Custom y-axis limit for CER
)

create_and_save_barplot(
    data=melted_data_recall,
    x='country',
    y='recall',
    hue='gender',
    title='Recall by Country and Gender',
    xlabel='Country',
    ylabel='Recall',
    output_filename='recall_by_country_and_gender.png', 
    palette= ["mediumpurple", "orange"], 
    ylim=(0, 1.0)  # Custom y-axis limit for Recall
)

# Load and plot the gender.csv data
gender_csv = '../results/final/summary/gender.csv'
gender_data = pd.read_csv(gender_csv)

# Plot for WER by Gender
create_and_save_barplot(
    data=gender_data,
    x='gender',
    y='wer',
    hue=None,
    title='Word Error Rate (WER) by Gender',
    xlabel='Gender',
    ylabel='Word Error Rate',
    output_filename='wer_by_gender.png', 
    palette=["mediumpurple", "orange"], 
    ylim=(0, 0.30)  # Custom y-axis limit for WER
)

# Plot for CER by Gender
create_and_save_barplot(
    data=gender_data,
    x='gender',
    y='cer',
    hue=None,
    title='Character Error Rate (CER) by Gender',
    xlabel='Gender',
    ylabel='Character Error Rate',
    output_filename='cer_by_gender.png', 
    palette=["mediumpurple", "orange"],  
    ylim=(0, 0.15)  # Custom y-axis limit for CER
)

# Plot for Recall by Gender
create_and_save_barplot(
    data=gender_data,
    x='gender',
    y='recall',
    hue=None,
    title='Recall by Gender',
    xlabel='Gender',
    ylabel='Recall',
    output_filename='recall_by_gender.png', 
    palette=["mediumpurple", "orange"], 
    ylim=(0, 1.0)  # Custom y-axis limit for Recall
)

# Load and plot the LATAM vs Spain data
latam_spain_csv = '../results/final/summary/spain_vs_LATAM.csv'
LATAM_spain_data = pd.read_csv(latam_spain_csv)

# Clean up any leading/trailing spaces in the columns
LATAM_spain_data.columns = LATAM_spain_data.columns.str.strip()
LATAM_spain_data['Country'] = LATAM_spain_data['Country'].str.strip()

# Plot for WER by Country (LATAM vs Spain)
create_and_save_barplot(
    data=LATAM_spain_data,
    x='Country',
    y='wer',
    hue=None,
    title='Word Error Rate (WER) by Country (LATAM vs Spain)',
    xlabel='Country',
    ylabel='Word Error Rate',
    output_filename='wer_LATAM_vs_Spain.png', 
    palette=["goldenrod", "firebrick"], 
    ylim=(0, 0.30)  # Custom y-axis limit for WER
)

# Plot for CER by Country (LATAM vs Spain)
create_and_save_barplot(
    data=LATAM_spain_data,
    x='Country',
    y='cer',
    hue=None,
    title='Character Error Rate (CER) by Country (LATAM vs Spain)',
    xlabel='Country',
    ylabel='Character Error Rate',
    output_filename='cer_LATAM_vs_Spain.png', 
    palette=["goldenrod", "firebrick"],
    ylim=(0, 0.15)  # Custom y-axis limit for CER
)

# Plot for Recall by Country (LATAM vs Spain)
create_and_save_barplot(
    data=LATAM_spain_data,
    x='Country',
    y='recall',
    hue=None,
    title='Recall by Country (LATAM vs Spain)',
    xlabel='Country',
    ylabel='Recall',
    output_filename='recall_LATAM_vs_Spain.png', 
    palette=["goldenrod", "firebrick"],
    ylim=(0, 1.0)  # Custom y-axis limit for Recall
)
