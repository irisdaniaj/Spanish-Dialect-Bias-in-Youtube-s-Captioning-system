import os
import pandas as pd
import json
from jiwer import wer

def load_data(captions_file, transcription_file):
    if not os.path.exists(captions_file):
        return None, None
    if not os.path.exists(transcription_file):
        return None, None

    with open(captions_file, 'r') as cf:
        captions_data = json.load(cf)

    transcription_data = pd.read_csv(transcription_file, sep='\t', header=None, names=['filename', 'transcription'])

    return captions_data, transcription_data

def calculate_wer(captions_data, transcription_data, case_sensitive=True):
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
            
            error_rate = wer(true_transcription, generated_caption)
            results.append({
                'filename': filename,
                'generated_caption': generated_caption,
                'true_transcription': true_transcription,
                'word_error_rate': error_rate
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
    
    results_df = pd.DataFrame([{'combined_word_error_rate': combined_wer}])
    results_df.to_csv(output_file, index=False)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(base_dir, "../data/raw/LATAM")
    captions_dir = os.path.join(base_dir, "../results/intermediate/captions_integrated")
    summary_output_dir = os.path.join(base_dir, "../results/final/summary")

    countries = ['argentinian', 'chilean', 'colombian', 'peruvian', 'puerto_rican', 'venezuelan']
    genders = ['female', 'male']

    os.makedirs(summary_output_dir, exist_ok=True)

    combined_results_female = []
    combined_results_male = []

    for country in countries:
        for gender in genders:
            if country == 'puerto_rican' and gender == 'male':
                continue

            captions_file = os.path.join(captions_dir, f"concatenated_audio_{country}_{gender}.json")
            transcription_file = os.path.join(raw_data_dir, country, f"line_index_{gender}.tsv")

            captions_data, transcription_data = load_data(captions_file, transcription_file)

            if captions_data is None or transcription_data is None:
                continue

            results = calculate_wer(captions_data, transcription_data, case_sensitive=True)

            # Save individual results
            output_file = os.path.join(summary_output_dir, f"wer_comparison_{country}_{gender}.csv")
            save_results(results, output_file)

            if gender == 'female':
                combined_results_female.extend(results)
            else:
                combined_results_male.extend(results)

    # Save combined results
    output_file_combined_female = os.path.join(summary_output_dir, "combined_wer_female.csv")
    output_file_combined_male = os.path.join(summary_output_dir, "combined_wer_male.csv")

    save_combined_results(combined_results_female, output_file_combined_female)
    save_combined_results(combined_results_male, output_file_combined_male)

if __name__ == "__main__":
    main()
