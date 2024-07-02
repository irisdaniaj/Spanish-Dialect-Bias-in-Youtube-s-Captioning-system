import os

# Check the current working directory
print("Current Working Directory:", os.getcwd())

# Path to the audio folder
audio_folder = '/Spanish-Dialect-Bias-in-Youtube-s-Captioning-system/data/raw/LATAM/argentinian/es_ar_female'

# Verify if the directory exists
if not os.path.exists(audio_folder):
    print(f"Directory does not exist: {audio_folder}")
else:
    print(f"Directory exists: {audio_folder}")

# List files in the audio folder
try:
    audio_files = os.listdir(audio_folder)
    print("Audio files:", audio_files)
except FileNotFoundError as e:
    print(e)
