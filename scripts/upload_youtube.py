import os
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)  # Replace with your client secret file
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def upload_video(video_file, title, description, tags, category, privacy_status, uploaded_videos):
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

    # Record the uploaded video
    uploaded_videos.append(video_file)
    with open('uploaded_videos.json', 'w') as f:
        json.dump(uploaded_videos, f)

if __name__ == "__main__":
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the base directory (one level up from the script directory)
    base_dir = os.path.dirname(script_dir)

    # Define the relative paths
    client_secret_file = os.path.join(script_dir, "client_secret.json")
    video_folder = os.path.join(base_dir, "data/processed")

    # Load the list of already uploaded videos
    if os.path.exists('uploaded_videos.json'):
        with open('uploaded_videos.json', 'r') as f:
            uploaded_videos = json.load(f)
    else:
        uploaded_videos = []

    # Iterate over all .mp4 files in the specified folder
    for video_file in os.listdir(video_folder):
        if video_file.endswith(".mp4") and video_file not in uploaded_videos:
            video_path = os.path.join(video_folder, video_file)

            # Upload video to YouTube
            title = f"Title for {video_file}"  # Customize the title as needed
            description = f"Description for {video_file}"  # Customize the description as needed
            tags = ["tag1", "tag2"]  # Customize the tags as needed
            category = "22"  # Replace with the appropriate category ID
            privacy_status = "public"  # "public", "private", or "unlisted"

            upload_video(video_path, title, description, tags, category, privacy_status, uploaded_videos)
