import os
from pydub import AudioSegment
import os
import wave
import soundfile as sf

def check_audio_files(directory, target_sample_rate=48000, target_channels=1):
    # List to store files that do not match the target format
    mismatched_files = []

    # Iterate through all .wav files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.wav'):
            file_path = os.path.join(directory, filename)

            # Check the sample rate and number of channels using soundfile
            try:
                with sf.SoundFile(file_path) as audio_file:
                    sample_rate = audio_file.samplerate
                    channels = audio_file.channels

                    # Check if the file matches the target format
                    if sample_rate != target_sample_rate or channels != target_channels:
                        mismatched_files.append((filename, sample_rate, channels))
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    # Display results
    if mismatched_files:
        print("The following files do not match the target format:")
        for filename, sample_rate, channels in mismatched_files:
            print(f"{filename}: Sample Rate = {sample_rate} Hz, Channels = {channels}")
    else:
        print("All audio files match the target sample rate and channel configuration.")

# Directory containing .wav files
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
audio_directory = os.path.join(base_dir, "data/interim")

# Target sample rate (e.g., 16000 Hz) and number of channels (e.g., mono = 1)
target_sample_rate = 48000
target_channels = 1

# Run the check
check_audio_files(audio_directory, target_sample_rate, target_channels)


def resample_audio(input_file, output_file, target_sample_rate=16000):
    # Load the audio file
    audio = AudioSegment.from_wav(input_file)

    # Resample the audio
    audio = audio.set_frame_rate(target_sample_rate)

    # Export the resampled audio
    audio.export(output_file, format="wav")
    print(f"Converted {input_file} to {output_file} with sample rate {target_sample_rate} Hz")

def resample_audio_files(directory, target_sample_rate=16000):
    # Iterate through all .wav files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.wav'):
            input_file = os.path.join(directory, filename)
            output_file = os.path.join(directory, f"resampled_{target_sample_rate}_{filename}")
            
            # Resample the audio file
            resample_audio(input_file, output_file, target_sample_rate)

# Directory containing the .wav files
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
audio_directory = os.path.join(base_dir, "data/interim")

# Target sample rate
target_sample_rate = 16000

# Run the resampling
resample_audio_files(audio_directory, target_sample_rate)
