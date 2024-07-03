import json

def parse_captions(captions_file):
    with open(captions_file, 'r') as file:
        captions = json.load(file)
    return captions

def map_captions_to_original_files(captions, start_times):
    results = {}
    for caption in captions:
        start = caption['start']
        end = start + caption['duration']
        text = caption['text']

        for file, file_start, file_end in start_times:
            if start >= file_start and end <= file_end:
                if file not in results:
                    results[file] = []
                results[file].append({
                    'start': start - file_start,
                    'end': end - file_start,
                    'text': text
                })
                break
    return results

if __name__ == "__main__":
    captions_file = "path/to/downloaded/captions.json"
    captions = parse_captions(captions_file)
    mapped_captions = map_captions_to_original_files(captions, start_times)
    
    # Print mapped captions
    for file, captions in mapped_captions.items():
        print(f"Captions for {file}:")
        for caption in captions:
            print(f"  {caption['start']} - {caption['end']}: {caption['text']}")
