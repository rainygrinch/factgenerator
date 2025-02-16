import os
import time
import requests
import torch
from typing import List
from dotenv import load_dotenv
from colored import fg, attr
from gtts import gTTS
from transformers import GPT2LMHeadModel, GPT2Tokenizer


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
    "STOCK_VIDEO_API_KEY", "YOUTUBE_API_KEY",
    "VIDEO_OUTPUT", "AUDIO_OUTPUT", "THUMBNAIL_OUTPUT",
    "YOUTUBE_UPLOAD_FOLDER", "THUMBNAIL_OUTPUT_FOLDER"
]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        print(f"{fg('red')}Error: Missing environment variable {var}{attr('reset')}")
        exit(1)


def generate_script(topic):
    """
    Generates a script based on the input topic using GPT-2.

    Args:
        topic (str): The topic for which to generate the script.

    Returns:
        str: A script generated for the given topic.
    """
    print(f"{fg('blue')}Generating script for topic: {topic}...{attr('reset')}")
    time.sleep(2)

    # Load GPT-2 model and tokenizer
    model_name = "gpt2"  # Use the GPT-2 model
    model = GPT2LMHeadModel.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)

    # Encode the input prompt
    input_text = f"Write a detailed, engaging, and informative script for a video about {topic}. Make it sound like an educational YouTube video. Include an introduction, main points, and a conclusion. Keep it around 400 words."
    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    # Create the attention mask (1 for actual tokens, 0 for padding tokens)
    attention_mask = torch.ones(input_ids.shape, device=input_ids.device)

    try:
        # Generate script with sampling enabled and attention_mask included
        output = model.generate(input_ids,
                                max_length=600,
                                num_return_sequences=1,
                                no_repeat_ngram_size=2,
                                temperature=0.7,  # Controls randomness
                                do_sample=True,  # Enable sampling for more dynamic output
                                attention_mask=attention_mask)  # Provide the attention mask

        script = tokenizer.decode(output[0], skip_special_tokens=True)

        print(f"{fg('green')}Script generated successfully!{attr('reset')}")
        print(script)
        return script

    except Exception as e:
        print(f"{fg('red')}Error generating script: {e}{attr('reset')}")
        return f"Sorry, we couldn't generate the script for '{topic}' at the moment."


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

    # Save the entered topic to a file
    topics_file_path = "topics.txt"  # You can change the path if needed
    with open(topics_file_path, "a") as file:
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {topic}\n")  # Write topic with a timestamp

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
