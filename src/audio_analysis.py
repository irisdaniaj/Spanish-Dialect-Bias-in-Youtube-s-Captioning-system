import os
import librosa
import numpy as np
import webrtcvad
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def extract_pitch(y, sr):
    try:
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr)
        return f0
    except Exception as e:
        print(f"Error extracting pitch: {e}")
        return None

def extract_intensity(y):
    try:
        rms = librosa.feature.rms(y=y)[0]
        return rms
    except Exception as e:
        print(f"Error extracting intensity: {e}")
        return None

import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def extract_pitch(y, sr):
    try:
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr)
        return f0
    except Exception as e:
        print(f"Error extracting pitch: {e}")
        return None

def extract_intensity(y):
    try:
        rms = librosa.feature.rms(y=y)[0]
        return rms
    except Exception as e:
        print(f"Error extracting intensity: {e}")
        return None

def analyze_audio_file(file_path, save_dir):
    filename = os.path.basename(file_path)
    plot_filename = f"{os.path.splitext(filename)[0]}_analysis.png"
    plot_path = os.path.join(save_dir, plot_filename)

    if os.path.exists(plot_path):
        print(f"Plot for {filename} already exists. Skipping analysis.")
    
    print(f"Processing file: {file_path}")
    try:
        y, sr = librosa.load(file_path, sr=None)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

    # Extract pitch and intensity
    f0 = extract_pitch(y, sr)
    rms = extract_intensity(y)
    
    # Calculate mean and standard deviation for pitch and intensity
    avg_pitch = np.nanmean(f0) if f0 is not None else None
    std_pitch = np.nanstd(f0) if f0 is not None else None
    avg_intensity = np.mean(rms) if rms is not None else None
    std_intensity = np.std(rms) if rms is not None else None

    # Extract country and gender from filename
    parts = filename.split('_')
    country = parts[4]
    gender = parts[5].replace('.wav', '')

    # Plot and save the waveform, pitch, and intensity
    plt.figure(figsize=(12, 8))
    plt.subplot(3, 1, 1)
    librosa.display.waveshow(y, sr=sr, alpha=0.6)
    plt.title('Waveform')
    
    plt.subplot(3, 1, 2)
    if f0 is not None:
        times = librosa.times_like(f0, sr=sr)
        plt.plot(times, f0, label='Pitch (F0)', color='r')
        plt.title('Pitch (F0)')
    else:
        plt.title('Pitch (F0) - Not available')
    plt.xlabel('Time (s)')
    
    plt.subplot(3, 1, 3)
    if rms is not None:
        rms_times = librosa.times_like(rms, sr=sr)
        plt.plot(rms_times, rms, label='RMS Intensity', color='b')
        plt.title('Intensity (RMS Energy)')
    else:
        plt.title('Intensity (RMS Energy) - Not available')
    plt.xlabel('Time (s)')
    
    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(plot_path, dpi=300)
    print(f"Plot saved to {plot_path}")
    #plt.show()

    # Return calculated metrics
    return {
        "filename": filename,
        "country": country,
        "gender": gender,
        "avg_pitch": avg_pitch,
        "std_pitch": std_pitch,
        "avg_intensity": avg_intensity,
        "std_intensity": std_intensity,
    }


def analyze_directory_or_load_aggregated(directory, save_dir, metrics_csv_path, aggregated_csv_path):
    prefix = "resampled_16000_concatenated_"
    metrics_data = []

    # Check if the aggregated CSV is already present
    if os.path.exists(aggregated_csv_path):
        print(f"Loading existing aggregated metrics from {aggregated_csv_path}.")
        metrics_df = pd.read_csv(aggregated_csv_path)
    else:
        # If the main metrics CSV is already present, load it
        if os.path.exists(metrics_csv_path):
            print(f"Metrics CSV {metrics_csv_path} already exists. Loading data.")
            metrics_df = pd.read_csv(metrics_csv_path)
        else:
            # Process audio files to create the metrics CSV
            for filename in os.listdir(directory):
                if filename.endswith('.wav') and filename.startswith(prefix):
                    file_path = os.path.join(directory, filename)
                    metrics = analyze_audio_file(file_path, save_dir)
                    if metrics:
                        metrics_data.append(metrics)

            # Save the metrics data to metrics CSV if new metrics were generated
            if metrics_data:
                metrics_df = pd.DataFrame(metrics_data)
                metrics_df.to_csv(metrics_csv_path, index=False)
                print(f"Metrics saved to {metrics_csv_path}")
            else:
                print("No metrics data generated.")
                return

        # Now that we have metrics data, create the aggregated file with standard deviation
    # Aggregate metrics by country and gender, with standard deviation
    aggregated_csv_path = metrics_csv_path.replace(".csv", "_aggregated_by_country_gender.csv")
    aggregated_df = metrics_df.groupby(['country', 'gender']).agg({
    'avg_pitch': ['mean', 'std'],
    'avg_intensity': ['mean', 'std'], 
    #'speech_rate': ['mean', 'std']
    }).reset_index()

    # Rename columns for clarity
    aggregated_df.columns = [
        'country', 'gender',
        'avg_pitch', 'std_pitch',
        'avg_intensity', 'std_intensity', 
        #'avg_speech_rate', 'std_speech_rate',
    ]

    # Save the aggregated data
    aggregated_df.to_csv(aggregated_csv_path, index=False)
    print(f"Aggregated metrics by country and gender saved to {aggregated_csv_path}")

    # Aggregate metrics by gender only, with standard deviation
    gender_aggregated_csv_path = aggregated_csv_path.replace("_by_country_gender.csv", "_by_gender.csv")
    gender_aggregated_df = metrics_df.groupby('gender').agg({
        'avg_pitch': ['mean', 'std'],
        'avg_intensity': ['mean', 'std'],
        #'speech_rate': ['mean', 'std']
    }).reset_index()
    gender_aggregated_df.columns = [
        'gender',
        'avg_pitch', 'std_pitch',
        'avg_intensity', 'std_intensity',
        #'avg_speech_rate', 'std_speech_rate'
    ]
    gender_aggregated_df.to_csv(gender_aggregated_csv_path, index=False)
    print(f"Aggregated metrics by gender saved to {gender_aggregated_csv_path}")

    # Aggregate metrics by country only, with standard deviation
    country_aggregated_csv_path = aggregated_csv_path.replace("_by_country_gender.csv", "_by_country.csv")
    country_aggregated_df = metrics_df.groupby('country').agg({
        'avg_pitch': ['mean', 'std'],
        'avg_intensity': ['mean', 'std'],
        #'speech_rate': ['mean', 'std']
    }).reset_index()
    country_aggregated_df.columns = [
        'country',
        'avg_pitch', 'std_pitch',
        'avg_intensity', 'std_intensity',
        #'avg_speech_rate', 'std_speech_rate'
    ]
    country_aggregated_df.to_csv(country_aggregated_csv_path, index=False)
    print(f"Aggregated metrics by country saved to {country_aggregated_csv_path}")


# Define the directories
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
audio_directory = os.path.join(base_dir, "data/interim")
plot_save_directory = os.path.join(base_dir, "results/final/plots")
metrics_csv_path = os.path.join(base_dir, "results/final/summary/audio_metrics.csv")
aggregated_csv_path = metrics_csv_path.replace(".csv", "_aggregated_by_country_gender.csv")

# Run the analysis or load existing data
analyze_directory_or_load_aggregated(audio_directory, plot_save_directory, metrics_csv_path, aggregated_csv_path)

