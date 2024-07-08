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

def concatenate_audios(output_folder, country, gender, audio_files, start_times):
    if audio_files:
        processed_filename = f"concatenated_audio_{country}_{gender}.wav"
        output_file = os.path.join(output_folder, processed_filename)
        
        if os.path.exists(output_file):
            print(f"Skipping {country} - {gender} as {processed_filename} already exists.")
            return

        print(f"Found audio files: {audio_files}")

        # Create a list file for FFmpeg
        list_file_path = os.path.join(output_folder, f"file_list_{country}_{gender}.txt")
        with open(list_file_path, "w") as file_list:
            for audio_file in audio_files:
                file_list.write(f"file '{audio_file}'\n")

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
        print(f"Processed {output_folder} - {gender}")
        for file, start, end in start_times:
            print(f"{file}: {start} - {end}")

        # Save the mapping to a JSON file
        mapping_filename = f"mapping_{country}_{gender}.json"
        with open(os.path.join(output_folder, mapping_filename), "w") as f:
            json.dump(start_times, f, indent=4)

def process_latam(base_audio_folder, output_folder):
    countries = ['argentinian', 'colombian', 'chilean', 'peruvian', 'puerto_rican', 'venezuelan']
    genders = ['female', 'male']
    
    for country in countries:
        for gender in genders:
            gender_path = os.path.join(base_audio_folder, country, f"es_{country[:2]}_{gender}")
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
                            start_times.append({"file": file, "start": current_time, "end": current_time + duration})
                            current_time += duration

                concatenate_audios(output_folder, country, gender, audio_files, start_times)

def process_spain(base_audio_folder, output_folder, transcription_file):
    genders = ['female', 'male']
    
    for gender in genders:
        gender_path = os.path.join(base_audio_folder, gender)
        if os.path.isdir(gender_path):
            audio_files = []
            start_times = []
            current_time = 0.0

            print(f"Processing Spain - {gender}")

            for _, _, files in os.walk(gender_path):
                for file in files:
                    if file.endswith(".wav"):
                        audio_path = os.path.join(gender_path, file)
                        duration = get_audio_duration(audio_path)
                        audio_files.append(audio_path)
                        start_times.append({"file": file, "start": current_time, "end": current_time + duration})
                        current_time += duration

            concatenate_audios(output_folder, 'spain', gender, audio_files, start_times)

            # Process transcription file
            with open(transcription_file, 'r') as f:
                transcriptions = f.readlines()
            transcription_map = {}
            for line in transcriptions:
                parts = line.strip().rsplit(' ', 1)
                if len(parts) == 2:
                    text, file_id = parts
                    transcription_map[file_id] = text

            # Save transcription mapping to JSON
            mapping_filename = f"mapping_spain_{gender}.json"
            with open(os.path.join(output_folder, mapping_filename), "w") as f:
                json.dump(transcription_map, f, indent=4)

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the base directory (one level up from the script directory)
    base_dir = os.path.dirname(script_dir)
    
    # Define the base audio folder and output folder for LATAM
    base_audio_folder_latam = os.path.join(base_dir, "data/raw/LATAM")
    output_folder_latam = os.path.join(base_dir, "data/processed")

    # Ensure the output directory exists
    os.makedirs(output_folder_latam, exist_ok=True)

    # Process LATAM audios
    process_latam(base_audio_folder_latam, output_folder_latam)

    # Define the base audio folder and output folder for Spain
    base_audio_folder_spain = os.path.join(base_dir, "data/raw/spain/tedx_spain/tedx_spanish_corpus/speech")
    output_folder_spain = os.path.join(base_dir, "data/processed")

    # Ensure the output directory exists
    os.makedirs(output_folder_spain, exist_ok=True)

    # Define the transcription file for Spain
    transcription_file_spain = os.path.join(base_dir, "data/raw/spain/tedx_spain/tedx_spanish_corpus/files/TEDx_Spanish.transcription")

    # Process Spain audios and transcriptions
    process_spain(base_audio_folder_spain, output_folder_spain, transcription_file_spain)
