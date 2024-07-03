import youtube_dl

def download_captions(video_url):
    ydl_opts = {
        'writesubtitles': True,
        'subtitleslangs': ['es'],  # Adjust the language as needed
        'skip_download': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        subtitles = info.get("subtitles", {})
        return subtitles.get("es")

if __name__ == "__main__":
    video_url = "your_youtube_video_url"
    captions = download_captions(video_url)
    print(captions)
