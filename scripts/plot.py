import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Function to create and save bar plots
def create_and_save_barplot(data, x, y, hue, title, xlabel, ylabel, output_filename, color=None, palette=None):
    plt.figure(figsize=(10, 6))
    sns.barplot(x=x, y=y, hue=hue, data=data, color= color, palette=palette)

    # Customize the plot
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ylim(0.15, 0.30)  # Adjust this range based on your data
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
create_and_save_barplot(
    data=overall_country_data,
    x='country',
    y='overall_wer',
    hue=None,
    title='Word Error Rate (WER) by Country',
    xlabel='Country',
    ylabel='Word Error Rate',
    output_filename='wer_by_country.png', 
    color="forestgreen"
)

# Load and reshape the overall_country_gender.csv data
overall_country_gender_csv = '../results/final/summary/overall_country_gender.csv'
overall_country_gender_data = pd.read_csv(overall_country_gender_csv)

# Assuming the file has columns 'country', 'wer_F', and 'wer_M'
# Melt the data to have 'country', 'gender', and 'wer' columns
melted_data = pd.melt(overall_country_gender_data, id_vars='country', value_vars=['wer_F', 'wer_M'], 
                      var_name='gender', value_name='wer')
melted_data['gender'] = melted_data['gender'].map({'wer_F': 'Female', 'wer_M': 'Male'})

# Create the bar plot for WER by country and gender
create_and_save_barplot(
    data=melted_data,
    x='country',
    y='wer',
    hue='gender',
    title='Word Error Rate (WER) by Country and Gender',
    xlabel='Country',
    ylabel='Word Error Rate',
    output_filename='wer_by_country_and_gender.png', 
    palette= ["mediumpurple", "orange"]
)

# Load and plot the gender.csv data
gender_csv = '../results/final/summary/gender.csv'
gender_data = pd.read_csv(gender_csv)
create_and_save_barplot(
    data=gender_data,
    x='gender',
    y='wer',  # Adjust this based on the actual column name
    hue=None,
    title='Word Error Rate (WER) by Gender',
    xlabel='Gender',
    ylabel='Word Error Rate',
    output_filename='wer_by_gender.png', 
    palette= ["mediumpurple", "orange"]
)

# Load and plot the LATAM vs Spain data
latam_spain_csv = '../results/final/summary/spain_vs_LATAM.csv'
LATAM_spain_data = pd.read_csv(latam_spain_csv)

# Clean up any leading/trailing spaces in the columns
LATAM_spain_data.columns = LATAM_spain_data.columns.str.strip()
LATAM_spain_data['Country'] = LATAM_spain_data['Country'].str.strip()

create_and_save_barplot(
    data=LATAM_spain_data,
    x='Country',  # Ensure this is the correct column name
    y='wer',  # Ensure this is the correct column name
    hue=None,
    title='Word Error Rate (WER) by Country (LATAM vs Spain)',
    xlabel='Country',
    ylabel='Word Error Rate',
    output_filename='wer_LATAM_vs_Spain.png', 
    palette=["goldenrod", "firebrick"]
)
