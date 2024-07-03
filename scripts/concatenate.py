import os
import subprocess

def concatenate_audios(audio_folder, output_file):
    audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.wav')]
    audio_files.sort()  # Ensure files are in order if necessary

    # Create a list file for FFmpeg
    with open("file_list.txt", "w") as file_list:
        start_times = []
        current_time = 0.0

        for audio_file in audio_files:
            audio_path = os.path.join(audio_folder, audio_file)
            duration = get_audio_duration(audio_path)
            start_times.append((audio_file, current_time, current_time + duration))
            file_list.write(f"file '{audio_path}'\n")
            current_time += duration

    # Use FFmpeg to concatenate the audio files
    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "file_list.txt",
        "-c", "copy",
        output_file
    ]
    subprocess.run(command, check=True)

    # Clean up
    os.remove("file_list.txt")

    return start_times

def get_audio_duration(audio_file):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", audio_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define the base directory (one level up from the script directory)
    base_dir = os.path.dirname(script_dir)
    audio_folder = os.path.join(base_dir, "data/raw/LATAM/argentinian/es_ar_female")
    output_file = os.path.join(base_dir, "data/processed/concated_audio/es_ar_female.wav")
    start_times = concatenate_audios(audio_folder, output_file)
    
    # Print start and end times for each audio file
    for file, start, end in start_times:
        print(f"{file}: {start} - {end}")
