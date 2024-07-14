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

def concatenate_audios(output_folder, country, gender, audio_files, start_times, max_duration=1800):
    processed_filename = f"concatenated_audio_{country}_{gender}.wav"
    output_file = os.path.join(output_folder, processed_filename)
    mapping_filename = f"mapping_{country}_{gender}.json"
    mapping_file = os.path.join(output_folder, mapping_filename)
    
    # Check if the output file and mapping file already exist
    if os.path.exists(output_file) and os.path.exists(mapping_file):
        print(f"Skipping {country} - {gender} as {processed_filename} and {mapping_filename} already exist.")
        return

    current_chunk_files = []
    current_chunk_start_times = []
    current_chunk_duration = 0.0
    delay = 5.0  # 5 seconds delay between each audio file

    for i, (audio_file, times) in enumerate(zip(audio_files, start_times)):
        duration = times["end"] - times["start"]

        if current_chunk_duration + duration + delay > max_duration:
            print(f"Reached maximum duration of {max_duration} seconds. Ignoring remaining files.")
            break

        current_chunk_files.append(audio_file)
        current_chunk_start_times.append(times)
        current_chunk_duration += duration + delay

    if current_chunk_files:
        save_concatenated_audio(output_folder, country, gender, current_chunk_files, current_chunk_start_times)

def save_concatenated_audio(output_folder, country, gender, audio_files, start_times):
    processed_filename = f"concatenated_audio_{country}_{gender}.wav"
    output_file = os.path.join(output_folder, processed_filename)

    print(f"Found audio files for concatenation: {audio_files}")

    # Create a list file for FFmpeg
    list_file_path = os.path.join(output_folder, f"file_list_{country}_{gender}.txt")
    with open(list_file_path, "w") as file_list:
        for audio_file in audio_files:
            file_list.write(f"file '{audio_file}'\n")
            file_list.write("file 'silence.wav'\n")  # Add silence between each file

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
    for times in start_times:
        print(f"{times['file']}: {times['start']} - {times['end']}")

    # Save the mapping to a JSON file
    mapping_filename = f"mapping_{country}_{gender}.json"
    with open(os.path.join(output_folder, mapping_filename), "w") as f:
        json.dump(start_times, f, indent=4)

def process_latam(base_audio_folder, output_folder):
    countries = ['argentinian', 'colombian', 'chilean', 'peruvian', 'puerto_rican', 'venezuelan']
    genders = ['female', 'male']

    for country in countries:
        for gender in genders:
            gender_path = os.path.join(base_audio_folder, country, gender)
            print(f"Checking directory: {gender_path}")
            if os.path.isdir(gender_path):
                processed_filename = f"concatenated_audio_{country}_{gender}.wav"
                output_file = os.path.join(output_folder, processed_filename)
                mapping_filename = f"mapping_{country}_{gender}.json"
                mapping_file = os.path.join(output_folder, mapping_filename)
                
                if os.path.exists(output_file) and os.path.exists(mapping_file):
                    print(f"Skipping {country} - {gender} as {processed_filename} and {mapping_filename} already exist.")
                    continue

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
                            current_time += duration + 5.0  # Add 5 seconds delay

                concatenate_audios(output_folder, country, gender, audio_files, start_times)
            else:
                print(f"Directory does not exist: {gender_path}")

def process_spain(base_audio_folder, output_folder, transcription_file):
    genders = ['female', 'male']

    for gender in genders:
        processed_filename = f"concatenated_audio_spain_{gender}.wav"
        output_file = os.path.join(output_folder, processed_filename)
        mapping_filename = f"mapping_spain_{gender}.json"
        mapping_file = os.path.join(output_folder, mapping_filename)
        
        if os.path.exists(output_file) and os.path.exists(mapping_file):
            print(f"Skipping Spain - {gender} as {processed_filename} and {mapping_filename} already exist.")
            continue

        gender_path = os.path.join(base_audio_folder, gender)
        print(f"Checking directory: {gender_path}")
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
                        current_time += duration + 5.0  # Add 5 seconds delay

            concatenate_audios(output_folder, 'spain', gender, audio_files, start_times)
        else:
            print(f"Directory does not exist: {gender_path}")

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the base directory (one level up from the script directory)
    base_dir = os.path.dirname(script_dir)

    # Define the base audio folder and output folder for LATAM
    base_audio_folder_latam = os.path.join(base_dir, "data/raw/LATAM")
    output_folder_latam = os.path.join(base_dir, "data/interim")

    # Ensure the output directory exists
    os.makedirs(output_folder_latam, exist_ok=True)

    # Create a 5-second silent audio file
    silent_audio_path = os.path.join(output_folder_latam, "silence.wav")
    if not os.path.exists(silent_audio_path):
        subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "5", silent_audio_path])

    # Process LATAM audios
    #process_latam(base_audio_folder_latam, output_folder_latam)

    # Define the base audio folder and output folder for Spain
    base_audio_folder_spain = os.path.join(base_dir, "data/raw/spain/tedx_spain/tedx_spanish_corpus/speech")
    output_folder_spain = os.path.join(base_dir, "data/interim")

    # Ensure the output directory exists
    os.makedirs(output_folder_spain, exist_ok=True)

    # Define the transcription file for Spain
    transcription_file_spain = os.path.join(base_dir, "data/raw/spain/tedx_spain/tedx_spanish_corpus/files/TEDx_Spanish.transcription")

    # Process Spain audios and transcriptions
    process_spain(base_audio_folder_spain, output_folder_spain, transcription_file_spain)
