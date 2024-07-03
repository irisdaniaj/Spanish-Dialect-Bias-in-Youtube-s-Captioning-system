import os
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def convert_audio_to_video(audio_file, image_file, output_file):
    command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_file,
        "-i", audio_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_file
    ]
    subprocess.run(command, check=True)

def upload_video(video_file, title, description, tags, category, privacy_status):
    # Set up WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # Open YouTube Studio
        driver.get("https://studio.youtube.com/")
        
        # Log in to YouTube
        input("Please log in to YouTube and press Enter to continue...")

        # Navigate to the upload page
        driver.get("https://studio.youtube.com/channel/UC/UPLOAD_PAGE_URL")

        # Wait for the upload button to be clickable and click it
        upload_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@type="file"]'))
        )
        upload_button.send_keys(os.path.abspath(video_file))
        
        # Wait for the title input field and enter the title
        title_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'textbox'))
        )
        title_input.clear()
        title_input.send_keys(title)
        
        # Enter the description
        description_input = driver.find_element(By.XPATH, '//*[@id="textbox"][@aria-label="Description"]')
        description_input.send_keys(description)
        
        # Add tags (you might need to add logic to find the correct element for tags)
        # Note: This might require additional steps depending on the page structure
        
        # Select category
        category_dropdown = driver.find_element(By.XPATH, '//*[@id="category"]')
        category_dropdown.click()
        category_option = driver.find_element(By.XPATH, f'//yt-formatted-string[text()="{category}"]')
        category_option.click()
        
        # Set privacy status
        privacy_dropdown = driver.find_element(By.XPATH, '//*[@id="privacy-dropdown"]')
        privacy_dropdown.click()
        privacy_option = driver.find_element(By.XPATH, f'//tp-yt-paper-item[@name="{privacy_status}"]')
        privacy_option.click()
        
        # Click "Done" to finalize the upload
        done_button = driver.find_element(By.XPATH, '//*[@id="done-button"]')
        done_button.click()
        
        # Wait for the process to complete
        time.sleep(60)  # Adjust sleep time as necessary
        
        print("Video uploaded successfully.")
        
        return driver.current_url  # Return the URL of the uploaded video for further use
        
    finally:
        driver.quit()

def process_audio_files(audio_folder, image_file, title_template, description_template, tags, category, privacy_status):
    for audio_file in os.listdir(audio_folder):
        if audio_file.endswith(".wav"):
            audio_path = os.path.join(audio_folder, audio_file)
            video_file = os.path.join(audio_folder, os.path.splitext(audio_file)[0] + ".mp4")

            # Convert audio to video
            convert_audio_to_video(audio_path, image_file, video_file)

            # Customize title and description
            title = title_template.format(audio_file=os.path.splitext(audio_file)[0])
            description = description_template.format(audio_file=os.path.splitext(audio_file)[0])

            # Upload video to YouTube
            video_url = upload_video(video_file, title, description, tags, category, privacy_status)
            
            if video_url:
                check_captions(video_url)

def check_captions(video_url):
    # Set up WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get(video_url)
        time.sleep(10)  # Wait for the video page to load completely
        
        captions_exist = False
        attempts = 10  # Number of attempts to check for captions
        
        for _ in range(attempts):
            driver.refresh()
            time.sleep(10)  # Wait for the video page to load completely
            try:
                # Check for the presence of captions (subtitles) on the page
                captions_element = driver.find_element(By.XPATH, '//div[@class="captions-text"]')
                if captions_element:
                    captions_exist = True
                    break
            except Exception:
                continue
        
        if captions_exist:
            print("Captions are available for the video.")
        else:
            print("Captions are not available for the video after checking.")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    # Define the base directory (one level up from the script directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    # Define the relative paths
    client_secret_file = os.path.join(script_dir, "client_secret.json")
    audio_folder = os.path.join(base_dir, "data/raw/LATAM/argentinian/es_ar_female")
    image_file = os.path.join(base_dir, "data/raw/A_black_image.jpg")
    
    # Define metadata templates
    title_template = "Title for {audio_file}"
    description_template = "Description for {audio_file}"
    tags = ["tag1", "tag2"]
    category = "Science & Technology"  # Replace with the appropriate category ID
    privacy_status = "private"  # "public", "private", or "unlisted"
    
    process_audio_files(audio_folder, image_file, title_template, description_template, tags, category, privacy_status)
