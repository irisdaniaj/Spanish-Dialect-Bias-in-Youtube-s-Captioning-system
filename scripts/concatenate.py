import os
import subprocess

def get_audio_duration(audio_file):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", audio_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

def concatenate_audios(base_audio_folder, output_folder):
    for root, dirs, _ in os.walk(base_audio_folder):
        for subdir in dirs:
            subdir_path = os.path.join(root, subdir)
            audio_files = []
            start_times = []
            current_time = 0.0

            print(f"Processing subdir: {subdir_path}")

            for _, _, files in os.walk(subdir_path):
                for file in files:
                    if file.endswith(".wav"):
                        audio_path = os.path.join(subdir_path, file)
                        duration = get_audio_duration(audio_path)
                        audio_files.append(audio_path)
                        start_times.append((audio_path, current_time, current_time + duration))
                        current_time += duration

            if audio_files:
                print(f"Found audio files: {audio_files}")

                # Create a list file for FFmpeg
                list_file_path = os.path.join(output_folder, f"file_list_{subdir.replace('/', '_')}.txt")
                with open(list_file_path, "w") as file_list:
                    for audio_file in audio_files:
                        file_list.write(f"file '{audio_file}'\n")

                # Define the output file path
                subdir_name = os.path.relpath(subdir_path, base_audio_folder).replace(os.sep, '_')
                processed_filename = f"concatenated_audio_{subdir_name}.wav"
                output_file = os.path.join(output_folder, processed_filename)

                print(f"Concatenating files into {output_file}")

                # Use FFmpeg to concatenate the audio files
                command = [
                    "ffmpeg",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", list_file_path,
                    "-c", "copy",
                    output_file
                ]
                subprocess.run(command, check=True)

                # Clean up
                os.remove(list_file_path)

                # Print start and end times for each audio file
                print(f"Processed {subdir_path}")
                for file, start, end in start_times:
                    print(f"{file}: {start} - {end}")

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the base directory (one level up from the script directory)
    base_dir = os.path.dirname(script_dir)
    
    # Define the base audio folder and output folder
    base_audio_folder = os.path.join(base_dir, "data/raw")
    output_folder = os.path.join(base_dir, "data/processed")

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Concatenate the audios
    concatenate_audios(base_audio_folder, output_folder)
