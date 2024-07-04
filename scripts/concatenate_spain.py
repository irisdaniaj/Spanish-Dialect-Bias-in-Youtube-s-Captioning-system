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
    for root, _, files in os.walk(base_audio_folder):
        male_audio_files = []
        female_audio_files = []
        male_start_times = []
        female_start_times = []
        male_current_time = 0.0
        female_current_time = 0.0

        print(f"Processing directory: {root}")

        for file in files:
            if file.endswith(".wav"):
                audio_path = os.path.join(root, file)
                duration = get_audio_duration(audio_path)
                
                if "_M_" in file:
                    male_audio_files.append(audio_path)
                    male_start_times.append((audio_path, male_current_time, male_current_time + duration))
                    male_current_time += duration
                elif "_F_" in file:
                    female_audio_files.append(audio_path)
                    female_start_times.append((audio_path, female_current_time, female_current_time + duration))
                    female_current_time += duration

        if male_audio_files:
            print(f"Found male audio files: {male_audio_files}")
            list_file_path = os.path.join(output_folder, "file_list_spain_male.txt")
            with open(list_file_path, "w") as file_list:
                for audio_file in male_audio_files:
                    file_list.write(f"file '{audio_file}'\n")

            output_file = os.path.join(output_folder, "concatenated_audio_spain_male.wav")
            print(f"Concatenating male files into {output_file}")

            command = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file_path,
                "-c", "copy",
                output_file
            ]
            subprocess.run(command, check=True)
            os.remove(list_file_path)

            print(f"Processed male files in {root}")
            for file, start, end in male_start_times:
                print(f"{file}: {start} - {end}")

        if female_audio_files:
            print(f"Found female audio files: {female_audio_files}")
            list_file_path = os.path.join(output_folder, "file_list_spain_female.txt")
            with open(list_file_path, "w") as file_list:
                for audio_file in female_audio_files:
                    file_list.write(f"file '{audio_file}'\n")

            output_file = os.path.join(output_folder, "concatenated_audio_spain_female.wav")
            print(f"Concatenating female files into {output_file}")

            command = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file_path,
                "-c", "copy",
                output_file
            ]
            subprocess.run(command, check=True)
            os.remove(list_file_path)

            print(f"Processed female files in {root}")
            for file, start, end in female_start_times:
                print(f"{file}: {start} - {end}")

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the base directory (one level up from the script directory)
    base_dir = os.path.dirname(script_dir)
    
    # Define the base audio folder and output folder
    base_audio_folder = os.path.join(base_dir, "data/raw/spain/tedx_spain/tedx_spanish_corpus/speech")
    output_folder = os.path.join(base_dir, "data/processed")

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Concatenate the audios
    concatenate_audios(base_audio_folder, output_folder)
