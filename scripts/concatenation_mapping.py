import os
import subprocess
import json

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
    countries = ['argentinian', 'colombian', 'chilean', 'peruvian', 'puerto_rican', 'venezuelan']
    genders = ['es_ar_female', 'es_ar_male', 'es_co_female', 'es_co_male', 'es_cl_female', 'es_cl_male', 'es_pe_female', 'es_pe_male', 'es_pr_female', 'es_ve_female', 'es_ve_male']
    mapping = {country: {gender: [] for gender in genders} for country in countries}

    for country in countries:
        for gender in genders:
            gender_path = os.path.join(base_audio_folder, country, gender)
            if os.path.isdir(gender_path):
                audio_files = []
                start_times = []
                current_time = 0.0

                print(f"Processing {country} - {gender}")

                for _, _, files in os.walk(gender_path):
                    for file in files:
                        if file.endswith(".wav"):
                            audio_path = os.path.join(gender_path, file)
                            duration = get_audio_duration(audio_path)
                            audio_files.append(audio_path)
                            start_times.append((file, current_time, current_time + duration))
                            mapping[country][gender].append({"file": file, "start": current_time, "end": current_time + duration})
                            current_time += duration

                if audio_files:
                    print(f"Found audio files: {audio_files}")

                    # Create a list file for FFmpeg
                    list_file_path = os.path.join(output_folder, f"file_list_{country}_{gender}.txt")
                    with open(list_file_path, "w") as file_list:
                        for audio_file in audio_files:
                            file_list.write(f"file '{audio_file}'\n")

                    # Define the output file path
                    processed_filename = f"concatenated_audio_{country}_{gender}.wav"
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
                    print(f"Processed {gender_path}")
                    for file, start, end in start_times:
                        print(f"{file}: {start} - {end}")

    # Save the mapping to a JSON file
    with open(os.path.join(output_folder, "mapping.json"), "w") as f:
        json.dump(mapping, f, indent=4)

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the base directory (one level up from the script directory)
    base_dir = os.path.dirname(script_dir)
    
    # Define the base audio folder and output folder
    base_audio_folder = os.path.join(base_dir, "data/raw/LATAM")
    output_folder = os.path.join(base_dir, "data/processed")

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Concatenate the audios
    concatenate_audios(base_audio_folder, output_folder)
