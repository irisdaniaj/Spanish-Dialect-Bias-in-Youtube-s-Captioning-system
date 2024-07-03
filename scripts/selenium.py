import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # Define your video file and metadata
    video_file = "path/to/your/video/file.mp4"
    title = "Your Video Title"
    description = "Your Video Description"
    tags = ["tag1", "tag2"]
    category = "Science & Technology"
    privacy_status = "public"  # "public", "private", or "unlisted"
    
    upload_video(video_file, title, description, tags, category, privacy_status)
