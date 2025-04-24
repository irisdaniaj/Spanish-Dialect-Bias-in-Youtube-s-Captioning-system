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
    return float(result.stdout.decode("utf-8"))

DELAY = 5
MAX_DURATION = 1800

def concatenate_audios(output_folder, country, gender, audio_files, start_times, sample_rate):
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

    for i, (audio_file, times) in enumerate(zip(audio_files, start_times)):
        if times["end"] > MAX_DURATION:
            print(f"Reached maximum duration of {MAX_DURATION} seconds. Ignoring remaining files.")
            break

        current_chunk_files.append(audio_file)
        current_chunk_start_times.append(times)

    if current_chunk_files:
        save_concatenated_audio(output_folder, country, gender, current_chunk_files, current_chunk_start_times, sample_rate)

def save_concatenated_audio(output_folder, country, gender, audio_files, start_times, sample_rate):
    processed_filename = f"concatenated_audio_{country}_{gender}.wav"
    output_file = os.path.join(output_folder, processed_filename)

    # Create a list file for FFmpeg
    list_file_path = os.path.join(output_folder, f"file_list_{country}_{gender}.txt")
    silent_audio_path = os.path.join(output_folder, f"silence_{sample_rate}.wav")
    with open(list_file_path, "w") as file_list:
        for audio_file in audio_files:
            file_list.write(f"file '{audio_file}'\n")
            file_list.write(f"file '{silent_audio_path}'\n")

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
        print(f"{times['file']}: {times['start']} - {times['end']}, duration: {times['duration']}")


    # Save the mapping to a JSON file
    mapping_filename = f"mapping_{country}_{gender}.json"
    with open(os.path.join(output_folder, mapping_filename), "w") as f:
        json.dump(start_times, f, indent=4)


def process_country_genders(country, genders, base_audio_folder, output_folder):
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
                        end_time = current_time + duration + DELAY
                        start_times.append({"file": file, "start": current_time, "end": end_time, "duration": duration})
                        current_time += duration + DELAY

                        if current_time > MAX_DURATION:
                            print(f"Reached maximum duration of {MAX_DURATION} seconds. Ignoring remaining files.")
                            break

            concatenate_audios(output_folder, country, gender, audio_files, start_times, 48000)
        else:
            print(f"Directory does not exist: {gender_path}")


def process_latam(base_audio_folder, output_folder):
    countries = ['argentinian', 'colombian', 'chilean', 'peruvian', 'puerto_rican', 'venezuelan']
    genders = ['female', 'male']

    for country in countries:
        process_country_genders(country, genders, base_audio_folder, output_folder)

def process_mexico(base_audio_folder, output_folder, transcription_file):
    genders = ['female', 'male']

    for gender in genders:
        processed_filename = f"concatenated_audio_mexico_{gender}.wav"
        output_file = os.path.join(output_folder, processed_filename)
        mapping_filename = f"mapping_mexico_{gender}.json"
        mapping_file = os.path.join(output_folder, mapping_filename)
        
        if os.path.exists(output_file) and os.path.exists(mapping_file):
            print(f"Skipping Mexico - {gender} as {processed_filename} and {mapping_filename} already exist.")
            continue

        gender_path = os.path.join(base_audio_folder, gender)
        print(f"Checking directory: {gender_path}")
        if os.path.isdir(gender_path):
            audio_files = []
            start_times = []
            current_time = 0.0

            print(f"Processing mexico - {gender}")

            for _, _, files in os.walk(gender_path):
                for file in files:
                    if file.endswith(".wav"):
                        audio_path = os.path.join(gender_path, file)
                        duration = get_audio_duration(audio_path)
                        audio_files.append(audio_path)
                        start_times.append({"file": file, "start": current_time, "end": current_time + duration, "duration": duration})
                        current_time += duration + DELAY

                        if current_time > MAX_DURATION:
                            print(f"Reached maximum duration of {MAX_DURATION} seconds. Ignoring remaining files.")
                            break

            concatenate_audios(output_folder, 'mexico', gender, audio_files, start_times, 16000)
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

    # Create a 5-second silent audio file.
    # This is for LATAM audios, which are sampled at 48000 Hz.
    silent_48000_audio_path = os.path.join(output_folder_latam, "silence_48000.wav")
    if not os.path.exists(silent_48000_audio_path):
        subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "5", silent_48000_audio_path])
    # This is for mexico audios, which are sampled at 16000 Hz.
    silent_16000_audio_path = os.path.join(output_folder_latam, "silence_16000.wav")
    if not os.path.exists(silent_16000_audio_path):
        subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono", "-t", "5", silent_16000_audio_path])

    # Process LATAM audios
    process_latam(base_audio_folder_latam, output_folder_latam)

    # Define the base audio folder and output folder for mexico
    base_audio_folder_mexico = os.path.join(base_dir, "data/raw/mexico/tedx_mexico/tedx_spanish_corpus/speech")
    output_folder_mexico = os.path.join(base_dir, "data/interim")

    # Ensure the output directory exists
    os.makedirs(output_folder_mexico, exist_ok=True)

    # Define the transcription file for mexico
    transcription_file_mexico = os.path.join(base_dir, "data/raw/mexico/tedx_mexico/tedx_spanish_corpus/files/TEDx_Spanish.transcription")

    # Process mexico audios and transcriptions
    process_mexico(base_audio_folder_mexico, output_folder_mexico, transcription_file_mexico)
