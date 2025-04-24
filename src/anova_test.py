import pandas as pd
from scipy import stats

# Example data
data = {
    "country": ["Argentina", "Argentina", "Chile", "Chile", "Colombia", "Colombia", "Peru", "Peru", "Puerto_Rico", "Puerto_Rico", "Mexico", "Mexico", "Venezuela", "Venezuela"],
    "gender": ["F", "M", "F", "M", "F", "M", "F", "M", "F", "M", "F", "M", "F", "M"],
    "wer": [0.2495, 0.234, 0.2188, 0.2282, 0.2200, 0.2248, 0.2018, 0.2096, 0.1671, None, 0.1999, 0.2057, 0.2377, 0.2157],
    "cer": [0.0877, 0.0615, 0.0823, 0.0771, 0.0799, 0.0663, 0.0653, 0.0801, 0.0588, None, 0.1087, 0.1022, 0.1229, 0.0625],
    "recall": [0.8159, 0.8165, 0.8463, 0.8394, 0.8461, 0.8405, 0.8537, 0.8497, 0.8912, None, 0.9103, 0.8962, 0.8340, 0.8227]
}

df = pd.DataFrame(data)

# Drop rows with missing values (if any)
df_clean = df.dropna()

# Perform ANOVA for WER across countries
country_groups_wer = [df_clean[df_clean['country'] == country]['wer'] for country in df_clean['country'].unique()]
f_stat_wer, p_value_wer = stats.f_oneway(*country_groups_wer)

# Perform ANOVA for CER
country_groups_cer = [df_clean[df_clean['country'] == country]['cer'] for country in df_clean['country'].unique()]
f_stat_cer, p_value_cer = stats.f_oneway(*country_groups_cer)

# Perform ANOVA for Recall
country_groups_recall = [df_clean[df_clean['country'] == country]['recall'] for country in df_clean['country'].unique()]
f_stat_recall, p_value_recall = stats.f_oneway(*country_groups_recall)

# Store the results in a dictionary
anova_results = {
    'Metric': ['WER', 'CER', 'Recall'],
    'F-Statistic': [f_stat_wer, f_stat_cer, f_stat_recall],
    'P-Value': [p_value_wer, p_value_cer, p_value_recall]
}

# Convert the results to a pandas DataFrame
anova_df = pd.DataFrame(anova_results)

# Save the results to a CSV file
anova_df.to_csv('../results/final/summary/anova_results.csv', index=False)

# Print a message to confirm the results have been saved
print(f"ANOVA results have been saved to 'anova_results.csv' in the 'results/final/summary' directory.")
