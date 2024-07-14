import os
import re
import sys
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import argparse
import webvtt

# Define the scope for YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

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
        raise ValueError()
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
        raise ValueError()
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
        output_path = os.path.join(output_dir, f"{clean_title}.vtt")

        if os.path.exists(output_path):
            print(f"Captions for video {clean_title} already downloaded.")
            return
        
        print(f"Downloading captions for video {clean_title}...")
        raise ValueError()

        request = youtube.captions().download(
            id=caption_id,
            tfmt="vtt"
        )

        caption_response = request.execute()
        with open(output_path, "wb") as caption_file:
            caption_file.write(caption_response)

        print(f"Captions for video {clean_title} downloaded successfully to {output_path}.")
    else:
        print(f"No captions found for video {clean_title}.")


def convert_time_to_seconds(time_str: str):
    h, m, s = time_str.split(':')
    s, ms = s.split('.')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def parse_vtt(vtt_file, metadata_file, output_dir):
    with open(metadata_file, 'r', encoding='utf-8') as file:
        metadata = json.load(file)

    raw_captions = []
    vtt = webvtt.read(vtt_file)
    for caption in vtt.captions:
        start = convert_time_to_seconds(caption.start)
        end = convert_time_to_seconds(caption.end)
        raw_captions.append({
            'start': start,
            'end': end,
            'raw': caption.raw_text,
        })

    # Remove captions created just for visual purposes.
    # These captions always have start at the same time of the previous
    # caption, and end at the same time of the next caption.
    # Also, these captions only ever last for 0.010 seconds (10 milliseconds).

    cleaned_captions = []
    for i, caption in enumerate(raw_captions):
        if caption['start'] == raw_captions[i - 1]['start'] and caption['end'] == raw_captions[i + 1]['end']:
            if caption['end'] - caption['start'] == 0.010:
                continue
        cleaned_captions.append(caption)

    captions = []
    for caption in cleaned_captions:
        # Within the raw text of a caption, we may have
        # words or phrases enclosed in a timestamp tag.
        # Example: "<00:00:04.680><c> some word</c>"
        # Where "some word" is the actual caption text,
        # and "00:00:04.680" is the timestamp at which
        # the caption should be displayed.

        # We want to remove these timestamp tags from the
        # raw text, and only keep the actual caption text.
        # A new caption entry will be created for each
        # timestamp tag found in the raw text.

        # We will also remove any leading or trailing
        # whitespaces from the caption text.

        matches = re.findall(r"<\d{2}:\d{2}:\d{2}\.\d{3}><c>.*?</c>", caption['raw'])

        if len(matches) == 0:
            # If no timestamp tags are found, we will
            # consider the entire caption as a single
            # entry.
            captions.append({
                'start': caption['start'],
                'end': caption['end'],
                'text': re.sub('<[^<]+?>', '', caption['raw']).strip(),
                "is_timestamp": False
            })
            continue
        else:
            # The text found at the beginning of the caption
            # before the first timestamp tag will be considered
            # as a separate entry.
            # The caption time will be the start time of the
            # caption, and the end time will be the start time
            # of the first timestamp tag.
            first_text, *rest_of_caption = caption['raw'].split('<')
            text = re.sub('<[^<]+?>', '', first_text).strip()
            first_match_time = matches[0].split('>')[0][1:]

            captions.append({
                'start': caption['start'],
                'end': convert_time_to_seconds(first_match_time),
                'text': text,
                "is_timestamp": False
            })

        last_match = None

        for i, match in enumerate(matches):
            # For the first match, the start time is the matched time,
            # and the end time is the start of the next caption.
            # For the last match, the start time is matched time,
            # and the end time is the end of the caption

            current_match_time = match.split('>')[0][1:]
            next_match_time = matches[i + 1].split('>')[0][1:] if i < len(matches) - 1 else None
            last_match_time = last_match.split('>')[0][1:] if last_match else None
            text = re.sub('<[^<]+?>', '', match).strip()

            if i == 0 and next_match_time:
                start = convert_time_to_seconds(current_match_time)
                end = convert_time_to_seconds(next_match_time)
            elif i == len(matches) - 1 and last_match_time:
                start = convert_time_to_seconds(last_match_time)
                end = caption['end']
            elif i == 0 and not next_match_time:
                start = convert_time_to_seconds(current_match_time)
                end = caption['end']
            else:
                start = convert_time_to_seconds(last_match_time)
                end = convert_time_to_seconds(current_match_time)

            last_match = match

            captions.append({
                'start': start,
                'end': end,
                'text': text,
                "is_timestamp": True
            })

    output = []
    
    for meta in metadata:
        file_info = meta['file'].split('_')
        start = meta['start']
        end = meta['end']
        filename = meta['file']
        speaker_type = file_info[0]
        speaker_id = file_info[1]
        file_id = file_info[2].split('.')[0]
        
        relevant_captions = []

        for caption in captions:
            if caption['start'] >= start and caption['start'] <= end:
                relevant_captions.append(caption['text'])

        print(relevant_captions)

        deduplicated_captions = []
        # remove any captions that are fully contained in another caption,
        # only if they are not "is_timestamp" captions
        for i, caption in enumerate(relevant_captions):
            if not captions[i]["is_timestamp"]:
                if any(caption in c for c in relevant_captions[:i] + relevant_captions[i+1:]):
                    continue
            # also replace newlines with spaces
            deduplicated_captions.append(caption.replace('\n', ' '))

        output.append({
            'filename': filename,
            'speaker_type': speaker_type,
            'speaker_id': speaker_id,
            'file_id': file_id,
            'start': start,
            'end': end,
            'captions': ' '.join(deduplicated_captions)
        })
    
    integrated_captions_path = os.path.join(output_dir, os.path.basename(captions_file).replace('.vtt', '.json'))
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
        # Save captions in VTT format
        get_captions(video_id, title, raw_captions_dir)
    
    for video_id, title in video_ids:
        # Integrate metadata into captions
        clean_title = title.replace("Title for ", "").replace(".mp4", "")
        if clean_title != "concatenated_audio_colombian_male":
            continue
        captions_file = os.path.join(raw_captions_dir, f"{clean_title}.vtt")
        metadata_file = os.path.join("../data", "interim", f"{clean_title.replace('concatenated_audio_', 'mapping_')}.json")
        parse_vtt(captions_file, metadata_file, intermediate_captions_dir)
