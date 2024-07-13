import os
import sys
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import argparse

# Define the scope for YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_all_video_ids(channel_id):
    creds = authenticate()
    youtube = build("youtube", "v3", credentials=creds)

    video_ids = []
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=50
    )

    while request:
        response = request.execute()
        for item in response['items']:
            if item['id']['kind'] == 'youtube#video':
                video_ids.append(item['id']['videoId'])
        request = youtube.search().list_next(request, response)

    return video_ids

def get_captions(video_id, output_dir):
    creds = authenticate()
    youtube = build("youtube", "v3", credentials=creds)
    
    request = youtube.captions().list(
        part="id",
        videoId=video_id
    )
    response = request.execute()
    
    caption_id = None
    for item in response["items"]:
        caption_id = item["id"]
        break

    if caption_id:
        request = youtube.captions().download(
            id=caption_id,
            tfmt="vtt"
        )
        caption_response = request.execute()
        output_path = os.path.join(output_dir, "raw", "captions", f"{video_id}.vtt")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as caption_file:
            caption_file.write(caption_response)

        print(f"Captions for video {video_id} downloaded successfully to {output_path}.")
    else:
        print(f"No captions found for video {video_id}.")

def integrate_metadata(captions_file, metadata_file, output_dir):
    with open(captions_file, 'r') as cf, open(metadata_file, 'r') as mf:
        captions = cf.readlines()
        metadata = json.load(mf)
    
    integrated_captions = []
    speaker_index = 0

    for line in captions:
        if line.strip().isdigit():
            integrated_captions.append(line)
        elif '-->' in line:
            integrated_captions.append(line)
            start_time, end_time = line.split(' --> ')
            start_time_seconds = float(start_time.split(':')[-1].replace(',', '.'))
            end_time_seconds = float(end_time.split(':')[-1].replace(',', '.'))

            if speaker_index < len(metadata):
                speaker_info = metadata[speaker_index]
                if start_time_seconds >= speaker_info["start"] and end_time_seconds <= speaker_info["end"]:
                    integrated_captions.append(f"Speaker {speaker_info['file'].split('_')[1]}: ")
                    speaker_index += 1
        else:
            integrated_captions.append(line)
    
    integrated_captions_path = os.path.join(output_dir, "intermediate", "captions_integrated", os.path.basename(captions_file).replace('.vtt', '_integrated.vtt'))
    os.makedirs(os.path.dirname(integrated_captions_path), exist_ok=True)
    with open(integrated_captions_path, 'w') as integrated_file:
        integrated_file.writelines(integrated_captions)

    print(f"Integrated captions saved to {integrated_captions_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve and integrate captions from YouTube videos")
    parser.add_argument("channel_id", help="The ID of the YouTube channel")

    args = parser.parse_args()
    
    # Use relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    output_dir = os.path.join(base_dir, "results")
    metadata_file = os.path.join(base_dir, "data", "metadata.json")
    
    raw_captions_dir = os.path.join(output_dir, "raw", "captions")
    intermediate_captions_dir = os.path.join(output_dir, "intermediate", "captions_integrated")
    os.makedirs(raw_captions_dir, exist_ok=True)
    os.makedirs(intermediate_captions_dir, exist_ok=True)
    
    video_ids = get_all_video_ids(args.channel_id)
    
    for video_id in video_ids:
        # Save captions in VTT format
        get_captions(video_id, output_dir)
        
        # Integrate metadata into captions
        captions_file = os.path.join(raw_captions_dir, f"{video_id}.vtt")
        integrate_metadata(captions_file, metadata_file, output_dir)
