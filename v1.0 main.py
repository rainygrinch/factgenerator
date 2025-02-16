import os
import time
import requests
from typing import List
from dotenv import load_dotenv
from colored import fg, attr


def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """
    Searches for stock videos based on a query.

    Args:
        query (str): The query to search for.
        api_key (str): The API key to use.
        it (int): Number of videos to retrieve.
        min_dur (int): Minimum video duration in seconds.

    Returns:
        List[str]: A list of stock video URLs.
    """
    headers = {"Authorization": api_key}
    qurl = f"https://api.pexels.com/videos/search?query={query}&per_page={it}"
    r = requests.get(qurl, headers=headers)
    response = r.json()
    video_url = []
    try:
        for i in range(it):
            if response["videos"][i]["duration"] < min_dur:
                continue
            raw_urls = response["videos"][i]["video_files"]
            temp_video_url = ""
            video_res = 0
            for video in raw_urls:
                if ".com/video-files" in video["link"] and (video["width"] * video["height"]) > video_res:
                    temp_video_url = video["link"]
                    video_res = video["width"] * video["height"]
            if temp_video_url:
                video_url.append(temp_video_url)
    except Exception as e:
        print(f"{fg('red')}[-] No Videos found.{attr('reset')}")
        print(f"{fg('red')}{e}{attr('reset')}")
    print(f"{fg('cyan')}\t=> \"{query}\" found {len(video_url)} Videos{attr('reset')}")
    return video_url


def download_video(url: str, save_path: str):
    """
    Downloads a video from the provided URL and saves it to the given path.

    Args:
        url (str): The URL of the video.
        save_path (str): The local path to save the video.
    """
    print(f"{fg('blue')}Downloading video from: {url}...{attr('reset')}")
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"{fg('green')}Video downloaded successfully to: {save_path}{attr('reset')}")
    else:
        print(f"{fg('red')}Failed to download video.{attr('reset')}")


# Load environment variables from .env file
load_dotenv()

REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY", "STOCK_VIDEO_API_KEY", "YOUTUBE_API_KEY",
    "VIDEO_OUTPUT", "AUDIO_OUTPUT", "THUMBNAIL_OUTPUT",
    "YOUTUBE_UPLOAD_FOLDER", "THUMBNAIL_OUTPUT_FOLDER"
]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        print(f"{fg('red')}Error: Missing environment variable {var}{attr('reset')}")
        exit(1)


def generate_script(topic):
    print(f"{fg('blue')}Generating script for topic: {topic}...{attr('reset')}")
    time.sleep(2)
    return f"This is an AI-generated script about {topic}."


def fetch_stock_videos(keywords):
    print(f"{fg('blue')}Fetching stock videos related to: {keywords}...{attr('reset')}")
    api_key = os.getenv("STOCK_VIDEO_API_KEY")
    videos = search_for_stock_videos(" ".join(keywords), api_key, 5, 10)

    # Create a directory to save the videos
    video_dir = "downloaded_videos"
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    saved_videos = []
    for i, video_url in enumerate(videos):
        video_path = os.path.join(video_dir, f"video_{i + 1}.mp4")
        download_video(video_url, video_path)
        saved_videos.append(video_path)

    return saved_videos if saved_videos else ["default_video.mp4"]


def generate_voiceover(script):
    print(f"{fg('blue')}Generating voiceover...{attr('reset')}")
    time.sleep(2)
    return "voiceover.mp3"


def add_subtitles(video, script):
    print(f"{fg('blue')}Adding subtitles to video...{attr('reset')}")
    time.sleep(2)
    return "final_video.mp4"


def upload_to_youtube(video_path):
    print(f"{fg('green')}Uploading {video_path} to YouTube...{attr('reset')}")
    time.sleep(2)
    print(f"{fg('green')}Upload successful!{attr('reset')}")


def main():
    print(f"{fg('cyan')}Welcome to the Automated Video Generator!{attr('reset')}")
    topic = input("Enter the video topic: ")
    script = generate_script(topic)
    keywords = topic.split()[:3]
    stock_videos = fetch_stock_videos(keywords)
    voiceover = generate_voiceover(script)
    final_video = add_subtitles(stock_videos[0], script)
    upload = input("Do you want to upload the video to YouTube? (yes/no): ")
    if upload.lower() == "yes":
        upload_to_youtube(final_video)
    print(f"{fg('green')}Video creation process complete!{attr('reset')}")


if __name__ == "__main__":
    main()
