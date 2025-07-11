import os
import shutil

def safe_merge_folders(src_folder, dst_folder):
    """Move files from src to dst without overwriting, then remove src."""
    for file_name in os.listdir(src_folder):
        src_file = os.path.join(src_folder, file_name)
        dst_file = os.path.join(dst_folder, file_name)
        if os.path.exists(dst_file):
            print(f"⚠️ File {dst_file} already exists. Skipping.")
        else:
            shutil.move(src_file, dst_file)
            print(f"✅ Moved {file_name} to {dst_folder}")
    try:
        os.rmdir(src_folder)
        print(f"🗑️ Removed empty folder: {src_folder}")
    except OSError:
        print(f"⚠️ Could not remove {src_folder}, it may not be empty.")

def rename_gender_folders(base_audio_folder_gender):
    """Merge es_XX_female/male into clean male/female folders inside country directories."""
    countries = ['argentinian', 'chilean', 'colombian', 'peruvian', 'venezuelan', 'puerto_rican']
    gender_mappings = {
        'es_ar_female': 'female', 'es_ar_male': 'male',
        'es_cl_female': 'female', 'es_cl_male': 'male',
        'es_co_female': 'female', 'es_co_male': 'male',
        'es_pe_female': 'female', 'es_pe_male': 'male',
        'es_ve_female': 'female', 'es_ve_male': 'male',
        'es_pr_female': 'female'
    }

    for country in countries:
        country_path = os.path.join(base_audio_folder_gender, country)
        if os.path.isdir(country_path):
            for old_gender_name, new_gender_name in gender_mappings.items():
                old_path = os.path.join(country_path, old_gender_name)
                new_path = os.path.join(country_path, new_gender_name)

                if os.path.isdir(old_path):
                    os.makedirs(new_path, exist_ok=True)
                    print(f"🔄 Merging contents of {old_path} into {new_path}")
                    safe_merge_folders(old_path, new_path)
                else:
                    print(f"ℹ️ Skipped: {old_path} does not exist")

def move_gender_audio(source_folder, gender_tag, dest_folder):
    """Move audio files matching TEDX_F_ or TEDX_M_ into appropriate folders."""
    if not os.path.isdir(source_folder):
        print(f"❌ Source folder not found: {source_folder}")
        return

    for fname in os.listdir(source_folder):
        if fname.endswith(".wav") and f"TEDX_{gender_tag}_" in fname:
            src = os.path.join(source_folder, fname)
            dst = os.path.join(dest_folder, fname)
            if os.path.exists(dst):
                print(f"⚠️ File already exists, skipping: {dst}")
            else:
                shutil.move(src, dst)
                print(f"✅ Moved {fname} → {dest_folder}")
    print(f"✅ Done moving TEDX_{gender_tag}_* files.")

def organize_mexico_audio(base_dir):
    """Handles the Mexico TEDX audio and transcription."""
    source_speech = os.path.join(base_dir, "data", "raw", "mexico", "tedx_spanish_corpus", "tedx_spanish_corpus", "speech")
    dest_female = os.path.join(base_dir, "data", "raw", "mexico", "speech", "female")
    dest_male = os.path.join(base_dir, "data", "raw", "mexico", "speech", "male")

    transcription_src = os.path.join(base_dir, "data", "raw", "mexico", "tedx_spanish_corpus", "tedx_spanish_corpus", "files", "TEDx_Spanish.transcription")
    transcription_dst = os.path.join(base_dir, "data", "raw", "mexico", "TEDx_Spanish.transcription")

    os.makedirs(dest_female, exist_ok=True)
    os.makedirs(dest_male, exist_ok=True)

    print(f"🔍 Looking in: {source_speech}")
    move_gender_audio(source_speech, "F", dest_female)
    move_gender_audio(source_speech, "M", dest_male)

    if os.path.isfile(transcription_src):
        shutil.move(transcription_src, transcription_dst)
        print(f"📄 Moved transcription → {transcription_dst}")
    else:
        print(f"❌ Transcription file not found at: {transcription_src}")

def main():
    # Resolve base directory two levels up from src/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, ".."))

    # LATAM dialect folder
    base_audio_folder_gender = os.path.join(base_dir, "data", "raw", "LATAM")
    rename_gender_folders(base_audio_folder_gender)

    # Mexico TEDX audio cleanup
    organize_mexico_audio(base_dir)

if __name__ == "__main__":
    main()
