import os
import librosa
import numpy as np
import webrtcvad
import matplotlib.pyplot as plt
import pandas as pd

def extract_pitch(y, sr):
    try:
        # Extract the pitch (F0) using librosa's pYIN
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), 
                                                     fmax=librosa.note_to_hz('C7'), sr=sr)
        return f0
    except Exception as e:
        print(f"Error extracting pitch: {e}")
        return None

def extract_intensity(y):
    try:
        # Calculate the Root Mean Square (RMS) energy
        rms = librosa.feature.rms(y=y)[0]
        return rms
    except Exception as e:
        print(f"Error extracting intensity: {e}")
        return None

def estimate_speech_rate(y, sr, frame_duration=30):
    try:
        # Use WebRTC Voice Activity Detector to detect voiced frames
        vad = webrtcvad.Vad()
        vad.set_mode(3)  # Mode 3 is the most aggressive

        # Convert to frames
        frame_length = int(sr * frame_duration / 1000)
        frames = librosa.util.frame(y, frame_length=frame_length, hop_length=frame_length).T

        # Detect voiced frames
        voiced_frames = sum(vad.is_speech(frame.tobytes(), sample_rate=sr) for frame in frames)
        
        # Estimate speech rate as syllables per second
        total_duration = len(y) / sr
        speech_rate = voiced_frames / total_duration  # approximates syllables per second
        return speech_rate
    except Exception as e:
        print(f"Error estimating speech rate: {e}")
        return None

def analyze_audio_file(file_path, save_dir):
    print(f"Processing file: {file_path}")
    
    try:
        # Load the audio file
        y, sr = librosa.load(file_path, sr=None)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None
    
    # Extract pitch, intensity, and speech rate
    f0 = extract_pitch(y, sr)
    rms = extract_intensity(y)
    speech_rate = estimate_speech_rate(y, sr)
    
    # Calculate average pitch and intensity for simplicity
    avg_pitch = np.nanmean(f0) if f0 is not None else None
    avg_intensity = np.mean(rms) if rms is not None else None

    # Extract country and gender from filename
    filename = os.path.basename(file_path)
    parts = filename.split('_')
    country = parts[4]  # assuming the format "resampled_16000_concatenated_audio_{country}_{gender}.wav"
    gender = parts[5].replace('.wav', '')

    # Display results
    if speech_rate is not None:
        print(f" - Estimated speech rate: {speech_rate:.2f} syllables per second")
    else:
        print(" - Could not estimate speech rate.")
    
    # Plotting
    plt.figure(figsize=(12, 8))

    # Plot the waveform
    plt.subplot(3, 1, 1)
    librosa.display.waveshow(y, sr=sr, alpha=0.6)
    plt.title('Waveform')
    
    # Plot the pitch
    plt.subplot(3, 1, 2)
    if f0 is not None:
        times = librosa.times_like(f0, sr=sr)
        plt.plot(times, f0, label='Pitch (F0)', color='r')
        plt.title('Pitch (F0)')
    else:
        plt.title('Pitch (F0) - Not available')
    plt.xlabel('Time (s)')
    
    # Plot the intensity (RMS)
    plt.subplot(3, 1, 3)
    if rms is not None:
        rms_times = librosa.times_like(rms, sr=sr)
        plt.plot(rms_times, rms, label='RMS Intensity', color='b')
        plt.title('Intensity (RMS Energy)')
    else:
        plt.title('Intensity (RMS Energy) - Not available')
    plt.xlabel('Time (s)')
    
    plt.tight_layout()

    # Save the plot
    os.makedirs(save_dir, exist_ok=True)
    plot_filename = f"{os.path.splitext(filename)[0]}_analysis.png"
    plot_path = os.path.join(save_dir, plot_filename)
    plt.savefig(plot_path, dpi=300)
    print(f"Plot saved to {plot_path}")

    # Show the plot
    plt.show()

    # Return metrics for CSV storage
    return {
        "filename": filename,
        "country": country,
        "gender": gender,
        "avg_pitch": avg_pitch,
        "avg_intensity": avg_intensity,
        "speech_rate": speech_rate
    }

def analyze_directory(directory, save_dir, csv_path):
    prefix = "resampled_16000_concatenated_"
    metrics_data = []  # To store metrics for each file

    for filename in os.listdir(directory):
        if filename.endswith('.wav') and filename.startswith(prefix):
            file_path = os.path.join(directory, filename)
            metrics = analyze_audio_file(file_path, save_dir)
            if metrics:
                metrics_data.append(metrics)

    if metrics_data:
        # Save metrics to CSV
        metrics_df = pd.DataFrame(metrics_data)
        metrics_df.to_csv(csv_path, index=False)
        print(f"Metrics saved to {csv_path}")
        
        # Calculate aggregated metrics by country and gender
        aggregated_df = metrics_df.groupby(['country', 'gender']).mean().reset_index()
        aggregated_csv_path = csv_path.replace(".csv", "_aggregated.csv")
        aggregated_df.to_csv(aggregated_csv_path, index=False)
        print(f"Aggregated metrics saved to {aggregated_csv_path}")

        # Plotting aggregated metrics by country and gender
        for metric in ['avg_pitch', 'avg_intensity', 'speech_rate']:
            plt.figure(figsize=(10, 6))
            sns.barplot(data=aggregated_df, x='country', y=metric, hue='gender')
            plt.title(f"{metric.replace('_', ' ').capitalize()} by Country and Gender")
            plt.xlabel('Country')
            plt.ylabel(metric.replace('_', ' ').capitalize())
            plt.legend(title='Gender')
            plt.tight_layout()

            # Save the plot
            plot_filename = f"{metric}_by_country_and_gender.png"
            plot_path = os.path.join(save_dir, plot_filename)
            plt.savefig(plot_path, dpi=300)
            print(f"Aggregated plot saved to {plot_path}")
            plt.show()
    else:
        print(f"No files found in {directory} with prefix '{prefix}'")

# Define the directories
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
audio_directory = os.path.join(base_dir, "data/interim")
plot_save_directory = os.path.join(base_dir, "results/final/plots")
csv_save_path = os.path.join(base_dir, "results/final/summary/audio_metrics.csv")

# Run the analysis
analyze_directory(audio_directory, plot_save_directory, csv_save_path)
