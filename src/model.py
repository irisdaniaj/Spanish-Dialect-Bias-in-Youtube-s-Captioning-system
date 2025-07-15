import pandas as pd
import statsmodels.formula.api as smf
import itertools
import os

# Define directories
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
data_dir = os.path.join(base_dir, "results/final/summary")  
data_path = os.path.join(data_dir, "audio_metrics.csv")

# Output directory
output_dir = os.path.join(base_dir, "results/final")
os.makedirs(output_dir, exist_ok=True)

# Output file to store model results
output_file = os.path.join(output_dir, "mixed_model_combinations_results.txt")

# Load the data
data = pd.read_csv(data_path)

# Extract unique speaker ID
data['speaker_id'] = data['filename'].str.extract(r'([a-z]{3}_\d{5})')
data = data.dropna(subset=['speaker_id'])
data['speaker_id'] = data['speaker_id'].astype('category')

# Define dependent variable and predictors
dependent_variable = "word_error_rate"
predictors = ["country", "gender", "pitch", "intensity"]

# Function to generate all possible predictor combinations
def generate_combinations(predictors):
    all_combinations = []
    for r in range(1, len(predictors) + 1):
        combinations = itertools.combinations(predictors, r)
        for combo in combinations:
            combo_list = list(combo)
            # Add interaction term if both 'pitch' and 'gender' are in the combination
            if "pitch" in combo_list and "gender" in combo_list:
                combo_list.append("pitch:gender")
            all_combinations.append(" + ".join(combo_list))
    return all_combinations

# Generate all predictor combinations
combinations = generate_combinations(predictors)

# Initialize results list
results_list = []

# Fit models for all combinations
with open(output_file, "w") as f:
    f.write("Mixed-Effects Model Results for All Predictor Combinations\n")
    f.write("=" * 80 + "\n")

    for idx, combo in enumerate(combinations, start=1):
        formula = f"{dependent_variable} ~ {combo}"
        print(f"Running model {idx}/{len(combinations)}: {formula}")
        try:
            model = smf.mixedlm(formula, data=data, groups=data["speaker_id"])
            result = model.fit(reml=False)  # Use ML for comparison
            aic = result.aic
            bic = result.bic
            summary = result.summary().as_text()
            
            # Write results to file
            f.write(f"Model {idx}: {formula}\n")
            f.write(f"AIC: {aic:.4f}, BIC: {bic:.4f}\n")
            f.write(summary)
            f.write("=" * 80 + "\n")
            
            # Save results for summary table
            results_list.append({
                "Model": formula,
                "AIC": aic,
                "BIC": bic
            })
        except Exception as e:
            print(f"Model {idx} failed: {e}")
            f.write(f"Model {idx} failed: {formula}\nError: {e}\n")
            f.write("=" * 80 + "\n")

# Create a summary table and save it
summary_df = pd.DataFrame(results_list)
summary_csv = os.path.join(output_dir, "mixed_model_combinations_summary.csv")
summary_df.to_csv(summary_csv, index=False)

print(f"Model results saved to: {output_file}")
print(f"Summary table saved to: {summary_csv}")
