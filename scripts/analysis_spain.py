import os
import pandas as pd
import json
from jiwer import wer

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

def calculate_wer(captions_data, transcription_data, case_sensitive=True):
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

            error_rate = wer(true_transcription, generated_caption)
            results.append({
                'filename': filename,
                'generated_caption': generated_caption,
                'true_transcription': true_transcription,
                'word_error_rate': error_rate
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

    results_df = pd.DataFrame([{'combined_word_error_rate': combined_wer}])
    results_df.to_csv(output_file, index=False)

def save_overall_summary(countries, female_wers, male_wers, output_file):
    summary_data = {
        'country': [],
        'wer_F': [],
        'wer_M': []
    }

    for country, female_wer, male_wer in zip(countries, female_wers, male_wers):
        if female_wer is not None and male_wer is not None:
            summary_data['country'].append(country)
            summary_data['wer_F'].append(female_wer)
            summary_data['wer_M'].append(male_wer)

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)

def save_overall_wer(countries, overall_wers, output_file):
    summary_data = {
        'country': [],
        'overall_wer': []
    }

    for country, overall_wer in zip(countries, overall_wers):
        summary_data['country'].append(country)
        summary_data['overall_wer'].append(overall_wer)

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)

def save_detailed_results(results, output_file):
    if not results:
        return

    detailed_data = [{
        'filename': result['filename'],
        'generated_captions': result['generated_caption'],
        'true_transcription': result['true_transcription'],
        'wer': result['word_error_rate']
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

    for gender in genders:
        captions_file = os.path.join(captions_dir, f"concatenated_audio_spain_{gender}.json")
        transcription_file = os.path.join(raw_data_dir, "TEDx_Spanish.transcription")

        captions_data, transcription_data = load_data(captions_file, transcription_file)

        if captions_data is None or transcription_data is None:
            print(f"Data not loaded for gender: {gender}")
            continue

        results = calculate_wer(captions_data, transcription_data, case_sensitive=True)

        # Save individual results
        output_file = os.path.join(summary_output_dir, f"wer_comparison_spain_{gender}.csv")
        save_results(results, output_file)

        if gender == 'female':
            combined_results_female.extend(results)
            if results:
                female_wer = wer(" ".join([result['true_transcription'] for result in results]),
                                 " ".join([result['generated_caption'] for result in results]))
            else:
                female_wer = None
            female_wers.append(female_wer)
        else:
            combined_results_male.extend(results)
            if results:
                male_wer = wer(" ".join([result['true_transcription'] for result in results]),
                               " ".join([result['generated_caption'] for result in results]))
            else:
                male_wer = None
            male_wers.append(male_wer)


    # Save overall summary
    overall_summary_file = os.path.join(summary_output_dir, "gender_spain.csv")
    save_overall_summary([country], female_wers, male_wers, overall_summary_file)

    # Calculate and save overall WER
    overall_wer_file = os.path.join(summary_output_dir, "overall_spain.csv")
    combined_all_results = combined_results_female + combined_results_male
    if combined_all_results:
        overall_wer = wer(" ".join([result['true_transcription'] for result in combined_all_results]),
                          " ".join([result['generated_caption'] for result in combined_all_results]))
        save_overall_wer([country], [overall_wer], overall_wer_file)
    else:
        print("No combined results to calculate overall WER.")

if __name__ == "__main__":
    main()
