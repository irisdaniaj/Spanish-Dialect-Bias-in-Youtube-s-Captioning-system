import os
import subprocess

def convert_audio_to_video(audio_file, image_file, output_file):
    # Convert to have 480x360 resolution.
    command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_file,
        "-i", audio_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-vf", "scale=480:360",
        "-shortest",
        output_file
    ]
    subprocess.run(command, check=True)

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the base directory (one level up from the script directory)
    base_dir = os.path.dirname(script_dir)

    # Define the relative paths
    client_secret_file = os.path.join(script_dir, "client_secret.json")
    audio_folder = os.path.join(base_dir, "data/interim")
    image_file = os.path.join(base_dir, "data/raw/A_black_image.jpg")
    processed_folder = os.path.join(base_dir, "data/processed")
  
    # Ensure the processed directory exists
    os.makedirs(processed_folder, exist_ok=True)

    # Iterate over .wav files starting with "concatenated_"
    for audio_file in os.listdir(audio_folder):
        if audio_file.endswith(".wav") and audio_file.startswith("concatenated_"):
            audio_path = os.path.join(audio_folder, audio_file)
            video_file = os.path.join(processed_folder, os.path.splitext(audio_file)[0] + ".mp4")

            # Check if the video file already exists
            if os.path.exists(video_file):
                print(f"Skipping creation of {video_file} as it already exists.")
                continue

            # Convert audio to video
            print(f"Processing: {audio_file} -> {video_file}")
            convert_audio_to_video(audio_path, image_file, video_file)
            print(f"Created: {video_file}")