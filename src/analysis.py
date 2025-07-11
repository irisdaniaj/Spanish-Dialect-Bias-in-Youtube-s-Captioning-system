import os
import pandas as pd
import json
from jiwer import wer, cer
from sklearn.metrics import recall_score
import numpy as np

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
        summary_data['country'].append(country)
        summary_data['wer_F'].append(female_wer)
        summary_data['wer_M'].append(male_wer)
        summary_data['cer_F'].append(female_cer)
        summary_data['cer_M'].append(male_cer)
        summary_data['recall_F'].append(female_recall)
        summary_data['recall_M'].append(male_recall)
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)

def save_country_overall_summary(countries, female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls, output_file):
    summary_data = {
        'country': [],
        'overall_wer': [],
        'overall_cer': [],
        'overall_recall': []
    }
    
    for country, female_wer, male_wer, female_cer, male_cer, female_recall, male_recall in zip(
            countries, female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls):
        combined_wer = (female_wer + male_wer) / 2 if female_wer is not None and male_wer is not None else female_wer or male_wer
        combined_cer = (female_cer + male_cer) / 2 if female_cer is not None and male_cer is not None else female_cer or male_cer
        combined_recall = (female_recall + male_recall) / 2 if female_recall is not None and male_recall is not None else female_recall or male_recall
        
        summary_data['country'].append(country)
        summary_data['overall_wer'].append(combined_wer)
        summary_data['overall_cer'].append(combined_cer)
        summary_data['overall_recall'].append(combined_recall)
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)

def save_gender_summary(female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls, output_file):
    valid_female_wers = [wer for wer in female_wers if wer is not None]
    print(f"Valid female WERs: {valid_female_wers}")
    valid_male_wers = [wer for wer in male_wers if wer is not None]
    print(f"Valid male WERs: {valid_male_wers}")
    valid_female_cers = [cer for cer in female_cers if cer is not None]
    valid_male_cers = [cer for cer in male_cers if cer is not None]
    valid_female_recalls = [recall for recall in female_recalls if recall is not None]
    valid_male_recalls = [recall for recall in male_recalls if recall is not None]
    
    summary_data = {
        'gender': ['female', 'male'],
        'average_wer': [
            sum(valid_female_wers) / len(valid_female_wers) if valid_female_wers else None,
            sum(valid_male_wers) / len(valid_male_wers) if valid_male_wers else None
        ],
        'average_cer': [
            sum(valid_female_cers) / len(valid_female_cers) if valid_female_cers else None,
            sum(valid_male_cers) / len(valid_male_cers) if valid_male_cers else None
        ],
        'average_recall': [
            sum(valid_female_recalls) / len(valid_female_recalls) if valid_female_recalls else None,
            sum(valid_male_recalls) / len(valid_male_recalls) if valid_male_recalls else None
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)

def save_overall_performance(female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls, output_file):
    valid_female_wers = [wer for wer in female_wers if wer is not None]
    valid_male_wers = [wer for wer in male_wers if wer is not None]
    valid_female_cers = [cer for cer in female_cers if cer is not None]
    valid_male_cers = [cer for cer in male_cers if cer is not None]
    valid_female_recalls = [recall for recall in female_recalls if recall is not None]
    valid_male_recalls = [recall for recall in male_recalls if recall is not None]
    
    overall_wer = (sum(valid_female_wers) + sum(valid_male_wers)) / (len(valid_female_wers) + len(valid_male_wers))
    overall_cer = (sum(valid_female_cers) + sum(valid_male_cers)) / (len(valid_female_cers) + len(valid_male_cers))
    overall_recall = (sum(valid_female_recalls) + sum(valid_male_recalls)) / (len(valid_female_recalls) + len(valid_male_recalls))
    
    summary_data = {
        'region': ['LATAM'],
        'overall_wer': [overall_wer],
        'overall_cer': [overall_cer],
        'overall_recall': [overall_recall]
    }

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_file, index=False)

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

    female_wers = []
    male_wers = []
    female_cers = []
    male_cers = []
    female_recalls = []
    male_recalls = []

    for country in countries:
        country_female_results = []
        country_male_results = []
        
        for gender in genders:
            if country == 'puerto_rican' and gender == 'male':
                continue

            captions_file = os.path.join(captions_dir, f"concatenated_audio_{country}_{gender}.json")
            transcription_file = os.path.join(raw_data_dir, country, f"line_index_{gender}.tsv")

            captions_data, transcription_data = load_data(captions_file, transcription_file)

            if captions_data is None:
                print(f"⛔ No captions found at {captions_file}")
            if transcription_data is None:
                print(f"⛔ No transcriptions found at {transcription_file}")
            else:
                print(f"✅ Loaded {len(captions_data)} captions and {len(transcription_data)} transcriptions for {country}_{gender}")

            # Calculate WER, CER, and recall
            results = calculate_error_rates(captions_data, transcription_data, case_sensitive=True)

            # Save individual results
            output_file = os.path.join(summary_output_dir, f"error_rates_comparison_{country}_{gender}.csv")
            save_results(results, output_file)

            if gender == 'female':
                combined_results_female.extend(results)
                country_female_results.extend(results)
            else:
                combined_results_male.extend(results)
                country_male_results.extend(results)
        
        # Calculate and save WER, CER, and recall for each country
        if country_female_results:
            female_wer = wer(" ".join([result['true_transcription'] for result in country_female_results]),
                             " ".join([result['generated_caption'] for result in country_female_results]))
            female_cer = cer(" ".join([result['true_transcription'] for result in country_female_results]),
                             " ".join([result['generated_caption'] for result in country_female_results]))
            female_recall = calculate_recall(" ".join([result['true_transcription'] for result in country_female_results]),
                                             " ".join([result['generated_caption'] for result in country_female_results]))
        else:
            female_wer = None
            female_cer = None
            female_recall = None
        
        if country_male_results:
            male_wer = wer(" ".join([result['true_transcription'] for result in country_male_results]),
                           " ".join([result['generated_caption'] for result in country_male_results]))
            male_cer = cer(" ".join([result['true_transcription'] for result in country_male_results]),
                           " ".join([result['generated_caption'] for result in country_male_results]))
            male_recall = calculate_recall(" ".join([result['true_transcription'] for result in country_male_results]),
                                           " ".join([result['generated_caption'] for result in country_male_results]))
        else:
            male_wer = None
            male_cer = None
            male_recall = None
        
        female_wers.append(female_wer)
        male_wers.append(male_wer)
        female_cers.append(female_cer)
        male_cers.append(male_cer)
        female_recalls.append(female_recall)
        male_recalls.append(male_recall)

    # Save overall summary
    overall_summary_file = os.path.join(summary_output_dir, "LATAM_country_gender.csv")
    save_overall_summary(countries, female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls, overall_summary_file)

    # Save country overall summary
    country_overall_summary_file = os.path.join(summary_output_dir, "LATAM_country.csv")
    save_country_overall_summary(countries, female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls, country_overall_summary_file)

    # Save gender summary
    gender_summary_file = os.path.join(summary_output_dir, "LATAM_gender.csv")
    save_gender_summary(female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls, gender_summary_file)

    # Save overall performance
    overall_performance_file = os.path.join(summary_output_dir, "LATAM_overall.csv")
    save_overall_performance(female_wers, male_wers, female_cers, male_cers, female_recalls, male_recalls, overall_performance_file)

if __name__ == "__main__":
    main()
