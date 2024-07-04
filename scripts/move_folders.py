import os
import shutil

def move_audio_files(base_audio_folder):
    male_folder = os.path.join(base_audio_folder, 'male')
    female_folder = os.path.join(base_audio_folder, 'female')
    
    # Create male and female folders if they don't exist
    os.makedirs(male_folder, exist_ok=True)
    os.makedirs(female_folder, exist_ok=True)
    
    for file_name in os.listdir(base_audio_folder):
        if file_name.endswith('.wav'):
            file_path = os.path.join(base_audio_folder, file_name)
            
            if 'TEDX_F_' in file_name:
                new_path = os.path.join(female_folder, file_name)
                shutil.move(file_path, new_path)
                print(f"Moved {file_name} to {female_folder}")
            
            elif 'TEDX_M_' in file_name:
                new_path = os.path.join(male_folder, file_name)
                shutil.move(file_path, new_path)
                print(f"Moved {file_name} to {male_folder}")

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the base directory (three levels up from the script directory)
    base_dir = os.path.dirname(script_dir)
    
    # Define the base audio folder using the base directory
    base_audio_folder = os.path.join(base_dir, "data/raw/spain/tedx_spain/tedx_spanish_corpus/speech")

    # Move the audio files
    move_audio_files(base_audio_folder)
