import os
import json
import pandas as pd

def load_mapping(mapping_file):
    with open(mapping_file, "r") as f:
        mapping = json.load(f)
    return mapping

def load_ground_truth(ground_truth_file):
    ground_truth_data = {}
    with open(ground_truth_file, "r") as f:
        for line in f:
            parts = line.strip().rsplit(" ", 1)
            if len(parts) == 2:
                transcription, file_id = parts
                ground_truth_data[file_id] = transcription
    return ground_truth_data

def compare_with_ground_truth(mapping, ground_truth_data):
    results = []
    for gender, files in mapping.items():
        for file_info in files:
            audio_file = file_info["file"]
            file_id = audio_file.replace(".wav", "")
            start_time = file_info["start"]
            end_time = file_info["end"]

            transcription = ground_truth_data.get(file_id, "Not found")

            results.append({
                "audio_file": audio_file,
                "start_time": start_time,
                "end_time": end_time,
                "ground_truth": transcription
            })

    return pd.DataFrame(results)

if __name__ == "__main__":
    # Define the paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    output_folder = os.path.join(base_dir, "data/processed")
    ground_truth_file = os.path.join(base_dir, "data/ground_truth/ground_truth.txt")

    # Load the mapping
    mapping_file = os.path.join(output_folder, "mapping.json")
    mapping = load_mapping(mapping_file)

    # Load the ground truth data
    ground_truth_data = load_ground_truth(ground_truth_file)

    # Compare with ground truth
    comparison_results = compare_with_ground_truth(mapping, ground_truth_data)

    # Save results to a CSV file
    comparison_results.to_csv(os.path.join(output_folder, "comparison_results.csv"), index=False)

    print("Comparison completed. Results saved to comparison_results.csv")
