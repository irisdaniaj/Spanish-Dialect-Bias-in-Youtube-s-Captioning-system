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

    with open(captions_file, 'r') as cf:
        captions_data = json.load(cf)

    transcription_data = {}
    with open(transcription_file, 'r') as tf:
        for line in tf:
            transcription, filename = line.rsplit(' ', 1)
            transcription_data[filename.strip()] = transcription.strip()

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
        else:
            print(f"Filename not found in transcriptions: {filename}")

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

def save_overall_summary(countries, female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls, output_file):
    summary_data = {
        'country': [],
        'wer_F': [],
        'wer_M': [],
        'cer_F': [],
        'cer_M': [],
        'recall_F': [],
        'recall_M': []
    }

    for country, female_wer, male_wer, female_cer, male_cer, female_recall, male_recall in zip(
            countries, female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls):
        if female_wer is not None and male_wer is not None:
            summary_data['country'].append(country)
            summary_data['wer_F'].append(female_wer)
            summary_data['wer_M'].append(male_wer)
            summary_data['cer_F'].append(female_cer)
            summary_data['cer_M'].append(male_cer)
            summary_data['recall_F'].append(female_recall)
            summary_data['recall_M'].append(male_recall)

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)

def save_overall_wer(countries, overall_wers, overall_cers, overall_recalls, output_file):
    summary_data = {
        'country': [],
        'overall_wer': [],
        'overall_cer': [],
        'overall_recall': []
    }

    for country, overall_wer, overall_cer, overall_recall in zip(countries, overall_wers, overall_cers, overall_recalls):
        summary_data['country'].append(country)
        summary_data['overall_wer'].append(overall_wer)
        summary_data['overall_cer'].append(overall_cer)
        summary_data['overall_recall'].append(overall_recall)

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)

def save_detailed_results(results, output_file):
    if not results:
        return

    detailed_data = [{
        'filename': result['filename'],
        'generated_captions': result['generated_caption'],
        'true_transcription': result['true_transcription'],
        'wer': result['word_error_rate'],
        'cer': result['character_error_rate'],
        'recall': result['recall']
    } for result in results]

    detailed_df = pd.DataFrame(detailed_data)
    detailed_df.to_csv(output_file, index=False)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(base_dir, "../data/raw/spain/tedx_spain/tedx_spanish_corpus/files")
    captions_dir = os.path.join(base_dir, "../results/intermediate/captions_integrated")
    summary_output_dir = os.path.join(base_dir, "../results/final/summary")

    genders = ['female', 'male']
    country = 'spain'

    os.makedirs(summary_output_dir, exist_ok=True)

    combined_results_female = []
    combined_results_male = []

    female_wers = []
    male_wers = []
    female_cers = []
    male_cers = []
    female_recalls = []
    male_recalls = []

    for gender in genders:
        captions_file = os.path.join(captions_dir, f"concatenated_audio_spain_{gender}.json")
        transcription_file = os.path.join(raw_data_dir, "TEDx_Spanish.transcription")

        captions_data, transcription_data = load_data(captions_file, transcription_file)

        if captions_data is None or transcription_data is None:
            print(f"Data not loaded for gender: {gender}")
            continue

        results = calculate_error_rates(captions_data, transcription_data, case_sensitive=True)

        # Save individual results
        output_file = os.path.join(summary_output_dir, f"error_rates_comparison_spain_{gender}.csv")
        save_results(results, output_file)

        if gender == 'female':
            combined_results_female.extend(results)
            if results:
                female_wer = wer(" ".join([result['true_transcription'] for result in results]),
                                 " ".join([result['generated_caption'] for result in results]))
                female_cer = cer(" ".join([result['true_transcription'] for result in results]),
                                 " ".join([result['generated_caption'] for result in results]))
                female_recall = calculate_recall(" ".join([result['true_transcription'] for result in results]),
                                                 " ".join([result['generated_caption'] for result in results]))
            else:
                female_wer = None
                female_cer = None
                female_recall = None
            female_wers.append(female_wer)
            female_cers.append(female_cer)
            female_recalls.append(female_recall)
        else:
            combined_results_male.extend(results)
            if results:
                male_wer = wer(" ".join([result['true_transcription'] for result in results]),
                               " ".join([result['generated_caption'] for result in results]))
                male_cer = cer(" ".join([result['true_transcription'] for result in results]),
                               " ".join([result['generated_caption'] for result in results]))
                male_recall = calculate_recall(" ".join([result['true_transcription'] for result in results]),
                                               " ".join([result['generated_caption'] for result in results]))
            else:
                male_wer = None
                male_cer = None
                male_recall = None
            male_wers.append(male_wer)
            male_cers.append(male_cer)
            male_recalls.append(male_recall)

    # Save overall summary
    overall_summary_file = os.path.join(summary_output_dir, "gender_spain.csv")
    save_overall_summary([country], female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls, overall_summary_file)

    # Calculate and save overall WER, CER, and recall
    overall_error_file = os.path.join(summary_output_dir, "overall_spain.csv")
    combined_all_results = combined_results_female + combined_results_male
    if combined_all_results:
        overall_wer = wer(" ".join([result['true_transcription'] for result in combined_all_results]),
                          " ".join([result['generated_caption'] for result in combined_all_results]))
        overall_cer = cer(" ".join([result['true_transcription'] for result in combined_all_results]),
                          " ".join([result['generated_caption'] for result in combined_all_results]))
        overall_recall = calculate_recall(" ".join([result['true_transcription'] for result in combined_all_results]),
                                          " ".join([result['generated_caption'] for result in combined_all_results]))
        save_overall_wer([country], [overall_wer], [overall_cer], [overall_recall], overall_error_file)
    else:
        print("No combined results to calculate overall WER, CER, and recall.")

if __name__ == "__main__":
    main()
