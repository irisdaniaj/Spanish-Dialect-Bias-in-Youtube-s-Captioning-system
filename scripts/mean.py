import pandas as pd

# Data
data = {
    'country': ['argentinian', 'chilean', 'colombian', 'peruvian', 'puerto_rican', 'venezuelan'],
    'wer': [0.24174033986912008, 0.22348423276983095, 0.2223892082300718, 0.20572656421217062, 0.16705882352941176, 0.2267167049190497]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Calculate the average WER
average_wer = df['wer'].mean()

print(f"The average WER is: {average_wer}")
