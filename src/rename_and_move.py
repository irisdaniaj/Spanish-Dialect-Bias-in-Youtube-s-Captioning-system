import os
import shutil

def rename_gender_folders(base_audio_folder_gender):
    countries = ['argentinian', 'chilean', 'colombian', 'peruvian', 'venezuelan', 'puerto_rican']
    gender_mappings = {
        'es_ar_female': 'female',
        'es_ar_male': 'male',
        'es_cl_female': 'female',
        'es_cl_male': 'male',
        'es_co_female': 'female',
        'es_co_male': 'male',
        'es_pe_female': 'female',
        'es_pe_male': 'male',
        'es_ve_female': 'female',
        'es_ve_male': 'male',
        'es_pr_female': 'female'
    }

    for country in countries:
        country_path = os.path.join(base_audio_folder_gender, country)
        if os.path.isdir(country_path):
            for old_gender_name, new_gender_name in gender_mappings.items():
                old_gender_path = os.path.join(country_path, old_gender_name)
                new_gender_path = os.path.join(country_path, new_gender_name)
                if os.path.isdir(old_gender_path):
                    print(f"Renaming {old_gender_path} to {new_gender_path}")
                    os.rename(old_gender_path, new_gender_path)
                elif os.path.isdir(new_gender_path):
                    print(f"{new_gender_path} already exists")
                else:
                    print(f"{old_gender_path} does not exist")

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

    # Define the base directory (one level up from the script directory)
    base_dir = os.path.dirname(script_dir)
    
    # Define the base audio folder
    base_audio_folder_gender = os.path.join(base_dir, "data/raw/LATAM")
    base_audio_folder = os.path.join(base_dir, "data/raw/spain/tedx_spain/tedx_spanish_corpus/speech")

    # Move the audio files
    move_audio_files(base_audio_folder)
    # Rename the gender folders
    rename_gender_folders(base_audio_folder_gender)


