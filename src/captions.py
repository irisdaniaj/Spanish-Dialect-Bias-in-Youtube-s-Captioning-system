from datetime import datetime, timedelta
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import argparse
import srt

# Define the scope for YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CAPTIONS_FORMAT = "srt"

def authenticate():
    creds = None 
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid or creds.scopes != SCOPES:
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
    # Load responses from disk if available.
    # It is expensive to fetch all video IDs, so we cache the responses.
    if os.path.exists("responses.json"):
        print("Found cached responses. Loading...")
        with open("responses.json", "r") as f:
            responses = json.load(f)
    else:
        print("Fetching all video IDs...")
        responses = []
        request = youtube.search().list(
            part="id,snippet",
            channelId=channel_id,
            maxResults=50
        )

        while request:
            response = request.execute()
            responses.append(response)
            print(f"Retrieved {len(video_ids)} video IDs.")
            request = youtube.search().list_next(request, response)

        # Save responses to disk
        with open("responses.json", "w") as f:
            json.dump(responses, f)

    for response in responses:
        for item in response['items']:
            if item['id']['kind'] == 'youtube#video':
                video_ids.append((item['id']['videoId'], item['snippet']['title']))

    return video_ids

def get_captions(video_id, title, output_dir):
    creds = authenticate()
    youtube = build("youtube", "v3", credentials=creds)

    clean_title = title.replace("Title for ", "").replace(".mp4", "")

    if os.path.exists(os.path.join(output_dir, f"{clean_title}_response.json")):
        print(f"Found cached captions metadata for video '{clean_title}'. Loading...")
        with open(os.path.join(output_dir, f"{clean_title}_response.json"), "r") as f:
            response = json.load(f)
    else:
        print(f"Fetching caption metadata for video '{clean_title}'...")
        request = youtube.captions().list(
            part="id,snippet",
            videoId=video_id
        )
        response = request.execute()

        # Save response to disk
        with open(os.path.join(output_dir, f"{clean_title}_response.json"), "w") as f:
            json.dump(response, f)

    caption_id = None
    if len(response["items"]) > 0:
        caption_id = response["items"][0].get("id")

    if caption_id:
        output_path = os.path.join(output_dir, f"{clean_title}.{CAPTIONS_FORMAT}")

        if os.path.exists(output_path):
            print(f"Captions for video {clean_title} already downloaded.")
            return
        
        print(f"Downloading captions for video {clean_title}...")

        request = youtube.captions().download(
            id=caption_id,
            tfmt=CAPTIONS_FORMAT
        )

        caption_response = request.execute()
        with open(output_path, "wb") as caption_file:
            caption_file.write(caption_response)

        print(f"Captions for video {clean_title} downloaded successfully to {output_path}.")
    else:
        print(f"No captions found for video {clean_title}.")

def convert_time_to_seconds(time_str: str):
    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    delta = timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second, microseconds=time_obj.microsecond)
    total_seconds = delta.total_seconds()
    return total_seconds

def get_matching_files(start, end, metadata):
    matching_files = []
    for meta in metadata:
        if start >= meta['start'] and end <= meta['end'] or \
            start >= meta['start'] and start <= meta['end'] or \
            end >= meta['start'] and end <= meta['end']:
            matching_files.append(meta)
    return matching_files

def parse_srt(srt_file, metadata_file, output_dir):
    with open(metadata_file, 'r', encoding='utf-8') as file:
        metadata = json.load(file)

    with open(srt_file, 'r', encoding='utf-8') as file:
        contents = file.read()

    captions = list(srt.parse(contents))

    output = []
    
    # Step 1: simple mapping of captions to files.
    # It is not entirely accurate, but it is a good starting point.
    possible_captions = []
    for caption in captions:
        start = caption.start.total_seconds()
        end = caption.end.total_seconds()
        possible_captions.append({
            'start': start,
            'end': end,
            'text': caption.content,
        })

    # Step 2: Youtube will sometimes split a single caption into multiple
    # parts, where the last word of one caption is the first word of the next
    # caption. Create a new caption entry for each part of the split caption.

    integrated_captions = []
    for caption in possible_captions:
        if len(integrated_captions) == 0:
            integrated_captions.append(caption)
        else:
            first_word, *rest = caption['text'].split(" ")
            last_caption = integrated_captions[-1]
            last_caption['text'] += " " + first_word
            integrated_captions.append(caption | {'text': " ".join(rest)})

    # Step 3: Add metadata to captions
    metadata_captions = []
    for caption in integrated_captions:
        matching_files = get_matching_files(caption['start'], caption['end'], metadata)
        metadata_captions.append(caption | {'files': matching_files})
    
    # Step 4: Combine captions that have the same file name.
    # For captions with multiple files, we will take the second file.
    captions = []
    for meta in metadata:
        file_info = meta['file'].split('_')
        speaker_type = file_info[0]
        speaker_id = file_info[1]
        file_id = file_info[2].split('.')[0]
        
        relevant_captions = []

        for caption in metadata_captions:
            caption_files = [f['file'] for f in caption['files']]
            if len(caption_files) == 1 and caption_files[0] == meta['file']:
                relevant_captions.append(caption)
            if len(caption_files) > 1 and caption_files[1] == meta['file']:
                relevant_captions.append(caption)

        captions.append({
            'filename': meta['file'],
            'speaker_type': speaker_type,
            'speaker_id': speaker_id,
            'file_id': file_id,
            'start': meta['start'],
            'end': meta['end'],
            'captions': ' '.join([c['text'] for c in relevant_captions])
        })

    output = captions

    integrated_captions_path = os.path.join(output_dir, os.path.basename(captions_file).replace('.srt', '.json'))
    with open(integrated_captions_path, 'w', encoding='utf-8') as file:
        json.dump(output, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve and integrate captions from YouTube videos")
    parser.add_argument("channel_id", help="The ID of the YouTube channel")

    args = parser.parse_args()

    output_dir = "../results"

    raw_captions_dir = os.path.join(output_dir, "raw", "captions")
    intermediate_captions_dir = os.path.join(output_dir, "intermediate", "captions_integrated")
    os.makedirs(raw_captions_dir, exist_ok=True)
    os.makedirs(intermediate_captions_dir, exist_ok=True)

    video_ids = get_all_video_ids(args.channel_id)

    for video_id, title in video_ids:
        # Save captions
        get_captions(video_id, title, raw_captions_dir)

    for file in os.listdir(raw_captions_dir):
        if not file.endswith(f".{CAPTIONS_FORMAT}"):
            continue
        captions_file = os.path.join(raw_captions_dir, file)
        title = os.path.basename(captions_file)
        # Integrate metadata into captions
        clean_title = title.replace("concatenated_audio_", "").replace(f".{CAPTIONS_FORMAT}", "")
        metadata_file = os.path.join("../data", "interim", f"mapping_{clean_title}.json")
        if "mexico_female" in clean_title:
            metadata_file = os.path.join("../data", "interim", "mapping_mexico_female.json")
        elif "mexico_male" in clean_title:
            metadata_file = os.path.join("../data", "interim", "mapping_mexico_male.json")
        else:
            print(f"No matching metadata file for {clean_title}. Skipping...")
            continue

        if CAPTIONS_FORMAT == "srt":
            parse_srt(captions_file, metadata_file, intermediate_captions_dir)
        else:
            raise ValueError(f"Unsupported captions format: {CAPTIONS_FORMAT}")
