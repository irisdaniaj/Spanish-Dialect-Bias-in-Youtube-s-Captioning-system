import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import subprocess

# Define the scope for YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES) # Replace with your client secret file
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def upload_video(video_file, title, description, tags, category, privacy_status):
    creds = authenticate()
    youtube = build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    media_file = MediaFileUpload(video_file)

    response_upload = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    ).execute()

    print(f"Video uploaded successfully: https://www.youtube.com/watch?v={response_upload['id']}")

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

if __name__ == "__main__":
    audio_folder = ".../data/raw/LATAM/aregentinian/es_ar_female"  # Replace with the path to your audio folder
    image_file = ".../data/raw/A_black_image.jpg"  # Replace with the path to your static image file

    # Iterate over all .wav files in the specified folder
    for audio_file in os.listdir(audio_folder):
        if audio_file.endswith(".wav"):
            audio_path = os.path.join(audio_folder, audio_file)
            video_file = os.path.join(audio_folder, os.path.splitext(audio_file)[0] + ".mp4")

            # Convert audio to video
            convert_audio_to_video(audio_path, image_file, video_file)

            # Upload video to YouTube
            title = f"Title for {audio_file}"  # Customize the title as needed
            description = f"Description for {audio_file}"  # Customize the description as needed
            tags = ["tag1", "tag2"]  # Customize the tags as needed
            category = "22"  # Replace with the appropriate category ID
            privacy_status = "public"  # "public", "private", or "unlisted"

            upload_video(video_file, title, description, tags, category, privacy_status)
