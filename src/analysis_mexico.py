import os
import pandas as pd
import json
from jiwer import wer, cer
import numpy as np
from sklearn.metrics import recall_score

def load_data(captions_file, transcription_file):
    if not os.path.exists(captions_file):
        print(f"Captions file not found: {captions_file}")
        return None, None
    if not os.path.exists(transcription_file):
        print(f"Transcription file not found: {transcription_file}")
        return None, None

    # Load captions JSON
    with open(captions_file, 'r') as cf:
        captions_data = json.load(cf)

    # Extract filenames from captions
    mapping_filenames = {entry["filename"].replace(".wav", "") for entry in captions_data}

    # Filter transcriptions to include only filenames in the mapping
    transcription_data = {}
    with open(transcription_file, 'r') as tf:
        for line in tf:
            transcription, filename = line.rsplit(" ", 1)
            filename = filename.strip().replace(".wav", "")
            if filename in mapping_filenames:
                transcription_data[filename] = transcription.strip()

    return captions_data, transcription_data

def calculate_recall(true_transcription, generated_caption):
    true_words = true_transcription.split()
    generated_words = generated_caption.split()

    # Create a binary array for matches
    true_binary = np.isin(true_words, generated_words).astype(int)

    # Calculate recall
    recall = recall_score(np.ones(len(true_words)), true_binary, zero_division=1)

    return recall

def calculate_error_rates(captions_data, transcription_data, case_sensitive=True):
    results = []
    filenames_in_captions = {entry['filename'].replace('.wav', '') for entry in captions_data}
    filenames_in_transcriptions = set(transcription_data.keys())

    common_filenames = filenames_in_captions.intersection(filenames_in_transcriptions)
    print(f"Common filenames: {len(common_filenames)}")

    # Debugging: Log mismatched filenames
    for filename in filenames_in_transcriptions - filenames_in_captions:
        print(f"Filename in transcription but not in captions: {filename}")
    for filename in filenames_in_captions - filenames_in_transcriptions:
        print(f"Filename in captions but not in transcription: {filename}")

    for entry in captions_data:
        filename = entry['filename'].replace('.wav', '')
        if filename in common_filenames:
            generated_caption = entry['captions']
            true_transcription = transcription_data[filename]

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

def save_results(results, output_file):
    if not results:
        return

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)

def save_combined_results(results, output_file):
    if not results:
        return

    all_generated_captions = " ".join([result['generated_caption'] for result in results])
    all_true_transcriptions = " ".join([result['true_transcription'] for result in results])
    combined_wer = wer(all_true_transcriptions, all_generated_captions)
    combined_cer = cer(all_true_transcriptions, all_generated_captions)
    combined_recall = calculate_recall(all_true_transcriptions, all_generated_captions)

    results_df = pd.DataFrame([{
        'combined_word_error_rate': combined_wer,
        'combined_character_error_rate': combined_cer,
        'combined_recall': combined_recall
    }])
    results_df.to_csv(output_file, index=False)

def main():
    raw_data_dir = "../data/raw/mexico/tedx_mexico/tedx_spanish_corpus/files"
    captions_dir =  "../results/intermediate/captions_integrated"
    summary_output_dir = "../results/final/summary"

    genders = ['female', 'male']
    country = 'mexico'

    os.makedirs(summary_output_dir, exist_ok=True)

    combined_results_female = []
    combined_results_male = []

    for gender in genders:
        captions_file = os.path.join(captions_dir, f"concatenated_audio_mexico_{gender}.json")
        transcription_file = os.path.join(raw_data_dir, "TEDx_Spanish.transcription")

        captions_data, transcription_data = load_data(captions_file, transcription_file)

        if captions_data is None or transcription_data is None:
            print(f"Data not loaded for gender: {gender}")
            continue

        results = calculate_error_rates(captions_data, transcription_data, case_sensitive=True)

        # Save individual results
        output_file = os.path.join(summary_output_dir, f"error_rates_comparison_mexico_{gender}.csv")
        save_results(results, output_file)

        if gender == 'female':
            combined_results_female.extend(results)
        else:
            combined_results_male.extend(results)

    # Save combined results
    combined_results = combined_results_female + combined_results_male
    overall_output_file = os.path.join(summary_output_dir, "overall_mexico.csv")
    save_combined_results(combined_results, overall_output_file)

if __name__ == "__main__":
    main()