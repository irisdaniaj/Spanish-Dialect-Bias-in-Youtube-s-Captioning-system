import os
import librosa
import numpy as np
import webrtcvad
import matplotlib.pyplot as plt

def extract_pitch(y, sr):
    # Extract the pitch (F0) using librosa's pYIN
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), 
                                                 fmax=librosa.note_to_hz('C7'), sr=sr)
    return f0

def extract_intensity(y):
    # Calculate the Root Mean Square (RMS) energy
    rms = librosa.feature.rms(y=y)[0]
    return rms

def estimate_speech_rate(y, sr, frame_duration=30):
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

def analyze_audio_file(file_path, save_dir):
    # Load the audio file
    y, sr = librosa.load(file_path, sr=None)
    
    # Extract pitch, intensity, and speech rate
    f0 = extract_pitch(y, sr)
    rms = extract_intensity(y)
    speech_rate = estimate_speech_rate(y, sr)
    
    # Display results
    print(f"Analysis for {os.path.basename(file_path)}:")
    print(f" - Estimated speech rate: {speech_rate:.2f} syllables per second")
    
    # Plotting
    plt.figure(figsize=(12, 8))

    # Plot the waveform
    plt.subplot(3, 1, 1)
    librosa.display.waveshow(y, sr=sr, alpha=0.6)
    plt.title('Waveform')
    
    # Plot the pitch
    plt.subplot(3, 1, 2)
    times = librosa.times_like(f0, sr=sr)
    plt.plot(times, f0, label='Pitch (F0)', color='r')
    plt.title('Pitch (F0)')
    plt.xlabel('Time (s)')
    
    # Plot the intensity (RMS)
    plt.subplot(3, 1, 3)
    rms_times = librosa.times_like(rms, sr=sr)
    plt.plot(rms_times, rms, label='RMS Intensity', color='b')
    plt.title('Intensity (RMS Energy)')
    plt.xlabel('Time (s)')
    
    plt.tight_layout()

    # Save the plot
    os.makedirs(save_dir, exist_ok=True)
    plot_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_analysis.png"
    plot_path = os.path.join(save_dir, plot_filename)
    plt.savefig(plot_path, dpi=300)
    print(f"Plot saved to {plot_path}")

    # Show the plot
    plt.show()

def analyze_directory(directory, save_dir):
    # Analyze each .wav file in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith('.wav'):
            file_path = os.path.join(directory, filename)
            analyze_audio_file(file_path, save_dir)

# Define the directories
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
audio_directory = os.path.join(base_dir, "data/interim")
plot_save_directory = os.path.join(base_dir, "../results/final/plots")

# Run the analysis
analyze_directory(audio_directory, plot_save_directory)
