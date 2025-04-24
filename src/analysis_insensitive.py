import os
import argparse
import pandas as pd
import json
from jiwer import wer, cer
from sklearn.metrics import recall_score
import numpy as np

#in this script case insenstive is the deafult 

def load_data(captions_file, transcription_file):
    if not os.path.exists(captions_file):
        return None, None
    if not os.path.exists(transcription_file):
        return None, None

    with open(captions_file, 'r') as cf:
        captions_data = json.load(cf)

    transcription_data = pd.read_csv(transcription_file, sep='\t', header=None, names=['filename', 'transcription'])

    return captions_data, transcription_data

def calculate_error_rates(captions_data, transcription_data, case_sensitive=True):
    results = []
    filenames_in_captions = {entry['filename'].replace('.wav', '') for entry in captions_data}
    filenames_in_transcriptions = set(transcription_data['filename'].values)

    common_filenames = filenames_in_captions.intersection(filenames_in_transcriptions)

    for entry in captions_data:
        filename = entry['filename'].replace('.wav', '')
        if filename in common_filenames:
            generated_caption = entry['captions']
            true_transcription = transcription_data[transcription_data['filename'] == filename]['transcription'].values[0]
            
            if not case_sensitive:
                generated_caption = generated_caption.lower()
                true_transcription = true_transcription.lower()
            
            word_error_rate = wer(true_transcription, generated_caption)
            character_error_rate = cer(true_transcription, generated_caption)
            recall = calculate_recall(true_transcription, generated_caption)
            
            results.append({
                'filename': filename,
                'generated_caption': generated_caption,
                'true_transcription': true_transcription,
                'word_error_rate': word_error_rate,
                'character_error_rate': character_error_rate,
                'recall': recall
            })

    return results

def calculate_recall(true_transcription, generated_caption):
    true_words = true_transcription.split()
    generated_words = generated_caption.split()

    # Create a binary array for matches
    true_binary = np.isin(true_words, generated_words).astype(int)
    
    # Calculate recall
    recall = recall_score(np.ones(len(true_words)), true_binary, zero_division=1)

    return recall

def main():
    parser = argparse.ArgumentParser(description="Calculate WER, CER, and Recall.")
    parser.add_argument('--case_sensitive', action='store_true', help='Enable case-sensitive calculations')
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(base_dir, "../data/raw/LATAM")
    captions_dir = os.path.join(base_dir, "../results/intermediate/captions_integrated")
    summary_output_dir = os.path.join(base_dir, "../results/final/summary")

    countries = ['argentinian', 'chilean', 'colombian', 'peruvian', 'puerto_rican', 'venezuelan']
    genders = ['female', 'male']

    os.makedirs(summary_output_dir, exist_ok=True)

    combined_results = []

    for country in countries:
        for gender in genders:
            if country == 'puerto_rican' and gender == 'male':
                continue

            captions_file = os.path.join(captions_dir, f"concatenated_audio_{country}_{gender}.json")
            transcription_file = os.path.join(raw_data_dir, country, f"line_index_{gender}.tsv")

            captions_data, transcription_data = load_data(captions_file, transcription_file)

            if captions_data is None or transcription_data is None:
                continue

            # Calculate WER, CER, and recall
            results = calculate_error_rates(captions_data, transcription_data, case_sensitive=args.case_sensitive)

            # Save individual results
            output_file = os.path.join(summary_output_dir, f"error_rates_comparison_{country}_{gender}_insensitive2.csv")
            pd.DataFrame(results).to_csv(output_file, index=False)

            combined_results.extend(results)

    if combined_results:
        combined_output_file = os.path.join(summary_output_dir, "combined_error_rates_insenstive2.csv")
        pd.DataFrame(combined_results).to_csv(combined_output_file, index=False)

if __name__ == "__main__":
    main()
